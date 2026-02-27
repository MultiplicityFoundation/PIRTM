from pirtm.types import (
    Certificate,
    CSCBudget,
    CSCMargin,
    MonitorRecord,
    PETCEntry,
    PETCReport,
    Status,
    StepInfo,
    WeightSchedule,
)


def test_step_info_construction():
    info = StepInfo(1, 0.8, 0.05, 0.2, 0.6, False, 1e-3)
    assert info.step == 1
    assert info.q == 0.8
    assert info.note is None


def test_status_and_certificate_defaults():
    status = Status(True, True, 10, 1e-8, 0.05)
    cert = Certificate(True, 0.1, 0.2)
    assert status.converged is True
    assert cert.details == {}


def test_petc_report_and_entry_defaults(safe_step_info):
    entry = PETCEntry(prime=2, event={"x": 1}, info=safe_step_info)
    report = PETCReport(satisfied=True)
    assert entry.prime == 2
    assert report.chain_length == 0
    assert report.primes_checked == []


def test_weight_and_csc_types(identity):
    schedule = WeightSchedule([identity], [identity], q_targets=[0.5], primes_used=[2])
    budget = CSCBudget(0.4, 0.2, 0.9, 0.1, 2.0, 0.5)
    margin = CSCMargin(0.1, 0.8, 0.9, 0.5, 0.1, True)
    assert len(schedule.Xi_seq) == 1
    assert budget.q_star == 0.9
    assert margin.safe is True


def test_monitor_record_construction(safe_step_info, converged_status):
    record = MonitorRecord(step=1, info=safe_step_info, status=converged_status)
    assert record.status is converged_status


def test_slots_enforced():
    instances = [
        StepInfo(0, 0.5, 0.05, 0.2, 0.3, False, 0.01),
        Status(False, True, 0, 0.0, 0.05),
        Certificate(False, -0.1, 1.0),
        PETCReport(False),
        PETCEntry(2),
        CSCBudget(0.1, 0.2, 0.3, 0.05, 1.0, 0.5),
        CSCMargin(0.1, 0.2, 0.3, 1.0, 0.05, True),
    ]
    for item in instances:
        assert not hasattr(item, "__dict__")
