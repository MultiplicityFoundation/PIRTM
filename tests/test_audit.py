import json

from pirtm.audit import AuditChain, AuditEvent
from pirtm.types import Certificate, StepInfo


def _step(step_index: int = 0) -> StepInfo:
    return StepInfo(step=step_index, q=0.4, epsilon=0.05, nXi=0.2, nLam=0.2, projected=False, residual=0.01)


def test_audit_chain_verify_true_for_clean_chain():
    chain = AuditChain()
    chain.append_step(_step(0))
    chain.append_certificate(Certificate(certified=True, margin=0.1, tail_bound=0.0))
    assert chain.verify() is True
    assert chain.head != AuditChain.GENESIS_HASH


def test_audit_chain_verify_false_on_payload_tamper():
    chain = AuditChain()
    chain.append_step(_step(0))
    event = chain.export()[0]
    tampered = AuditEvent(
        sequence=0,
        event_hash=event["event_hash"],
        chain_hash=event["chain_hash"],
        payload_json='{"type":"step","step":0,"q":9.99}',
    )
    chain._events[0] = tampered
    assert chain.verify() is False


def test_audit_chain_verify_false_on_chainhash_tamper():
    chain = AuditChain()
    chain.append_step(_step(0))
    event = chain.export()[0]
    tampered = AuditEvent(
        sequence=0,
        event_hash=event["event_hash"],
        chain_hash="f" * 64,
        payload_json=event["payload_json"],
    )
    chain._events[0] = tampered
    assert chain.verify() is False


def test_audit_export_is_json_parseable_and_deterministic_format():
    chain = AuditChain()
    chain.append_step(_step(0))
    exported = chain.export()
    json.dumps(exported)
    payload_json = exported[0]["payload_json"]
    assert payload_json == '{"epsilon":0.05,"nLam":0.2,"nXi":0.2,"projected":false,"q":0.4,"residual":0.01,"step":0,"type":"step"}'
    assert len(chain) == 1
