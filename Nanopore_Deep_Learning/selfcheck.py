#!/usr/bin/env python3
"""Build-time check that classification still preprocesses the way training does.

nanopore_classify.py reimplements nanopore_dataloader.py's transform chain
(there is no shared entry point to call), so the two can drift apart silently -
a model would still load and still emit a class per read, just a meaningless
one. This pins the window nanopore_classify.preprocess cuts against the one
cutToWindows_transform cuts from get_signal.py's training row of the same read,
and checks a model survives a save/load/forward round trip on CPU.
"""

import numpy as np
import torch

from nanopore_classify import MIN_DIFFS, STRIDE_FOR_WINDOW, Signalstart, preprocess
from nanopore_dataloader import cutToWindows_transform, differences_transform
from nanopore_models import bnLSTM_32window

SEQ_LENGTH, WIN_LENGTH = 200, 32
STRIDE = STRIDE_FOR_WINDOW[WIN_LENGTH]

# A read Signalstart can place: a flat stretch, the spike it looks for at 1000, then
# strand-like noise, so the variance after the spike beats the variance before it.
signal = np.full(8000, 400, dtype="int16")
signal[1000] = 1000
signal[1001:] += np.random.default_rng(0).integers(-50, 50, size=len(signal) - 1001, dtype="int16")
start = Signalstart(signal)
assert start == 1000, start

windows = preprocess(signal[start:], SEQ_LENGTH, STRIDE, WIN_LENGTH)
assert windows.shape == (SEQ_LENGTH, WIN_LENGTH), windows.shape

# get_signal.py's training row is signal[start:start+5000]; the training chain on it at
# startMove's offset 0, which is what preprocess pins.
row = signal[start : start + 5000]
expected = cutToWindows_transform(differences_transform(row[: len(row) - 1000]), SEQ_LENGTH, STRIDE, WIN_LENGTH)
assert np.array_equal(windows, expected), "preprocess no longer matches cutToWindows_transform"

# Neither window configuration may read past the MIN_DIFFS differences main() guarantees.
assert MIN_DIFFS >= (200 - 1) * 10 + 32 and MIN_DIFFS >= (2000 - 1) * 1 + 1

model = bnLSTM_32window(
    input_size=WIN_LENGTH, hidden_size=8, max_length=SEQ_LENGTH, num_layers=1,
    use_bias=True, batch_first=True, dropout=0.5, num_classes=2,
)
torch.save(model, "/tmp/selfcheck_model.pth")
# Exactly how nanopore_classify loads it: pickled nn.Module, not a state dict.
reloaded = torch.load("/tmp/selfcheck_model.pth", map_location="cpu", weights_only=False)
reloaded.eval()
with torch.no_grad():
    logits = reloaded(input_=torch.tensor(np.stack([windows, windows]), dtype=torch.float32))
assert logits.shape == (2, 2), logits.shape

print("selfcheck OK")
