import pytest
import json
import hashlib

from pirtm.transpiler import TranspileSpec, transpile


def test_transpile_data_asset_end_to_end(tmp_path):
    input_file = tmp_path / "dataset.csv"
    input_file.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")

    spec = TranspileSpec(
        input_type="data_asset",
        input_ref=str(input_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=6,
        max_steps=8,
        emission_policy="pass_through",
    )

    result = transpile(spec)

    assert result.xi_initial.shape[1] == 6
    assert len(result.trajectory) >= 2
    assert result.petc_report.satisfied is True
    assert result.certificate.details["steps"] >= 3
    assert result.compliance.passed is True
    assert result.merkle_root
    assert result.witness_json["primeIndex"] == 7919
    assert result.verdict in {"CERTIFIED", "UNCERTIFIED", "SILENT"}

    payload0 = json.loads(result.audit_export[0]["payload_json"])
    payload1 = json.loads(result.audit_export[1]["payload_json"])
    assert payload0["type"] == "identity_binding"
    assert payload1["type"] == "content_anchor"
    assert result.witness_json["pathType"] == "data_asset"
    assert result.witness_json["channelCount"] == 2
    assert result.witness_json["channelPrimes"] == [2, 3]
    assert result.witness_json["merkleRootPoseidon"] is not None
    assert result.witness_json["stateHashPoseidon"]


def test_transpile_data_asset_with_prime_map(tmp_path):
    input_file = tmp_path / "doc.txt"
    input_file.write_text("alpha\n\nbeta", encoding="utf-8")

    spec = TranspileSpec(
        input_type="data_asset",
        input_ref=str(input_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=4,
        metadata={"prime_map": [11, 13]},
    )

    result = transpile(spec)
    assert result.witness_json["channelPrimes"] == [11, 13]


def test_transpile_data_asset_invalid_prime_map_rejected(tmp_path):
    input_file = tmp_path / "doc.txt"
    input_file.write_text("alpha\n\nbeta", encoding="utf-8")

    spec = TranspileSpec(
        input_type="data_asset",
        input_ref=str(input_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=4,
        metadata={"prime_map": [11, 12]},
    )

    with pytest.raises(ValueError, match="prime_map"):
        transpile(spec)


def test_transpile_requires_prime_identity(tmp_path):
    input_file = tmp_path / "doc.txt"
    input_file.write_text("hello", encoding="utf-8")

    spec = TranspileSpec(
        input_type="data_asset",
        input_ref=str(input_file),
        prime_index=8,
        identity_commitment="0xabc123",
    )

    with pytest.raises(ValueError):
        transpile(spec)


def test_transpile_computation_end_to_end(tmp_path):
    input_file = tmp_path / "computation.json"
    input_file.write_text(
        '{"mode":"gradient_descent","steps":7,"learning_rate":0.15,"initial_state":[1,1,1],"target_state":[0,0,0]}',
        encoding="utf-8",
    )

    spec = TranspileSpec(
        input_type="computation",
        input_ref=str(input_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=3,
        emission_policy="pass_through",
        op_norm_T=0.5,
    )

    result = transpile(spec)

    assert len(result.trajectory) == 8
    assert result.certificate.details["steps"] == 7
    assert result.witness_json["pathType"] == "computation"
    assert result.witness_json["trajectoryLength"] == len(result.trajectory)
    assert result.witness_json["stepCount"] == 7
    assert "qMax" in result.witness_json
    assert result.petc_report.chain_length >= 3
    assert result.witness_json["weightScheduleValid"] is True
    assert result.witness_json["weightSchedulePrimeCount"] == 7
    assert "descriptorHash" in result.witness_json
    assert result.witness_json["merkleRootPoseidon"] is not None
    assert result.witness_json["hashSchemes"] == ["sha256", "poseidon_compat"]

    payload0 = json.loads(result.audit_export[0]["payload_json"])
    assert payload0["type"] == "identity_binding"

    expected_state_hash = hashlib.sha256(
        json.dumps(result.xi_initial.tolist(), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert result.witness_json["stateHash"] == expected_state_hash


def test_transpile_computation_adam_mode(tmp_path):
    input_file = tmp_path / "computation_adam.json"
    input_file.write_text(
        '{"mode":"adam","steps":6,"learning_rate":0.1,"beta1":0.9,"beta2":0.99,"initial_state":[1,1,1],"target_state":[0,0,0]}',
        encoding="utf-8",
    )

    spec = TranspileSpec(
        input_type="computation",
        input_ref=str(input_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=3,
        emission_policy="pass_through",
        op_norm_T=0.5,
    )

    result = transpile(spec)

    assert result.witness_json["mode"] == "adam"
    assert "beta1" in result.witness_json
    assert "effectiveLrMax" in result.witness_json
    assert result.certificate.details["steps"] == 6


def test_transpile_computation_iterative_solver_mode(tmp_path):
    input_file = tmp_path / "computation_iterative.json"
    input_file.write_text(
        '{"mode":"iterative_solver","steps":5,"relaxation":0.25,"initial_state":[1,1],"target_state":[0,0]}',
        encoding="utf-8",
    )

    spec = TranspileSpec(
        input_type="computation",
        input_ref=str(input_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=2,
        emission_policy="pass_through",
        op_norm_T=0.5,
    )

    result = transpile(spec)

    assert result.witness_json["mode"] == "iterative_solver"
    assert result.witness_json["relaxation"] == pytest.approx(0.25)
    assert result.certificate.details["steps"] == 5


def test_transpile_computation_two_layer_nn_mode(tmp_path):
    input_file = tmp_path / "computation_mlp2.json"
    input_file.write_text(
        '{"mode":"two_layer_nn","steps":8,"learning_rate":0.12,"input_dim":2,"hidden_dim":3,"output_dim":1,"seed":7}',
        encoding="utf-8",
    )

    spec = TranspileSpec(
        input_type="computation",
        input_ref=str(input_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=13,
        emission_policy="pass_through",
        op_norm_T=0.5,
    )

    result = transpile(spec)

    assert result.witness_json["mode"] == "two_layer_nn"
    assert result.witness_json["modelShape"] == [2, 3, 1]
    assert result.witness_json["parameterCount"] == 13
    assert result.witness_json["lossInitial"] is not None
    assert result.witness_json["lossFinal"] is not None
    assert result.witness_json["lossFinal"] <= result.witness_json["lossInitial"]


def test_transpile_computation_prime_step_petc_indexing(tmp_path):
    input_file = tmp_path / "computation_primes.json"
    input_file.write_text(
        '{"mode":"gradient_descent","steps":10,"learning_rate":0.15,"initial_state":[1,1,1],"target_state":[0,0,0]}',
        encoding="utf-8",
    )

    spec = TranspileSpec(
        input_type="computation",
        input_ref=str(input_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=3,
        emission_policy="pass_through",
        op_norm_T=0.5,
    )

    result = transpile(spec)
    assert result.petc_report.primes_checked == [2, 3, 5, 7]


def test_transpile_computation_adaptive_override(tmp_path):
    input_file = tmp_path / "computation_adaptive_off.json"
    input_file.write_text(
        '{"mode":"gradient_descent","steps":5,"learning_rate":0.15,"adaptive":false,"initial_state":[1,1,1],"target_state":[0,0,0]}',
        encoding="utf-8",
    )

    spec = TranspileSpec(
        input_type="computation",
        input_ref=str(input_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=3,
        emission_policy="pass_through",
        op_norm_T=0.5,
    )

    result = transpile(spec)
    assert result.witness_json["adaptiveEnabled"] is False


def test_transpile_computation_invalid_adam_descriptor(tmp_path):
    input_file = tmp_path / "bad_adam.json"
    input_file.write_text(
        '{"mode":"adam","steps":4,"learning_rate":0.1,"beta1":1.2,"beta2":0.99}',
        encoding="utf-8",
    )

    spec = TranspileSpec(
        input_type="computation",
        input_ref=str(input_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=3,
    )

    with pytest.raises(ValueError, match="beta1"):
        transpile(spec)


def test_transpile_computation_invalid_steps_descriptor(tmp_path):
    input_file = tmp_path / "bad_steps.json"
    input_file.write_text('{"mode":"gradient_descent","steps":0}', encoding="utf-8")

    spec = TranspileSpec(
        input_type="computation",
        input_ref=str(input_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=3,
    )

    with pytest.raises(ValueError, match="steps"):
        transpile(spec)


def test_transpile_workflow_end_to_end(tmp_path):
    workflow_file = tmp_path / "workflow.json"
    workflow_file.write_text(
        json.dumps(
            {
                "steps": [
                    {
                        "id": "s1",
                        "mode": "gradient_descent",
                        "steps": 3,
                        "learning_rate": 0.15,
                        "initial_state": [1, 1, 1],
                        "target_state": [0, 0, 0],
                    },
                    {
                        "id": "s2",
                        "mode": "adam",
                        "steps": 3,
                        "learning_rate": 0.1,
                        "beta1": 0.9,
                        "beta2": 0.99,
                        "dependencies": ["s1"],
                    },
                    {
                        "id": "s3",
                        "mode": "iterative_solver",
                        "steps": 3,
                        "relaxation": 0.2,
                        "dependencies": ["s2"],
                        "prime_index": 11,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    spec = TranspileSpec(
        input_type="workflow",
        input_ref=str(workflow_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=3,
        emission_policy="pass_through",
        op_norm_T=0.5,
    )

    result = transpile(spec)

    assert result.witness_json["pathType"] == "workflow"
    assert result.witness_json["workflowStepCount"] == 3
    assert result.petc_report.satisfied is True
    assert result.certificate.details["session_ids"] == ["s1", "s2", "s3"]
    assert result.witness_json["merkleRootPoseidon"] is not None
    assert result.verdict in {"CERTIFIED", "UNCERTIFIED"}


def test_transpile_workflow_cycle_rejected(tmp_path):
    workflow_file = tmp_path / "workflow_cycle.json"
    workflow_file.write_text(
        json.dumps(
            {
                "steps": [
                    {"id": "a", "mode": "gradient_descent", "steps": 2, "dependencies": ["b"]},
                    {"id": "b", "mode": "gradient_descent", "steps": 2, "dependencies": ["a"]},
                ]
            }
        ),
        encoding="utf-8",
    )

    spec = TranspileSpec(
        input_type="workflow",
        input_ref=str(workflow_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=3,
    )

    with pytest.raises(ValueError, match="cycle"):
        transpile(spec)


def test_transpile_workflow_unknown_dependency_rejected(tmp_path):
    workflow_file = tmp_path / "workflow_unknown_dep.json"
    workflow_file.write_text(
        json.dumps(
            {
                "steps": [
                    {"id": "a", "mode": "gradient_descent", "steps": 2},
                    {"id": "b", "mode": "gradient_descent", "steps": 2, "dependencies": ["missing"]},
                ]
            }
        ),
        encoding="utf-8",
    )

    spec = TranspileSpec(
        input_type="workflow",
        input_ref=str(workflow_file),
        prime_index=7919,
        identity_commitment="0xabc123",
        dim=3,
    )

    with pytest.raises(ValueError, match="unknown step"):
        transpile(spec)
