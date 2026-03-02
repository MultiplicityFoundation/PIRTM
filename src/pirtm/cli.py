from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .petc import compute_coverage, validate_petc_chain
from .transpiler import transpile
from .transpiler.cli import add_transpile_parser, build_spec


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if is_dataclass(value) and not isinstance(value, type):
        return {key: _to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pirtm", description="PIRTM command-line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_transpile_parser(subparsers)

    petc_parser = subparsers.add_parser("petc", help="PETC chain tools")
    petc_subparsers = petc_parser.add_subparsers(dest="petc_command", required=True)

    coverage_parser = petc_subparsers.add_parser("coverage", help="Compute PETC coverage ratio")
    coverage_parser.add_argument("--chain", required=True, help="Path to JSON chain file")
    coverage_parser.add_argument("--range", dest="range_spec", required=True, help='Range "a-b"')

    validate_parser = petc_subparsers.add_parser("validate", help="Validate PETC chain invariants")
    validate_parser.add_argument("--chain", required=True, help="Path to JSON chain file")
    validate_parser.add_argument("--max-gap", type=int, default=100)
    validate_parser.add_argument("--min-coverage", type=float, default=0.8)
    validate_parser.add_argument("--coverage-window", type=int, default=1000)

    return parser


def _load_chain(path: str) -> list[int]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    values = payload.get("prime_indices", []) if isinstance(payload, dict) else payload
    if not isinstance(values, list):
        raise ValueError("chain JSON must be a list[int] or object with 'prime_indices'")
    return [int(value) for value in values]


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "petc":
        chain = _load_chain(args.chain)
        if args.petc_command == "coverage":
            left, right = args.range_spec.split("-", maxsplit=1)
            lo = int(left)
            hi = int(right)
            coverage = compute_coverage(chain, lo, hi)
            payload = {
                "coverage": coverage,
                "range": [min(lo, hi), max(lo, hi)],
                "chain_primes_in_range": sum(
                    1 for value in chain if min(lo, hi) <= value <= max(lo, hi)
                ),
            }
            print(json.dumps(payload, indent=2))
            return 0

        if args.petc_command == "validate":
            validation = validate_petc_chain(
                chain,
                max_gap=args.max_gap,
                min_coverage=args.min_coverage,
                coverage_window=args.coverage_window,
            )
            print(json.dumps(validation, indent=2))
            return 0 if bool(validation["valid"]) else 1

        parser.error("unsupported petc command")

    if args.command != "transpile":
        parser.error("unsupported command")

    spec = build_spec(args, parser)

    transpile_result = transpile(spec)

    if args.output == "summary":
        payload = {
            "verdict": transpile_result.verdict,
            "certified": transpile_result.certificate.certified,
            "steps": len(transpile_result.trajectory) - 1,
            "merkle_root": transpile_result.merkle_root,
            "petc_satisfied": transpile_result.petc_report.satisfied,
            "conformance_passed": transpile_result.compliance.passed,
        }
    else:
        payload = _to_jsonable(transpile_result)
        if not bool(args.emit_witness):
            payload.pop("witness_json", None)
        if not bool(args.emit_lambda_events):
            payload.pop("lambda_events", None)

    encoded = json.dumps(payload, indent=2)
    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
    else:
        print(encoded)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
