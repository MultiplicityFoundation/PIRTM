from pirtm.audit import AuditChain
from pirtm.petc_bridge import PETCAllocator
from pirtm.types import StepInfo


def _chain(n: int):
    chain = AuditChain()
    for idx in range(n):
        info = StepInfo(step=idx, q=0.4, epsilon=0.05, nXi=0.2, nLam=0.2, projected=False, residual=0.1)
        chain.append_step(info)
    return chain


def test_allocate_unique_primes_and_idempotent():
    allocator = PETCAllocator(max_sessions=10)
    a1 = allocator.allocate("s1", 5)
    a2 = allocator.allocate("s2", 5)
    a1_repeat = allocator.allocate("s1", 9)

    assert a1 is a1_repeat
    assert set(a1.allocated_primes).isdisjoint(set(a2.allocated_primes))
    assert a1.report.satisfied is True
    assert allocator.verify_global_ordering()["globally_ordered"] is True


def test_tag_audit_chain_pairs_prime_and_hash():
    allocator = PETCAllocator(max_sessions=10)
    chain = _chain(4)
    tagged = allocator.tag_audit_chain("s1", chain)
    assert len(tagged) == 4
    assert all(len(item) == 2 for item in tagged)
