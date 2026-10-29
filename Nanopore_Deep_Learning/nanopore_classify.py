#!/usr/bin/env python3
"""Classify fast5 reads with a trained Nanopore_Deep_Learning model.

Upstream ships no offline inference entry point. It has nanopore_training.py,
which trains and validates in one process, and a Read Until `simple.py` that
lives in a fork of nanoporetech/read_until_api and needs the proprietary
MinKNOW API to run at all. This script is the missing third piece: load a
model, preprocess reads exactly the way training did, write one class per read.

Training never sees a read from its first sample: upstream's get_signal.py,
which writes the training CSVs, starts every read at Signalstart() and drops
the reads where it finds no start. So this script does the same, and then
follows the one published offline inference for this model, Fan et al. 2024's
inference.py (github.com/fankc/Nanopore_Deep_Learning): a read with no start,
or with fewer than 2100 differences after it, is skipped.

Output is read_id,predicted_class with the raw argmax index, the same shape as
NanoDeep's predictions_per_read.csv. --target trained class 1, so 1 is target
and 0 is background (see nanopore_training.py's loadReads comment).
"""

import argparse
import csv
import os
import sys

import numpy as np
import torch
from ont_fast5_api.fast5_interface import get_fast5_file

# Upstream's own function, imported rather than copied so it cannot drift from the
# one that cut the training CSVs. Importing get_signal.py runs nothing but imports.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Preparing_fast5_for_analysis"))
from get_signal import Signalstart  # noqa: E402

# Not stored on the model, so it has to be rederived the way nanopore_training.py
# derives it - from the window length encoded in the model directory's name.
STRIDE_FOR_WINDOW = {1: 1, 32: 10}

# Fan et al.'s inference.py skips a read with fewer than --length differences after
# its start (2100, its default and their published value). Both window configurations
# read fewer than that: (200-1)*10+32 = 2022 for 32, (2000-1)*1+1 = 2000 for 1.
MIN_DIFFS = 2100


def preprocess(signal, seq_length, stride, win_length):
    """The training transform (nanopore_dataloader.py), minus its two augmentations.

    signal starts at the read's Signalstart, like a get_signal.py training row.
    Training composes startMove -> differences -> cutToWindows -> noise on that row.
    startMove slices row[r:-1000+r] for a random r in [0, 999]; r=0 is the
    deterministic member of that family, and cutToWindows then reads only the
    first (seq_length-1)*stride + win_length differences, so the model sees
    samples [0, that+1) of signal. noise is augmentation and is dropped here.
    """
    diffs = np.diff(signal)
    windows = np.zeros((seq_length, win_length), dtype="int16")
    for i in range(seq_length):
        windows[i, :] = diffs[i * stride : i * stride + win_length]
    return windows


def iter_reads(signal_dir):
    """Yield (read_id, raw signal) for every read under signal_dir, recursively."""
    for root, _, files in sorted(os.walk(signal_dir)):
        for name in sorted(files):
            if not name.lower().endswith(".fast5"):
                continue
            with get_fast5_file(os.path.join(root, name), mode="r") as f5:
                for read_id in f5.get_read_ids():
                    yield read_id, f5.get_read(read_id).get_raw_data()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Model .pth written by nanopore_training.py")
    parser.add_argument("--signal-dir", required=True, help="Directory of fast5 files, searched recursively")
    parser.add_argument("--out", required=True, help="Output CSV: read_id,predicted_class")
    parser.add_argument("--batch-size", default=32, type=int)
    parser.add_argument("--gpu", default=False, action="store_true")
    args = parser.parse_args()

    device = "cuda" if args.gpu else "cpu"
    # weights_only=False: these .pth files hold a pickled nn.Module, not a state
    # dict, so torch >= 2.6's default refuses to load them. nanopore_models must
    # be importable for the unpickle to resolve the class.
    model = torch.load(args.model, map_location=device, weights_only=False)
    model.to(device)
    model.eval()

    win_length = model.input_size
    seq_length = model.max_length
    if win_length not in STRIDE_FOR_WINDOW:
        sys.exit(f"ERROR: model window length {win_length} is neither 1 nor 32, so its stride is unknown")
    stride = STRIDE_FOR_WINDOW[win_length]

    print(f"model: {type(model).__name__}, {seq_length} steps of {win_length} samples, stride {stride}")
    print(f"skipping reads with no Signalstart or fewer than {MIN_DIFFS} differences after it")

    written = 0
    no_start = 0
    too_short = 0
    with open(args.out, "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["read_id", "predicted_class"])

        batch_ids, batch_signals = [], []

        def flush():
            nonlocal written
            if not batch_ids:
                return
            x = torch.tensor(np.stack(batch_signals), dtype=torch.float32, device=device)
            with torch.no_grad():
                predictions = model(input_=x).argmax(1).tolist()
            writer.writerows(zip(batch_ids, predictions))
            written += len(batch_ids)
            batch_ids.clear()
            batch_signals.clear()

        for read_id, signal in iter_reads(args.signal_dir):
            # Checked first because Signalstart raises on a read of 10 samples or fewer;
            # any read this short fails the check after it anyway.
            if len(signal) <= MIN_DIFFS:
                too_short += 1
                continue
            start = Signalstart(signal)
            if start == 0:  # upstream's "no valid start point"
                no_start += 1
                continue
            if len(signal) - start - 1 < MIN_DIFFS:
                too_short += 1
                continue
            batch_ids.append(read_id)
            batch_signals.append(preprocess(signal[start:], seq_length, stride, win_length))
            if len(batch_ids) == args.batch_size:
                flush()
        flush()

    print(f"classified {written} reads, skipped {no_start} with no Signalstart and {too_short} too short -> {args.out}")
    if written == 0:
        sys.exit(f"ERROR: no read under {args.signal_dir} could be classified")


if __name__ == "__main__":
    main()
