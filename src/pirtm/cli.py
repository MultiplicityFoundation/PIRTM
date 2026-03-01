from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from typing import Any

import numpy as np

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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "transpile":
        parser.error("unsupported command")

    spec = build_spec(args, parser)

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
