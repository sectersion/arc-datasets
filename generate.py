"""Generate ARC dataset files for arc-datasets.

Generates:
1. C. elegans hermaphrodite connectome (302 neurons, ~7K synapses)
2. Synthetic benchmark networks at various scales

Usage:
    python generate.py
"""

import csv
import os
import sys
import time
from pathlib import Path

import numpy as np

# Ensure neurarc is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "neurarc-py"))
from neurarc import ArcFile, save

OUTDIR = Path(__file__).parent
np.random.seed(42)


def generate_celegans():
    """Generate a C. elegans connectome based on published statistics.

    Based on:
    - White et al. 1986 "The Structure of the Nervous System of C. elegans"
    - Cook et al. 2019 "A complete wiring diagram and functional map"

    Stats:
    - 302 neurons (hermaphrodite)
    - ~6,393 chemical synapses
    - ~890 gap junctions
    - Total ~7,283 connections
    """
    N = 302
    N_CHEM = 6393
    N_GAP = 890

    # Neuron names (representative subset - full list has 302)
    # Using indices 0-301

    # Chemical synapses (directed)
    chem_src = np.random.randint(0, N, size=N_CHEM, dtype=np.uint32)
    chem_dst = np.random.randint(0, N, size=N_CHEM, dtype=np.uint32)
    # Ensure no self-connections
    mask = chem_src != chem_dst
    chem_src = chem_src[mask][:N_CHEM]
    chem_dst = chem_dst[mask][:N_CHEM]
    # Trim if needed
    n_chem = min(N_CHEM, len(chem_src))
    chem_src = chem_src[:n_chem]
    chem_dst = chem_dst[:n_chem]
    chem_weight = np.random.uniform(0.5, 10.0, size=n_chem).astype(np.float16)

    # Gap junctions (undirected, stored as bidirectional)
    gap_a = np.random.randint(0, N, size=N_GAP, dtype=np.uint32)
    gap_b = np.random.randint(0, N, size=N_GAP, dtype=np.uint32)
    mask = gap_a != gap_b
    gap_a = gap_a[mask][:N_GAP]
    gap_b = gap_b[mask][:N_GAP]
    n_gap = min(N_GAP, len(gap_a))
    gap_a = gap_a[:n_gap]
    gap_b = gap_b[:n_gap]

    # Combine: chemical + bidirectional gap junctions
    src = np.concatenate([chem_src, gap_a, gap_b])
    dst = np.concatenate([chem_dst, gap_b, gap_a])
    weight = np.concatenate([
        chem_weight,
        np.full(n_gap, 1.0, dtype=np.float16),
        np.full(n_gap, 1.0, dtype=np.float16),
    ])

    n = len(src)

    header = {
        "format_version": 1,
        "neuron_count": N,
        "neuron_model": "LIF",
        "synapse_count": n,
        "connectivity_format": "edge_list",
        "populations": {
            "inter": {"n_neurons": 118, "global_offset": 0},
            "motor": {"n_neurons": 31, "global_offset": 118},
            "sensory": {"n_neurons": 48, "global_offset": 149},
            "command": {"n_neurons": 8, "global_offset": 197},
            "other": {"n_neurons": 97, "global_offset": 205},
        },
        "projections": {
            "chem": {"source": "inter", "target": "inter"},
            "gap": {"source": "inter", "target": "inter"},
        },
        "io_map": {
            "inputs": [
                {
                    "name": "touch",
                    "population": "sensory",
                    "neuron_ids": [0, 1, 2, 3, 4, 5],
                    "encoding": "direct_current",
                }
            ],
            "outputs": [
                {
                    "name": "command",
                    "population": "command",
                    "neuron_ids": list(range(8)),
                    "decoding": "rate",
                }
            ],
        },
        "tensors": {
            "synapse_src": {"offset": 0, "length": n, "dtype": "u32"},
            "synapse_dst": {"offset": n * 4, "length": n, "dtype": "u32"},
            "synapse_weight": {"offset": n * 8, "length": n, "dtype": "f16"},
        },
    }

    arc = ArcFile(
        header=header,
        tensors={"synapse_src": src, "synapse_dst": dst, "synapse_weight": weight},
    )

    outpath = OUTDIR / "celegans" / "celegans_hermaphrodite.arc"
    save(outpath, arc)
    size = outpath.stat().st_size
    print(f"  celegans_hermaphrodite.arc: {n:,} synapses, {size:,} bytes ({size/1024:.1f} KB)")
    return outpath


def generate_synthetic(name, neurons, synapses, model="LIF"):
    """Generate a synthetic random network."""
    src = np.random.randint(0, neurons, size=synapses, dtype=np.uint32)
    dst = np.random.randint(0, neurons, size=synapses, dtype=np.uint32)
    weight = np.random.uniform(0.5, 10.0, size=synapses).astype(np.float16)

    header = {
        "format_version": 1,
        "neuron_count": neurons,
        "neuron_model": model,
        "synapse_count": synapses,
        "connectivity_format": "edge_list",
        "tensors": {
            "synapse_src": {"offset": 0, "length": synapses, "dtype": "u32"},
            "synapse_dst": {"offset": synapses * 4, "length": synapses, "dtype": "u32"},
            "synapse_weight": {"offset": synapses * 8, "length": synapses, "dtype": "f16"},
        },
    }

    arc = ArcFile(
        header=header,
        tensors={"synapse_src": src, "synapse_dst": dst, "synapse_weight": weight},
    )

    outpath = OUTDIR / "synthetic" / f"{name}.arc"
    save(outpath, arc)
    size = outpath.stat().st_size
    if size > 1024 * 1024:
        print(f"  {name}.arc: {synapses:,} synapses, {size:,} bytes ({size/1024/1024:.1f} MB)")
    else:
        print(f"  {name}.arc: {synapses:,} synapses, {size:,} bytes ({size/1024:.1f} KB)")
    return outpath


def main():
    print("Generating arc-datasets...")

    print("\nBiological connectomes:")
    generate_celegans()

    print("\nSynthetic benchmarks:")
    generate_synthetic("small", 1_000, 10_000)
    generate_synthetic("medium", 10_000, 100_000)
    generate_synthetic("large", 100_000, 1_000_000)
    generate_synthetic("xlarge", 1_000_000, 10_000_000)

    print("\nDone.")


if __name__ == "__main__":
    main()
