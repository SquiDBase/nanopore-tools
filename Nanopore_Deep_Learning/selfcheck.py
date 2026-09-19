#!/usr/bin/env python3
"""Build-time check that classification still preprocesses the way training does.

nanopore_classify.py reimplements nanopore_dataloader.py's transform chain
(there is no shared entry point to call), so the two can drift apart silently -
a model would still load and still emit a class per read, just a meaningless
one. This pins the window nanopore_classify.preprocess cuts against the one
cutToWindows_transform cuts from the same signal, and checks a model survives
a save/load/forward round trip on CPU.
"""

import numpy as np
import torch

from nanopore_classify import STARTMOVE_TRIM, STRIDE_FOR_WINDOW, preprocess
from nanopore_dataloader import cutToWindows_transform, differences_transform
from nanopore_models import bnLSTM_32window

SEQ_LENGTH, WIN_LENGTH = 200, 32
STRIDE = STRIDE_FOR_WINDOW[WIN_LENGTH]

signal = np.arange(5000, dtype="int16")
windows = preprocess(signal, SEQ_LENGTH, STRIDE, WIN_LENGTH)
assert windows.shape == (SEQ_LENGTH, WIN_LENGTH), windows.shape

# The training chain at startMove's offset 0, which is what preprocess pins.
expected = cutToWindows_transform(
    differences_transform(signal[: len(signal) - STARTMOVE_TRIM]), SEQ_LENGTH, STRIDE, WIN_LENGTH
)
assert np.array_equal(windows, expected), "preprocess no longer matches cutToWindows_transform"

# The last sample preprocess reads decides min_samples in nanopore_classify.main.
assert STARTMOVE_TRIM + 1 + (SEQ_LENGTH - 1) * STRIDE + WIN_LENGTH == 3023

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
