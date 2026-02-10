"""MNIST data cleaning script.

Downloads MNIST dataset, normalizes pixel values, and writes to Lance format.
Implements the run(input_path, output_path, params) interface.
"""

import struct
from pathlib import Path

import daft
import numpy as np
import pyarrow as pa


def run(input_path: str, output_path: str, params: dict) -> dict:
    """
    Args:
        input_path: path to directory containing MNIST IDX files, or "download" to auto-download
        output_path: Lance output path
        params: {"normalize": bool, "test_ratio": float}
    Returns:
        stats dict
    """
    input_dir = Path(input_path)

    if input_path == "download" or not input_dir.exists():
        input_dir = _download_mnist(input_dir)

    # Read IDX files
    train_images = _read_idx_images(input_dir / "train-images-idx3-ubyte")
    train_labels = _read_idx_labels(input_dir / "train-labels-idx1-ubyte")
    test_images = _read_idx_images(input_dir / "t10k-images-idx3-ubyte")
    test_labels = _read_idx_labels(input_dir / "t10k-labels-idx1-ubyte")

    # Flatten 28x28 -> 784
    train_images = train_images.reshape(-1, 784)
    test_images = test_images.reshape(-1, 784)

    # Normalize
    if params.get("normalize", True):
        train_images = train_images.astype(np.float32) / 255.0
        test_images = test_images.astype(np.float32) / 255.0

    # Build Arrow table
    n_train = len(train_labels)
    n_test = len(test_labels)
    all_images = np.concatenate([train_images, test_images], axis=0)
    all_labels = np.concatenate([train_labels, test_labels], axis=0)
    all_splits = ["train"] * n_train + ["test"] * n_test

    table = pa.table({
        "image": [row.tolist() for row in all_images],
        "label": all_labels.tolist(),
        "split": all_splits,
    })

    df = daft.from_arrow(table)
    df.write_lance(output_path, mode="overwrite")

    return {
        "total_records": n_train + n_test,
        "train_records": n_train,
        "test_records": n_test,
    }


def _read_idx_images(path: Path) -> np.ndarray:
    with open(path, "rb") as f:
        magic, num, rows, cols = struct.unpack(">IIII", f.read(16))
        assert magic == 2051
        return np.frombuffer(f.read(), dtype=np.uint8).reshape(num, rows, cols)


def _read_idx_labels(path: Path) -> np.ndarray:
    with open(path, "rb") as f:
        magic, num = struct.unpack(">II", f.read(8))
        assert magic == 2049
        return np.frombuffer(f.read(), dtype=np.uint8)


def _download_mnist(target_dir: Path) -> Path:
    """Download MNIST dataset from the web."""
    import gzip
    import urllib.request

    base_url = "https://storage.googleapis.com/cvdf-datasets/mnist/"
    files = [
        "train-images-idx3-ubyte.gz",
        "train-labels-idx1-ubyte.gz",
        "t10k-images-idx3-ubyte.gz",
        "t10k-labels-idx1-ubyte.gz",
    ]

    target_dir.mkdir(parents=True, exist_ok=True)
    for fname in files:
        gz_path = target_dir / fname
        out_path = target_dir / fname.replace(".gz", "")
        if out_path.exists():
            continue
        print(f"Downloading {fname}...")
        urllib.request.urlretrieve(base_url + fname, gz_path)
        with gzip.open(gz_path, "rb") as f_in, open(out_path, "wb") as f_out:
            f_out.write(f_in.read())
        gz_path.unlink()

    return target_dir
