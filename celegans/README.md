# C. elegans Hermaphrodite Connectome

Real connectome data from *Caenorhabditis elegans* (adult hermaphrodite).

## Source

WormWiring — Chen, Hall, and Chklovskii (2006), with reannotation from White et al. (1986).

- **Paper:** Varshney et al., "Structural properties of the *C. elegans* neuronal network," *PLoS Comput. Biol.* 7(2): e1001066, 2011.
- **Data:** [WormWiring](https://www.wormwiring.org/)
- **Original:** [WormAtlas Connectivity Download](https://wormatlas.org/MoW_built0.92/MoW.html)

## Stats

| Property | Value |
|----------|-------|
| Neurons | 283 |
| Synapses | 6,264 |
| File size | 61.8 KB |
| Chemical synapses | 5,233 rows |
| Electrical (gap) junctions | 1,031 rows |
| NMJ (excluded) | 153 rows |
| Bytes/synapse | 10.1 |

## Synapse Types

| Type | Description | Count |
|------|-------------|-------|
| S | Chemical (monadic) | 950 |
| Sp | Chemical (polyadic, presynaptic) | 1,625 |
| R | Chemical (receive, monadic) | 773 |
| Rp | Chemical (receive, polyadic) | 1,885 |
| EJ | Electrical junction (gap) | 1,031 |
| NMJ | Neuromuscular junction (excluded) | 153 |

## Format

Edge list format with `u32` source/destination indices and `f16` weights.
Neuron names are mapped to indices alphabetically.
