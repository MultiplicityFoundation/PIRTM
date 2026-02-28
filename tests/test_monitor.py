from pirtm.monitor import Monitor
from pirtm.types import StepInfo


def test_monitor_empty_summary_and_last():
    monitor = Monitor()
    assert monitor.summary() == {"steps": 0, "max_q": 0.0, "converged": False}
    assert monitor.last() is None


def test_monitor_push_and_iter(safe_step_info, converged_status):
    monitor = Monitor(maxlen=2)
    record = monitor.push(safe_step_info, converged_status)
    assert record.info is safe_step_info
    assert len(list(monitor)) == 1
    summary = monitor.summary()
    assert summary["steps"] == 1
    assert summary["converged"] is True


def test_monitor_maxlen_eviction():
    monitor = Monitor(maxlen=2)
    for idx in range(3):
        info = StepInfo(idx, 0.5, 0.05, 0.2, 0.3, False, 0.01)
        monitor.push(info)
    assert len(list(monitor)) == 2
