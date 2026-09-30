import pytest
from backend.scheduler import (
    Job,
    greedy_schedule,
    naive_edf_schedule,
    fcfs_schedule,
    is_feasible,
    brute_force_best,
    step_by_step_trace
)


def test_empty_jobs():
    sch, rej, total = greedy_schedule([], 2)
    assert sch == {}
    assert rej == []
    assert total == 0

    edf_done, edf_total = naive_edf_schedule([], 2)
    assert edf_done == []
    assert edf_total == 0

    fcfs_done, fcfs_total = fcfs_schedule([], 2)
    assert fcfs_done == []
    assert fcfs_total == 0


def test_invalid_processors():
    jobs = [Job("J1", 1, 10)]
    with pytest.raises(ValueError, match="need at least one processor"):
        greedy_schedule(jobs, 0)
    with pytest.raises(ValueError, match="need at least one processor"):
        greedy_schedule(jobs, -1)


def test_single_processor_demo():
    jobs = [
        Job("J1", 2, 100), Job("J2", 1, 19), Job("J3", 2, 27), Job("J4", 1, 25),
        Job("J5", 3, 15), Job("J6", 3, 60), Job("J7", 2, 40), Job("J8", 4, 35)
    ]
    sch, rej, total = greedy_schedule(jobs, 1)
    assert total == 235
    scheduled_ids = sorted(j.job_id for j in sch.values())
    assert scheduled_ids == ["J1", "J6", "J7", "J8"]
    rejected_ids = sorted(j.job_id for j in rej)
    assert rejected_ids == ["J2", "J3", "J4", "J5"]


def test_two_processors_demo():
    jobs = [
        Job("J1", 2, 100), Job("J2", 1, 19), Job("J3", 2, 27), Job("J4", 1, 25),
        Job("J5", 3, 15), Job("J6", 3, 60), Job("J7", 2, 40), Job("J8", 4, 35)
    ]
    sch, rej, total = greedy_schedule(jobs, 2)
    assert total == 302
    scheduled_ids = sorted(j.job_id for j in sch.values())
    assert scheduled_ids == ["J1", "J3", "J4", "J5", "J6", "J7", "J8"]
    rejected_ids = sorted(j.job_id for j in rej)
    assert rejected_ids == ["J2"]


def test_deadline_constraints():
    jobs = [Job(f"J{i}", d, p) for i, (d, p) in enumerate([(1, 50), (1, 60), (2, 80), (2, 20), (3, 100)])]
    sch, rej, total = greedy_schedule(jobs, 2)
    for (proc, time_slot), job in sch.items():
        assert time_slot <= job.deadline, f"Job {job.job_id} scheduled at {time_slot} but deadline is {job.deadline}"
        assert 0 <= proc < 2


def test_step_by_step_trace():
    jobs = [Job("J1", 2, 100), Job("J2", 1, 50), Job("J3", 1, 80)]
    trace = step_by_step_trace(jobs, 1)
    assert len(trace["steps"]) == 3
    assert trace["total_profit"] == 180
    assert trace["steps"][0]["job"]["id"] == "J1"
    assert trace["steps"][0]["status"] == "scheduled"
    assert trace["steps"][1]["job"]["id"] == "J3"
    assert trace["steps"][1]["status"] == "scheduled"
    assert trace["steps"][2]["job"]["id"] == "J2"
    assert trace["steps"][2]["status"] == "rejected"


def test_brute_force_equivalence():
    jobs = [
        Job("A", 1, 30),
        Job("B", 2, 40),
        Job("C", 2, 35),
        Job("D", 3, 25),
        Job("E", 1, 10)
    ]
    for m in (1, 2, 3):
        sch, rej, greedy_total = greedy_schedule(jobs, m)
        opt_total = brute_force_best(jobs, m)
        assert greedy_total == opt_total
