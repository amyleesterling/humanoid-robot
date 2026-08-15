#!/usr/bin/env python3
"""Lossless raw-mesh shard helpers for large HR-V0 evidence packages."""
from __future__ import annotations
from pathlib import Path
import numpy as np

LINEAR_KEYS = (
    "linear_node_tags", "linear_node_xyz", "linear_element_tags",
    "linear_tet4_connectivity", "linear_sicn", "element_zone_code",
)
TET10_KEYS = ("node_tags", "node_xyz", "tet10_element_tags", "tet10_connectivity")


def split_raw(source: Path, linear_path: Path, tet10_path: Path) -> None:
    with np.load(source) as data:
        if set(data.files) != set(LINEAR_KEYS + TET10_KEYS):
            raise RuntimeError(f"unexpected raw mesh array set: {data.files}")
        np.savez_compressed(linear_path, **{key: data[key] for key in LINEAR_KEYS})
        np.savez_compressed(tet10_path, **{key: data[key] for key in TET10_KEYS})


def load_shards(package: Path) -> dict[str, np.ndarray]:
    result: dict[str, np.ndarray] = {}
    for name, expected in (("raw-linear-mesh.npz", LINEAR_KEYS), ("raw-tet10-mesh.npz", TET10_KEYS)):
        with np.load(package / name) as data:
            if tuple(data.files) != expected:
                raise RuntimeError(f"{name} array order/set drift: {data.files}")
            for key in expected:
                result[key] = data[key]
    return result
