# NanoDeep

CNN + squeeze-and-excitation classifier for nanopore adaptive sampling
(Lin et al. 2024, *Briefings in Bioinformatics*, `bbad499`).

Upstream is [lysovosyl/NanoDeep](https://github.com/lysovosyl/NanoDeep); this
image builds [laura-raes/NanoDeep](https://github.com/laura-raes/NanoDeep),
a fork that adds what benchmarking needs without touching the method:

- `nanodeep_testmodel_nostats` — classify without a label directory, and write
  one `predictions_per_read.csv` row per read
- read-id/prediction alignment fix (the reads were being shuffled relative to
  their predictions)
- reads shorter than the model input no longer crash the loader
- CPU support (`-device cpu`) in the test *and* train entry points

## Entry points

```
docker run --rm ghcr.io/squidbase/nanodeep:latest nanodeep_trainmodel --help
docker run --rm ghcr.io/squidbase/nanodeep:latest nanodeep_testmodel_nostats --help
```

`nanodeep_testmodel` (with stats) and `nanodeep_adaptivesample` are also on PATH.

## Gotchas

- **`-model_name` is case-sensitive and the argparse default is wrong.** It is
  used verbatim as both `read_deep.model.<name>` and the `<name>` entry of
  `read_deep.model_config.defaultconfig`, both of which are `NanoDeep`. The
  default, `nanodeep`, cannot resolve. Always pass `-model_name NanoDeep`.
- **`--load_to_mem` changes preprocessing, not just speed.** The in-memory
  loader takes `signal[1000:signal_length+1000]`; the on-disk loader takes
  `signal[0:signal_length]` and trims no adapter. Training and classification
  must pass the same flag.
- **Class polarity comes from the training label filenames.** The label
  directory is sorted case-insensitively and that order becomes the class
  index, so the file that sorts first is class 0. Nothing in the model file
  records this — name the files so the order is explicit.
- **Inference is not deterministic.** `forward()` hardcodes
  `F.dropout(..., training=True)`, so `model.eval()` does not disable dropout
  and repeated runs on the same input give different logits. This is upstream
  behaviour and the published results were produced with it.
