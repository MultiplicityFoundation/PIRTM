from __future__ import annotations

import argparse
import json
from typing import Any

from .spec import TranspileSpec


def add_transpile_parser(subparsers: Any) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("transpile", help="Transpile into PIRTM runtime artifacts")
    parser.add_argument("--type", dest="input_type", required=True)
    parser.add_argument("--input", dest="input_ref", required=True)
    parser.add_argument("--prime-index", type=int, required=True)
    parser.add_argument("--identity-commitment", required=True)
    parser.add_argument("--dim", type=int, default=8)
    parser.add_argument("--epsilon", type=float, default=0.05)
    parser.add_argument("--max-steps", type=int, default=1000)
    parser.add_argument("--op-norm-T", type=float, default=0.5)
    parser.add_argument("--emission-policy", default="suppress")
    parser.add_argument("--metadata", default="{}")
    parser.add_argument(
        "--hash-scheme",
        default="dual",
        choices=["sha256", "poseidon_compat", "dual"],
        help="Primary witness hash scheme (dual emits both SHA-256 and Poseidon-compatible fields)",
    )
    parser.add_argument(
        "--dual-hash",
        action="store_true",
        help="Force dual-hash witness output regardless of --hash-scheme",
    )
    parser.add_argument(
        "--emit-witness",
        action="store_true",
        help="Include witness JSON in CLI output payload",
    )
    parser.add_argument(
        "--emit-lambda-events",
        action="store_true",
        help="Include Lambda bridge events in CLI output payload",
    )
    parser.add_argument("--output", default="json", choices=["json", "summary"])
    parser.add_argument("--output-file", default="")
    return parser


def parse_metadata(raw_metadata: str, parser: argparse.ArgumentParser) -> dict[str, Any]:
    try:
        metadata = json.loads(raw_metadata)
    except json.JSONDecodeError as exc:
        parser.error(f"--metadata must be valid JSON: {exc.msg}")
    if not isinstance(metadata, dict):
        parser.error("--metadata must decode to a JSON object")
    return dict(metadata)


def build_spec(args: argparse.Namespace, parser: argparse.ArgumentParser) -> TranspileSpec:
    metadata = parse_metadata(str(args.metadata), parser)
    metadata["hash_scheme"] = str(args.hash_scheme)
    metadata["dual_hash"] = bool(args.dual_hash)

    return TranspileSpec(
        input_type=str(args.input_type),
        input_ref=str(args.input_ref),
        prime_index=int(args.prime_index),
        identity_commitment=str(args.identity_commitment),
        dim=int(args.dim),
        epsilon=float(args.epsilon),
        max_steps=int(args.max_steps),
        op_norm_T=float(args.op_norm_T),
        emission_policy=str(args.emission_policy),
        metadata=metadata,
    )
