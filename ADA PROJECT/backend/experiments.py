"""
Benchmark Experiments Suite
===========================
Runs empirical performance scaling tests and baseline profit comparisons.
Generates:
  - results.json (metrics)
  - gantt.png (Gantt chart visualization)
  - profit.png (Profit comparison bar chart)
"""

import os
import random
import time
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    from .scheduler import (
        Job,
        greedy_schedule,
        naive_edf_schedule,
        fcfs_schedule,
    )
except ImportError:
    from scheduler import (
        Job,
        greedy_schedule,
        naive_edf_schedule,
        fcfs_schedule,
    )

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_all_experiments(output_dir=PROJECT_ROOT):
    random.seed(7)
    print("Running Experiment 1: Average Profit Comparison across workloads...")
    res = {}
    for m in (1, 2, 4, 8):
        g = e = f = 0
        T = 40
        for _ in range(T):
            n = 200
            D = max(5, n // (2 * m))
            jobs = [Job(f"J{i}", random.randint(1, D), random.randint(10, 500)) for i in range(n)]
            g += greedy_schedule(jobs, m)[2]
            e += naive_edf_schedule(jobs, m)[1]
            f += fcfs_schedule(jobs, m)[1]
        res[m] = (g / T, e / T, f / T)

    print("Running Experiment 2: DSU Runtime Scaling up to 500,000 jobs...")
    rt = {}
    for n in (1000, 10000, 100000, 500000):
        jobs = [Job(f"J{i}", random.randint(1, n // 4), random.randint(1, 1000)) for i in range(n)]
        t = time.perf_counter()
        greedy_schedule(jobs, 4)
        rt[n] = time.perf_counter() - t

    # Save results.json
    results_file = os.path.join(output_dir, "results.json")
    with open(results_file, "w") as fp:
        json.dump({"profit": res, "runtime": rt}, fp)
    print(f"Saved: {results_file}")
    print("Profit Comparison:", res)
    print("Runtime Scaling:", rt)

    print("Generating Experiment 3: Demo Gantt Chart Plot...")
    jobs = [
        Job("J1", 2, 100), Job("J2", 1, 19), Job("J3", 2, 27), Job("J4", 1, 25),
        Job("J5", 3, 15), Job("J6", 3, 60), Job("J7", 2, 40), Job("J8", 4, 35)
    ]
    sch, rej, tot = greedy_schedule(jobs, 2)
    fig, ax = plt.subplots(figsize=(6.4, 2.4))
    cm = plt.get_cmap("Set3")
    for (p, t), j in sch.items():
        ax.barh(p, 1, left=t - 1, color=cm(int(j.job_id[1:]) % 12), edgecolor="k")
        ax.text(t - 0.5, p, f"{j.job_id}\n${j.profit}", ha="center", va="center", fontsize=8)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Processor 1", "Processor 2"])
    ax.set_xticks(range(0, 5))
    ax.set_xlabel("Time (unit slots)")
    ax.set_ylim(-0.6, 1.6)
    ax.set_title(f"Greedy schedule on 2 processors - total profit {tot}", fontsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    gantt_path = os.path.join(output_dir, "gantt.png")
    fig.savefig(gantt_path, dpi=200)
    plt.close(fig)
    print(f"Saved: {gantt_path}")

    print("Generating Experiment 4: Average Profit Comparison Bar Chart...")
    fig, ax = plt.subplots(figsize=(6.4, 3))
    x = np.arange(4)
    w = 0.26
    for i, (l, c) in enumerate([
        ("Greedy (by profit)", "#117a8b"),
        ("Earliest deadline first", "#e67e22"),
        ("First come first served", "#999999")
    ]):
        ax.bar(x + (i - 1) * w, [res[m][i] for m in res], w, label=l, color=c)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{m} processor{'s' if m > 1 else ''}" for m in res])
    ax.set_ylabel("Average total profit")
    ax.set_title("Average profit over 40 random workloads (200 jobs each)", fontsize=10)
    ax.set_ylim(0, 48000)
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper center")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    profit_path = os.path.join(output_dir, "profit.png")
    fig.savefig(profit_path, dpi=200)
    plt.close(fig)
    print(f"Saved: {profit_path}")


if __name__ == "__main__":
    run_all_experiments()
