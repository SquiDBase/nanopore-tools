# Nanopore_Deep_Learning

Batch-normalised LSTM classifier over raw nanopore signal, for real-time
selective sequencing (Noam-Shomron lab, *"Real-time selective sequencing using
nanopores and deep learning"*).

Upstream is [nshomron/Nanopore_Deep_Learning](https://github.com/nshomron/Nanopore_Deep_Learning).
CPU only, and it does both halves: `nanopore_training.py` trains,
`nanopore_classify.py` classifies.

## Entry points

```
docker run --rm ghcr.io/squidbase/nanoporedeeplearning:latest nanopore_training.py --help
docker run --rm ghcr.io/squidbase/nanoporedeeplearning:latest nanopore_classify.py --help
```

Smoke test, on the example Hek data the repository ships (one epoch, a couple
of minutes):

```
docker run --rm ghcr.io/squidbase/nanoporedeeplearning:latest \
  nanopore_training.py --hidden-size 512 --batch-size 32 --max-iter 1 \
    --train-target      /app/Nanopore_Deep_Learning/Data/Hek1_example_data/FAF13387-Hek_run1.minimap2.Mito5KbTrain.csv \
    --train-background  /app/Nanopore_Deep_Learning/Data/Hek1_example_data/FAF13387-Hek_run1.minimap2.not-Mito5KbTrain.csv \
    --valid-target      /app/Nanopore_Deep_Learning/Data/Hek1_example_data/FAF13387-Hek_run1.minimap2.Mito5KbTest.csv \
    --valid-background  /app/Nanopore_Deep_Learning/Data/Hek1_example_data/FAF13387-Hek_run1.minimap2.not-Mito5KbTest.csv \
    --out-dir /tmp/run
```

## What is patched, and why

`cpu_and_cli.patch`, applied to upstream at `db57ad6`:

- **`__getitem__` indexes instead of popping.** `NanoporeDataset.__getitem__`
  ignored its `index` and did `load_order.pop(0)`, so `__len__` shrank while
  the sampler iterated. Torch 1.8's `RandomSampler` read the length once and
  got away with it; every torch since re-reads `num_samples` after the first
  pass and over-yields, so the fetch for the last partial batch raised
  `IndexError: pop from empty list` at the end of epoch 1. The training script
  catches `StopIteration` to start a new epoch, not `IndexError`, so upstream
  could not complete a single epoch on a current torch.
- **`np.Inf` -> `np.inf`**, removed in numpy 2.
- **The four input CSVs, the output directory and the model configuration are
  arguments.** Upstream scanned a fixed directory for four fixed filenames and
  derived its hyperparameters from the *names of the subdirectories* of
  `Models/`, which it otherwise ignored. `--model-name`/`--window-length`
  replace that scan; the name still carries `_winlen<N>` because that is what
  the hyperparameter parsing reads.
- **The 10000-read cap is `--max-reads`, default unlimited.** It used to
  silently truncate any larger training set.
- **`nn.CrossEntropyLoss().cuda()` is conditional on `--gpu`.** It happens to
  be a no-op today, because the loss holds no tensors, which is not a property
  to depend on.
- **A model is always saved.** Upstream only wrote one from inside the
  validation block at batch 200, 300, ..., so a shorter run produced nothing.

## Gotchas

- **Class polarity: `--target` is class 1.** The script calls class 0 "Chrom"
  and class 1 "Mito", after the mitochondrial-enrichment task of the paper, and
  `--train-target`/`--valid-target` feed Mito. Nothing in the `.pth` records
  this. Note this is the *opposite* of NanoDeep, where class 0 is the target.
- **Input is one read per CSV row**, raw int16 signal samples, every row the
  same width. Rows must be at least `1000 + 1 + (steps-1)*stride + window`
  samples wide — 3023 for the default 32-sample window — or the read is
  windowed out of zeros. `nanopore_classify.py` skips reads below that floor
  and says how many.
- **Training augments, classification does not.** The training transform is
  `startMove -> differences -> cutToWindows -> noise`, where `startMove` jitters
  the read start by a random 0-999 samples and `noise` adds N(0,5).
  `nanopore_classify.py` pins the offset at 0 and drops the noise, so it reads
  samples `[0, 3023)` of each read. `selfcheck.py` runs at build time and fails
  the build if the two chains stop agreeing.
- **Model files are pickled `nn.Module` objects, not state dicts,** so loading
  needs `weights_only=False` on torch >= 2.6 and `nanopore_models` on the path.
  Both are already true inside this image.
- **`--max-iter` counts epochs of the target class,** not batches or steps.
