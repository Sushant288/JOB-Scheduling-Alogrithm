"""
Cloud Computing Job Scheduler - Greedy Job Sequencing with Deadlines
====================================================================
Each job needs 1 unit of processor time, has a deadline (latest finishing
time slot) and a profit earned only if the job finishes by its deadline.
There are m identical processors (cloud VMs). Goal: maximise total profit.

Greedy strategy
  1. Sort jobs by profit, highest first.
  2. Give each job the LATEST free slot (on any processor) not after its deadline.
  3. If no such slot exists, reject the job.

Implementation trick: the m processors are "unrolled" into one timeline of
m*D slots (slot index i -> time i//m + 1, processor i % m). A Disjoint Set Union
finds the latest free slot <= a given index in near-constant time, so the whole
algorithm runs in O(n log n) (dominated by sorting).
"""
import random
import sys
import time
from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Job:
    job_id: str
    deadline: int
    profit: int


def greedy_schedule(jobs, m):
    """Return (schedule, rejected, total_profit).
    schedule: dict {(processor, time_slot): Job}  (processor 0..m-1, time 1..D)"""
    if m < 1:
        raise ValueError("need at least one processor")
    if not jobs:
        return {}, [], 0
    D = max(j.deadline for j in jobs)
    size = m * D
    parent = list(range(size))            # DSU: parent[i] -> latest free slot <= i (or -1)

    def find(i):
        root = i
        while root >= 0 and parent[root] != root:
            root = parent[root]
        while i >= 0 and parent[i] != root:   # path compression
            parent[i], i = root, parent[i]
        return root

    schedule, rejected, total = {}, [], 0
    for job in sorted(jobs, key=lambda j: (-j.profit, j.deadline, j.job_id)):
        if job.deadline < 1:
            rejected.append(job); continue
        slot = find(min(job.deadline, D) * m - 1)
        if slot < 0:
            rejected.append(job)
        else:
            schedule[(slot % m, slot // m + 1)] = job
            total += job.profit
            parent[slot] = slot - 1        # slot used: future finds fall through to the left
    return schedule, rejected, total


def naive_edf_schedule(jobs, m):
    """Baseline: earliest-deadline-first, ignores profit. Fills slots left to right."""
    if not jobs:
        return [], 0
    D = max(j.deadline for j in jobs)
    free = {t: m for t in range(1, D + 1)}
    t, total, done = 1, 0, []
    for job in sorted(jobs, key=lambda j: (j.deadline, j.job_id)):
        while t <= D and free[t] == 0:
            t += 1
        if t <= job.deadline and t <= D:
            free[t] -= 1; total += job.profit; done.append(job)
    return done, total


def fcfs_schedule(jobs, m):
    """Baseline: first-come-first-served in given arrival order."""
    if not jobs:
        return [], 0
    D = max(j.deadline for j in jobs)
    free = {t: m for t in range(1, D + 1)}
    t, total, done = 1, 0, []
    for job in jobs:
        while t <= D and free[t] == 0:
            t += 1
        if t <= job.deadline and t <= D:
            free[t] -= 1; total += job.profit; done.append(job)
    return done, total


def is_feasible(subset, m):
    """A set of unit jobs fits on m processors iff for every d:
    number of jobs with deadline <= d is at most m*d."""
    dl = sorted(j.deadline for j in subset)
    return all(cnt <= m * d for cnt, d in enumerate(dl, 1))


def brute_force_best(jobs, m):
    best = 0
    for r in range(len(jobs) + 1):
        for sub in combinations(jobs, r):
            if is_feasible(sub, m):
                best = max(best, sum(j.profit for j in sub))
    return best


def print_schedule(schedule, m):
    D = max(t for _, t in schedule) if schedule else 0
    print("Time slot -> " + "".join(f"{t:>6}" for t in range(1, D + 1)))
    for p in range(m):
        print(f"Processor {p + 1}  " + "".join(f"{(schedule[(p, t)].job_id if (p, t) in schedule else '-'):>6}" for t in range(1, D + 1)))


def demo():
    jobs = [Job("J1", 2, 100), Job("J2", 1, 19), Job("J3", 2, 27), Job("J4", 1, 25),
            Job("J5", 3, 15), Job("J6", 3, 60), Job("J7", 2, 40), Job("J8", 4, 35)]
    for m in (1, 2):
        print(f"\n=== {m} processor(s) ===")
        sch, rej, total = greedy_schedule(jobs, m)
        print_schedule(sch, m)
        print("Scheduled :", sorted(j.job_id for j in sch.values()))
        print("Rejected  :", sorted(j.job_id for j in rej))
        print("Total profit:", total)


def step_by_step_trace(jobs, m):
    """Execute greedy scheduling step-by-step and return a detailed execution trace.
    Useful for visualization, pedagogical demonstration, and debugging."""
    if m < 1:
        raise ValueError("need at least one processor")
    if not jobs:
        return {"steps": [], "schedule": {}, "rejected": [], "total_profit": 0, "max_time": 0}

    D = max(j.deadline for j in jobs)
    size = m * D
    parent = list(range(size))

    def find(i):
        root = i
        while root >= 0 and parent[root] != root:
            root = parent[root]
        while i >= 0 and parent[i] != root:
            parent[i], i = root, parent[i]
        return root

    sorted_jobs = sorted(jobs, key=lambda j: (-j.profit, j.deadline, j.job_id))
    schedule, rejected, total = {}, [], 0
    steps = []

    for idx, job in enumerate(sorted_jobs, 1):
        step_info = {
            "step": idx,
            "job": {"id": job.job_id, "deadline": job.deadline, "profit": job.profit},
            "target_max_slot": min(job.deadline, D) * m - 1,
        }
        if job.deadline < 1:
            rejected.append(job)
            step_info["status"] = "rejected"
            step_info["reason"] = "Deadline < 1"
        else:
            slot = find(min(job.deadline, D) * m - 1)
            step_info["found_slot"] = slot
            if slot < 0:
                rejected.append(job)
                step_info["status"] = "rejected"
                step_info["reason"] = "All slots up to deadline are occupied"
            else:
                proc = slot % m
                time_slot = slot // m + 1
                schedule[(proc, time_slot)] = job
                total += job.profit
                parent[slot] = slot - 1
                step_info["status"] = "scheduled"
                step_info["processor"] = proc + 1
                step_info["time_slot"] = time_slot
                step_info["current_total"] = total
        steps.append(step_info)

    return {
        "steps": steps,
        "schedule": {f"{p},{t}": j for (p, t), j in schedule.items()},
        "rejected": rejected,
        "total_profit": total,
        "max_time": D
    }


def verify(trials=300):
    random.seed(1)
    for _ in range(trials):
        n, m = random.randint(1, 10), random.randint(1, 3)
        jobs = [Job(f"J{i}", random.randint(1, 5), random.randint(1, 100)) for i in range(n)]
        sch, rej, total = greedy_schedule(jobs, m)
        assert all(j.deadline >= t for (_, t), j in sch.items()), "deadline violated"
        assert len(sch) + len(rej) == n and len(set(sch)) == len(sch)
        assert total == brute_force_best(jobs, m), "greedy not optimal!"
    print(f"Verification passed: greedy profit == brute-force optimum on {trials} random instances.")


def _cli_main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help", "help"):
        print("Usage: python scheduler.py [demo | verify [num_trials]]")
        print("  demo             Run standard 8-job demonstration (default)")
        print("  verify [trials]  Run randomized equivalence check against brute force (default: 300)")
        sys.exit(0)

    cmd = sys.argv[1] if len(sys.argv) > 1 else "demo"
    if cmd == "demo":
        demo()
    elif cmd == "verify":
        trials = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        verify(trials)
    else:
        print(f"Unknown command: '{cmd}'. Available: 'demo', 'verify [trials]'.")
        print("Run with --help for details or run 'python main.py' for full CLI.")
        sys.exit(1)


if __name__ == "__main__":
    _cli_main()
