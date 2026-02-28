import json

import pytest

from pirtm.cli import main


def test_cli_transpile_computation_json_output(tmp_path, capsys):
    computation_file = tmp_path / "computation.json"
    computation_file.write_text(
        '{"mode":"gradient_descent","steps":5,"learning_rate":0.2,"initial_state":[1,1,1],"target_state":[0,0,0]}',
        encoding="utf-8",
    )

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
            "--emission-policy",
            "pass_through",
            "--output",
            "json",
        ]
    )

    assert code == 0
    stdout = capsys.readouterr().out
    payload = json.loads(stdout)
    assert payload["spec"]["input_type"] == "computation"
    assert payload["witness_json"]["pathType"] == "computation"
    assert payload["certificate"]["details"]["steps"] == 5


def test_cli_transpile_summary_to_file(tmp_path):
    computation_file = tmp_path / "computation.json"
    output_file = tmp_path / "result.json"
    computation_file.write_text('{"mode":"gradient_descent","steps":4}', encoding="utf-8")

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
            "2",
            "--output",
            "summary",
            "--output-file",
            str(output_file),
        ]
    )

    assert code == 0
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert "verdict" in payload
    assert payload["steps"] == 4


def test_cli_transpile_workflow_summary(tmp_path, capsys):
    workflow_file = tmp_path / "workflow.json"
    workflow_file.write_text(
        json.dumps(
            {
                "steps": [
                    {
                        "id": "s1",
                        "mode": "gradient_descent",
                        "steps": 2,
                        "learning_rate": 0.15,
                    },
                    {
                        "id": "s2",
                        "mode": "iterative_solver",
                        "steps": 2,
                        "relaxation": 0.2,
                        "dependencies": ["s1"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    code = main(
        [
            "transpile",
            "--type",
            "workflow",
            "--input",
            str(workflow_file),
            "--prime-index",
            "7919",
            "--identity-commitment",
            "0xabc123",
            "--dim",
            "3",
            "--emission-policy",
            "pass_through",
            "--output",
            "summary",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["petc_satisfied"] is True


def test_cli_transpile_workflow_unknown_dependency_rejected(tmp_path):
    workflow_file = tmp_path / "workflow_unknown_dep.json"
    workflow_file.write_text(
        json.dumps(
            {
                "steps": [
                    {"id": "s1", "mode": "gradient_descent", "steps": 2},
                    {
                        "id": "s2",
                        "mode": "iterative_solver",
                        "steps": 2,
                        "relaxation": 0.2,
                        "dependencies": ["missing"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unknown step"):
        main(
            [
                "transpile",
                "--type",
                "workflow",
                "--input",
                str(workflow_file),
                "--prime-index",
                "7919",
                "--identity-commitment",
                "0xabc123",
                "--dim",
                "3",
                "--output",
                "summary",
            ]
        )


def test_cli_transpile_hash_scheme_poseidon(tmp_path, capsys):
    computation_file = tmp_path / "computation_poseidon.json"
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
            "--hash-scheme",
            "poseidon_compat",
            "--output",
            "json",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    witness = payload["witness_json"]
    assert witness["hashScheme"] == "poseidon_compat"
    assert witness["hashSchemes"] == ["poseidon_compat"]
    assert "stateHashPoseidon" not in witness


def test_cli_transpile_dual_hash_override(tmp_path, capsys):
    computation_file = tmp_path / "computation_dual.json"
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
            "--hash-scheme",
            "sha256",
            "--dual-hash",
            "--output",
            "json",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    witness = payload["witness_json"]
    assert witness["hashSchemes"] == ["sha256", "poseidon_compat"]
    assert "stateHashPoseidon" in witness
