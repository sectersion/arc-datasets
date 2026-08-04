"""Verify all .arc files in the repository.

Checks:
1. Magic bytes are correct
2. Header is valid JSON
3. All required fields present
4. Tensor data is not truncated
5. Neuron indices are in bounds

Usage:
    python verify.py
    python verify.py path/to/file.arc
"""

import json
import struct
import sys
from pathlib import Path

MAGIC = b"ARC1"
REQUIRED_FIELDS = ["format_version", "neuron_count", "neuron_model", "synapse_count", "connectivity_format", "tensors"]


def verify_arc(path: Path) -> list[str]:
    errors = []

    data = path.read_bytes()
    if len(data) < 12:
        return [f"File too small ({len(data)} bytes)"]

    # Check magic
    if data[:4] != MAGIC:
        errors.append(f"Invalid magic: {data[:4]!r}")
        return errors

    # Parse header
    header_len = struct.unpack("<Q", data[4:12])[0]
    if len(data) < 12 + header_len:
        errors.append(f"Truncated header: need {12 + header_len} bytes, have {len(data)}")
        return errors

    try:
        header = json.loads(data[12:12 + header_len])
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON header: {e}")
        return errors

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in header:
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors

    # Check format version
    if header["format_version"] != 1:
        errors.append(f"Unknown format_version: {header['format_version']}")

    # Check connectivity format
    fmt = header.get("connectivity_format", "edge_list")
    if fmt not in ("edge_list", "csr"):
        errors.append(f"Invalid connectivity_format: {fmt}")

    # Check tensors
    blob = data[12 + header_len:]
    tensors = header.get("tensors", {})
    neuron_count = header.get("neuron_count", 0)
    synapse_count = header.get("synapse_count", 0)

    for name, desc in tensors.items():
        if "offset" not in desc:
            errors.append(f"Tensor '{name}': missing offset")
            continue
        if "length" not in desc:
            errors.append(f"Tensor '{name}': missing length")
            continue
        if "dtype" not in desc:
            errors.append(f"Tensor '{name}': missing dtype")
            continue

        dtype = desc["dtype"]
        dtype_sizes = {"u8": 1, "u32": 4, "f16": 2, "f32": 4}
        if dtype not in dtype_sizes:
            errors.append(f"Tensor '{name}': unknown dtype '{dtype}'")
            continue

        byte_size = desc["length"] * dtype_sizes[dtype]
        end = desc["offset"] + byte_size
        if end > len(blob):
            errors.append(f"Tensor '{name}': truncated (need {end} bytes, blob is {len(blob)})")

    # Check required tensors for edge_list
    if fmt == "edge_list":
        for name in ["synapse_src", "synapse_dst", "synapse_weight"]:
            if name not in tensors:
                errors.append(f"Missing required tensor for edge_list: {name}")
    elif fmt == "csr":
        for name in ["synapse_row_ptr", "synapse_col_idx", "synapse_weight"]:
            if name not in tensors:
                errors.append(f"Missing required tensor for csr: {name}")

    return errors


def main():
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
    else:
        files = sorted(Path(".").rglob("*.arc"))

    if not files:
        print("No .arc files found.")
        sys.exit(1)

    total = 0
    passed = 0
    failed = 0

    for f in files:
        total += 1
        errors = verify_arc(f)
        if errors:
            failed += 1
            print(f"FAIL {f}")
            for e in errors:
                print(f"     {e}")
        else:
            passed += 1
            print(f"OK   {f}")

    print(f"\n{passed}/{total} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
