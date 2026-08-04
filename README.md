# arc-datasets

Reference datasets in [ARC](https://github.com/sectersion/neurarc) format for benchmarking and testing.

## Datasets

### Biological Connectomes

| File | Neurons | Synapses | Size | Description |
|------|---------|----------|------|-------------|
| `celegans/celegans_hermaphrodite.arc` | 302 | 8,152 | 80.5 KB | C. elegans hermaphrodite nervous system |

### Synthetic Benchmarks

| File | Neurons | Synapses | Size | Description |
|------|---------|----------|------|-------------|
| `synthetic/small.arc` | 1,000 | 10,000 | 98 KB | Small random network |
| `synthetic/medium.arc` | 10,000 | 100,000 | 977 KB | Medium random network |
| `synthetic/large.arc` | 100,000 | 1,000,000 | 9.5 MB | Large random network |
| `synthetic/xlarge.arc` | 1,000,000 | 10,000,000 | 95.4 MB | Extra-large random network |

## Usage

```bash
# with neurarc-py
pip install neurarc

neurarc info celegans/celegans_hermaphrodite.arc
neurarc validate celegans/celegans_hermaphrodite.arc

# with neurarc-rs
cargo add neurarc --features cli

arc info celegans/celegans_hermaphrodite.arc
```

## Regenerating

```bash
pip install numpy
python generate.py
```

## Verification

```bash
python verify.py
```

All `.arc` files are verified in CI on every push that modifies them.
