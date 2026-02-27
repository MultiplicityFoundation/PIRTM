import pytest

from pirtm.petc import PETCLedger, petc_invariants


def test_ledger_append_and_validate():
    ledger = PETCLedger(max_gap=10, min_length=3)
    for prime in [2, 3, 5, 7]:
        ledger.append(prime)
    report = ledger.validate()
    assert report.satisfied is True
    assert report.monotonic is True
    assert report.chain_length == 4


def test_ledger_append_nonprime_raises():
    ledger = PETCLedger()
    with pytest.raises(ValueError):
        ledger.append(4)


def test_ledger_gap_violation():
    ledger = PETCLedger(max_gap=2, min_length=2)
    ledger.append(2)
    ledger.append(11)
    report = ledger.validate()
    assert report.satisfied is False
    assert report.gap_violations == [(2, 11)]


def test_coverage_and_iterator():
    ledger = PETCLedger()
    for prime in [2, 3, 5, 7, 11]:
        ledger.append(prime)
    assert ledger.coverage(2, 11) == 1.0
    assert len(list(iter(ledger))) == len(ledger)


def test_petc_invariants_mass_violation_raises():
    with pytest.raises(ValueError):
        petc_invariants([2, 4, 6])


def test_petc_invariants_backcompat_ok():
    report = petc_invariants([2, 3, 5, 7, 11])
    assert report.satisfied is True
    assert report.primes_checked == [2, 3, 5, 7, 11]
