from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from typing import Any

import numpy as np

from .transpiler import TranspileSpec, transpile


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if is_dataclass(value):
        return {key: _to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pirtm", description="PIRTM command-line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    transpile_parser = subparsers.add_parser("transpile", help="Transpile into PIRTM runtime artifacts")
    transpile_parser.add_argument("--type", dest="input_type", required=True)
    transpile_parser.add_argument("--input", dest="input_ref", required=True)
    transpile_parser.add_argument("--prime-index", type=int, required=True)
    transpile_parser.add_argument("--identity-commitment", required=True)
    transpile_parser.add_argument("--dim", type=int, default=8)
    transpile_parser.add_argument("--epsilon", type=float, default=0.05)
    transpile_parser.add_argument("--max-steps", type=int, default=1000)
    transpile_parser.add_argument("--op-norm-T", type=float, default=0.5)
    transpile_parser.add_argument("--emission-policy", default="suppress")
    transpile_parser.add_argument("--metadata", default="{}")
    transpile_parser.add_argument(
        "--hash-scheme",
        default="dual",
        choices=["sha256", "poseidon_compat", "dual"],
        help="Primary witness hash scheme (dual emits both SHA-256 and Poseidon-compatible fields)",
    )
    transpile_parser.add_argument(
        "--dual-hash",
        action="store_true",
        help="Force dual-hash witness output regardless of --hash-scheme",
    )
    transpile_parser.add_argument("--output", default="json", choices=["json", "summary"])
    transpile_parser.add_argument("--output-file", default="")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "transpile":
        parser.error("unsupported command")

    metadata = json.loads(args.metadata)
    if not isinstance(metadata, dict):
        raise ValueError("--metadata must decode to a JSON object")
    metadata = dict(metadata)
    metadata["hash_scheme"] = str(args.hash_scheme)
    metadata["dual_hash"] = bool(args.dual_hash)

    spec = TranspileSpec(
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

    result = transpile(spec)

    if args.output == "summary":
        payload = {
            "verdict": result.verdict,
            "certified": result.certificate.certified,
            "steps": len(result.trajectory) - 1,
            "merkle_root": result.merkle_root,
            "petc_satisfied": result.petc_report.satisfied,
            "conformance_passed": result.compliance.passed,
        }
    else:
        payload = _to_jsonable(result)

    encoded = json.dumps(payload, indent=2)
    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
    else:
        print(encoded)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
