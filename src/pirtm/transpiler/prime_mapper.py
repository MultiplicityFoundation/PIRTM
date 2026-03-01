from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class PrimeChannel:
    prime: int
    digest: str
    vector: np.ndarray


def _prime_stream(n: int) -> list[int]:
    if n <= 0:
        return []
    primes: list[int] = []
    value = 2
    while len(primes) < n:
        if _is_prime(value):
            primes.append(value)
        value += 1
    return primes


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    cursor = 3
    while cursor * cursor <= n:
        if n % cursor == 0:
            return False
        cursor += 2
    return True


def _to_vector(payload: bytes, dim: int) -> np.ndarray:
    values = np.frombuffer(payload, dtype=np.uint8).astype(float)
    if values.size == 0:
        return np.zeros(dim, dtype=float)
    bins = np.array_split(values, dim)
    return np.array([float(chunk.mean()) if chunk.size else 0.0 for chunk in bins], dtype=float)


def _chunk_bytes(raw: bytes, chunk_size: int = 1024) -> list[bytes]:
    return [raw[idx : idx + chunk_size] for idx in range(0, len(raw), chunk_size)]


def _csv_columns(raw: bytes) -> list[bytes]:
    text = raw.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return []
    columns: dict[str, list[str]] = {name: [] for name in reader.fieldnames}
    for row in reader:
        for key in reader.fieldnames:
            columns[key].append(str(row.get(key, "")))
    return ["\n".join(values).encode("utf-8") for values in columns.values()]


def _json_channels(raw: bytes) -> list[bytes]:
    parsed = json.loads(raw.decode("utf-8"))
    if isinstance(parsed, dict):
        return [
            json.dumps({key: value}, sort_keys=True, separators=(",", ":")).encode("utf-8")
            for key, value in parsed.items()
        ]
    if isinstance(parsed, list):
        return [
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
            for value in parsed
        ]
    return [json.dumps(parsed, sort_keys=True, separators=(",", ":")).encode("utf-8")]


def _text_paragraphs(raw: bytes) -> list[bytes]:
    text = raw.decode("utf-8")
    paragraphs = [entry.strip() for entry in text.split("\n\n") if entry.strip()]
    return [entry.encode("utf-8") for entry in paragraphs]


def map_content_to_prime_channels(
    raw: bytes,
    input_ref: str,
    dim: int,
    prime_map: list[int] | None = None,
) -> list[PrimeChannel]:
    lower = input_ref.lower()
    channels: list[bytes]
    try:
        if lower.endswith(".csv"):
            channels = _csv_columns(raw)
        elif lower.endswith(".json"):
            channels = _json_channels(raw)
        elif lower.endswith((".txt", ".md")):
            channels = _text_paragraphs(raw)
        else:
            channels = _chunk_bytes(raw)
    except (UnicodeDecodeError, json.JSONDecodeError, csv.Error):
        channels = _chunk_bytes(raw)

    if not channels:
        channels = [raw if raw else b""]

    if prime_map is None:
        primes = _prime_stream(len(channels))
    else:
        if len(prime_map) != len(channels):
            raise ValueError(
                f"prime_map length ({len(prime_map)}) must match channels ({len(channels)})"
            )
        if not all(_is_prime(int(value)) for value in prime_map):
            raise ValueError("prime_map must contain only prime values")
        if len(set(int(value) for value in prime_map)) != len(prime_map):
            raise ValueError("prime_map must not contain duplicates")
        primes = [int(value) for value in prime_map]

    mapped: list[PrimeChannel] = []
    for prime, channel in zip(primes, channels, strict=True):
        digest = hashlib.sha256(channel).hexdigest()
        mapped.append(PrimeChannel(prime=prime, digest=digest, vector=_to_vector(channel, dim)))
    return mapped
