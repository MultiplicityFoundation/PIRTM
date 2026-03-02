"""Conformance tests for §9 witness dual-hash behavior."""

import json

from pirtm.cli import main


def _run_transpile_witness(tmp_path, capsys, *extra_args: str) -> dict[str, object]:
    computation_file = tmp_path / "computation.json"
    computation_file.write_text('{"mode":"gradient_descent","steps":3}', encoding="utf-8")

    code = main(
        [
            "transpile",
            "--type",
            "computation",
            "--input",
            str(computation_file),
            "--prime-index",
            "7919",
            "--identity-commitment",
            "0xabc123",
            "--dim",
            "3",
            "--emit-witness",
            "--output",
            "json",
            *extra_args,
        ]
    )
    assert code == 0

    payload = json.loads(capsys.readouterr().out)
    return payload["witness_json"]


def test_dual_hash_includes_sha256_and_poseidon_fields(tmp_path, capsys):
    witness = _run_transpile_witness(tmp_path, capsys, "--dual-hash")

    assert witness["hashSchemes"] == ["sha256", "poseidon_compat"]
    assert witness["hashScheme"] == "sha256"
    assert "stateHashSha256" in witness
    assert "stateHashPoseidon" in witness
    assert "merkleRootSha256" in witness
    assert "merkleRootPoseidon" in witness


def test_single_hash_sha256_excludes_poseidon_fields(tmp_path, capsys):
    witness = _run_transpile_witness(tmp_path, capsys, "--hash-scheme", "sha256")

    assert witness["hashSchemes"] == ["sha256"]
    assert witness["hashScheme"] == "sha256"
    assert "stateHashPoseidon" not in witness
    assert "merkleRootPoseidon" not in witness


def test_single_hash_poseidon_excludes_dual_fields(tmp_path, capsys):
    witness = _run_transpile_witness(tmp_path, capsys, "--hash-scheme", "poseidon_compat")

    assert witness["hashSchemes"] == ["poseidon_compat"]
    assert witness["hashScheme"] == "poseidon_compat"
    assert "stateHashPoseidon" not in witness
    assert "merkleRootPoseidon" not in witness
