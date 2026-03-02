import json

from pirtm.cli import main


def test_cli_petc_coverage(tmp_path, capsys):
    chain_file = tmp_path / "chain.json"
    chain_file.write_text(json.dumps([2, 3, 5, 11, 13]), encoding="utf-8")

    code = main(["petc", "coverage", "--chain", str(chain_file), "--range", "2-13"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["coverage"] == 5 / 6
    assert payload["range"] == [2, 13]


def test_cli_petc_validate_exit_code(tmp_path, capsys):
    chain_file = tmp_path / "chain_bad.json"
    chain_file.write_text(json.dumps([2, 11]), encoding="utf-8")

    code = main(
        [
            "petc",
            "validate",
            "--chain",
            str(chain_file),
            "--max-gap",
            "2",
            "--min-coverage",
            "1.0",
            "--coverage-window",
            "20",
        ]
    )

    assert code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is False
    assert payload["gap_ok"] is False
