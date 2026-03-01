import json

from pirtm.audit import AuditChain
from pirtm.lambda_bridge import LambdaTraceBridge, SubmissionReceipt
from pirtm.types import StepInfo


def _chain():
    chain = AuditChain()
    info = StepInfo(step=0, q=0.4, epsilon=0.05, nXi=0.2, nLam=0.2, projected=False, residual=0.1)
    chain.append_step(info)
    chain.append_gate(0, emitted=True, policy="emitted", reason="")
    return chain


def test_translate_maps_schema_ids_and_types():
    bridge = LambdaTraceBridge(session_id="abc", capability_token="token")
    events = bridge.translate(_chain())
    assert len(events) == 2
    assert events[0].schema_id == "pirtm.step.v1"
    assert events[1].schema_id == "pirtm.gate.v1"
    assert events[0].event_type == "pirtm.step"


def test_batch_submit_dry_run_and_empty():
    bridge = LambdaTraceBridge(session_id="abc")
    empty = bridge.batch_submit()
    assert empty.status == "empty"
    assert empty.poseidon_merkle_root == "0" * 64

    bridge.translate(_chain())
    receipt = bridge.batch_submit()
    assert receipt.status == "dry_run"
    assert receipt.events_submitted == 2
    assert receipt.poseidon_merkle_root is not None
    assert len(receipt.poseidon_merkle_root) == 64
    assert bridge.pending_count == 0


def test_batch_submit_calls_submit_fn_and_merkle_handles_odd():
    called = {"count": 0, "payload": None}

    def submit_fn(payload):
        called["count"] += 1
        called["payload"] = payload
        return SubmissionReceipt(
            batch_id="b1",
            events_submitted=len(payload),
            merkle_root="r1",
            status="accepted",
            timestamp=0.0,
        )

    bridge = LambdaTraceBridge(session_id="abc", submit_fn=submit_fn)
    chain = _chain()
    chain.append_gate(1, emitted=False, policy="suppress", reason="x")
    bridge.translate(chain)
    receipt = bridge.batch_submit()

    assert receipt.status == "accepted"
    assert called["count"] == 1
    assert isinstance(called["payload"], list)

    merkle = LambdaTraceBridge._compute_merkle_root(["a" * 64, "b" * 64, "c" * 64])
    poseidon_merkle = LambdaTraceBridge._compute_poseidon_merkle_root(
        ["a" * 64, "b" * 64, "c" * 64]
    )
    assert isinstance(merkle, str)
    assert len(merkle) == 64
    assert isinstance(poseidon_merkle, str)
    assert len(poseidon_merkle) == 64

    json.dumps(called["payload"], default=str)


def test_batch_submit_rejected_keeps_pending_events():
    def submit_fn(payload):
        return SubmissionReceipt(
            batch_id="b-rej",
            events_submitted=len(payload),
            merkle_root="r-rej",
            status="rejected",
            timestamp=0.0,
        )

    bridge = LambdaTraceBridge(session_id="abc", submit_fn=submit_fn)
    bridge.translate(_chain())
    receipt = bridge.batch_submit()

    assert receipt.status == "rejected"
    assert bridge.pending_count == 2
