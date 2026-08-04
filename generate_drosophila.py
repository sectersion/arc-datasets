"""Generate a Drosophila hemibrain-like synthetic dataset.

Based on published statistics from the hemibrain connectome:
- ~25,000 neurons
- ~20,000,000 synapses
- Multiple neuron types and populations

This is a synthetic approximation for benchmarking.
Real data can be obtained from neuPrint: https://neuprint.janelia.org/
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "neurarc-py"))
from neurarc import ArcFile, save

np.random.seed(42)

NEURONS = 25_000
SYNAPSES = 9_000_000

print(f"Generating Drosophila hemibrain-like dataset: {NEURONS:,} neurons, {SYNAPSES:,} synapses")

src = np.random.randint(0, NEURONS, size=SYNAPSES, dtype=np.uint32)
dst = np.random.randint(0, NEURONS, size=SYNAPSES, dtype=np.uint32)
weight = np.random.uniform(0.5, 10.0, size=SYNAPSES).astype(np.float16)

header = {
    "format_version": 1,
    "neuron_count": NEURONS,
    "neuron_model": "LIF",
    "synapse_count": SYNAPSES,
    "connectivity_format": "edge_list",
    "populations": {
        "Kenyon_cells": {"n_neurons": 2000, "global_offset": 0},
        "mushroom_body": {"n_neurons": 3000, "global_offset": 2000},
        "antennal_lobe": {"n_neurons": 2500, "global_offset": 5000},
        "optic_lobe": {"n_neurons": 8000, "global_offset": 7500},
        "motor": {"n_neurons": 2000, "global_offset": 15500},
        "interneurons": {"n_neurons": 9500, "global_offset": 17500},
    },
    "projections": {
        "antennal_to_KC": {"source": "antennal_lobe", "target": "Kenyon_cells"},
        "KC_to_MB": {"source": "Kenyon_cells", "target": "mushroom_body"},
        "optic_to_inter": {"source": "optic_lobe", "target": "interneurons"},
        "inter_to_motor": {"source": "interneurons", "target": "motor"},
    },
    "tensors": {
        "synapse_src": {"offset": 0, "length": SYNAPSES, "dtype": "u32"},
        "synapse_dst": {"offset": SYNAPSES * 4, "length": SYNAPSES, "dtype": "u32"},
        "synapse_weight": {"offset": SYNAPSES * 8, "length": SYNAPSES, "dtype": "f16"},
    },
}

arc = ArcFile(
    header=header,
    tensors={"synapse_src": src, "synapse_dst": dst, "synapse_weight": weight},
)

outpath = r"C:\Users\Oliver\arc-datasets\drosophila\drosophila_hemibrain.arc"
os.makedirs(os.path.dirname(outpath), exist_ok=True)
save(outpath, arc)

size = os.path.getsize(outpath)
print(f"Saved: {outpath}")
print(f"Size: {size:,} bytes ({size / 1e6:.1f} MB)")
print(f"Bytes/synapse: {size / SYNAPSES:.1f}")
