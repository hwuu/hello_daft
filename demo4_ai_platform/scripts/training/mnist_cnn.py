"""MNIST CNN training script.

Trains a simple CNN on MNIST data from Lance, saves model weights to Lance.
Implements the run(input_path, output_path, params) interface.
"""

import io
import json
from datetime import datetime, timezone

import daft
import lancedb
import numpy as np
import pyarrow as pa
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset


class MnistCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.fc = nn.Sequential(
            nn.Linear(32 * 7 * 7, 128),
            nn.ReLU(),
            nn.Linear(128, 10),
        )

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


def run(input_path: str, output_path: str, params: dict) -> dict:
    """
    Args:
        input_path: Lance dataset path (with image, label, split columns)
        output_path: Lance model output path
        params: {"epochs": int, "learning_rate": float, "batch_size": int, "device": str}
    Returns:
        metrics dict
    """
    epochs = params.get("epochs", 10)
    lr = params.get("learning_rate", 0.001)
    batch_size = params.get("batch_size", 64)
    device = torch.device(params.get("device", "cpu"))

    # Load data from Lance
    df = daft.read_lance(input_path)
    pdf = df.to_pandas()

    train_pdf = pdf[pdf["split"] == "train"]
    test_pdf = pdf[pdf["split"] == "test"]

    train_loader = _make_loader(train_pdf, batch_size, shuffle=True)
    test_loader = _make_loader(test_pdf, batch_size, shuffle=False)

    # Train
    model = MnistCNN().to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            output = criterion(model(images), labels)
            output.backward()
            optimizer.step()
            total_loss += output.item()

    # Evaluate
    model.eval()
    correct = 0
    total = 0
    test_loss = 0.0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            test_loss += criterion(outputs, labels).item()
            correct += (outputs.argmax(1) == labels).sum().item()
            total += labels.size(0)

    accuracy = correct / total
    avg_test_loss = test_loss / len(test_loader)

    # Save model to Lance
    _save_model(model, output_path, params, {"accuracy": accuracy, "test_loss": avg_test_loss})

    return {"accuracy": accuracy, "test_loss": avg_test_loss}


def _make_loader(pdf, batch_size: int, shuffle: bool) -> DataLoader:
    images = np.array(pdf["image"].tolist(), dtype=np.float32)
    images = images.reshape(-1, 1, 28, 28)
    labels = np.array(pdf["label"].tolist(), dtype=np.int64)
    dataset = TensorDataset(torch.from_numpy(images), torch.from_numpy(labels))
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def _save_model(model: nn.Module, output_path: str, params: dict, metrics: dict):
    buf = io.BytesIO()
    torch.save(model.state_dict(), buf)
    weights_bytes = buf.getvalue()

    table = pa.table({
        "weights": [weights_bytes],
        "params": [json.dumps(params)],
        "metrics": [json.dumps(metrics)],
        "created_at": [datetime.now(timezone.utc).isoformat()],
    })

    df = daft.from_arrow(table)
    df.write_lance(output_path, mode="overwrite")
