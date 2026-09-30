"""
FastAPI Web Dashboard for Cloud Computing Job Scheduler
======================================================
Provides interactive GUI, API endpoints for scheduling, step-by-step
DSU tracing, multi-algorithm comparison, and benchmark visualization.
"""

import os
import random
import time
import json
import subprocess
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel, Field

try:
    from .scheduler import (
        Job,
        greedy_schedule,
        naive_edf_schedule,
        fcfs_schedule,
        brute_force_best,
        step_by_step_trace,
    )
except ImportError:
    from scheduler import (
        Job,
        greedy_schedule,
        naive_edf_schedule,
        fcfs_schedule,
        brute_force_best,
        step_by_step_trace,
    )

app = FastAPI(
    title="Cloud Computing Job Scheduler",
    description="Greedy Multi-Processor Job Sequencing with Deadlines and Disjoint Set Union",
    version="1.0.0"
)

# Project root directory is parent of backend/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class JobItem(BaseModel):
    job_id: str = Field(..., example="J1")
    deadline: int = Field(..., ge=1, example=2)
    profit: int = Field(..., ge=0, example=100)


class ScheduleRequest(BaseModel):
    m: int = Field(2, ge=1, le=32, description="Number of processors")
    jobs: List[JobItem]
    algorithm: Optional[str] = Field("all", description="greedy, edf, fcfs, or all")


class RandomGenRequest(BaseModel):
    num_jobs: int = Field(12, ge=1, le=100)
    max_deadline: int = Field(6, ge=1, le=30)
    max_profit: int = Field(150, ge=10, le=2000)


DEFAULT_JOBS = [
    JobItem(job_id="J1", deadline=2, profit=100),
    JobItem(job_id="J2", deadline=1, profit=19),
    JobItem(job_id="J3", deadline=2, profit=27),
    JobItem(job_id="J4", deadline=1, profit=25),
    JobItem(job_id="J5", deadline=3, profit=15),
    JobItem(job_id="J6", deadline=3, profit=60),
    JobItem(job_id="J7", deadline=2, profit=40),
    JobItem(job_id="J8", deadline=4, profit=35),
]


@app.get("/api/presets")
def get_presets():
    return {
        "textbook": {
            "name": "Standard Demo (8 Jobs)",
            "description": "Textbook 8-job multi-processor benchmark instance",
            "m": 2,
            "jobs": [j.model_dump() for j in DEFAULT_JOBS]
        },
        "contention": {
            "name": "High Deadline Contention (12 Jobs)",
            "description": "Tight deadlines (1-3) causing intense competition for early slots",
            "m": 2,
            "jobs": [
                {"job_id": f"J{i+1}", "deadline": d, "profit": p}
                for i, (d, p) in enumerate([
                    (1, 90), (1, 85), (1, 80), (1, 75),
                    (2, 120), (2, 110), (2, 95), (2, 70),
                    (3, 150), (3, 130), (3, 60), (3, 40)
                ])
            ]
        },
        "cloud_cluster": {
            "name": "Cloud Burst Cluster (20 Jobs, 4 VMs)",
            "description": "Large workload scheduled across 4 identical VMs",
            "m": 4,
            "jobs": [
                {"job_id": f"VM_Job_{i+1}", "deadline": random.Random(42 + i).randint(2, 7),
                 "profit": random.Random(100 + i).randint(20, 250)}
                for i in range(20)
            ]
        }
    }


@app.post("/api/random-jobs")
def generate_random_jobs(req: RandomGenRequest):
    jobs = []
    for i in range(req.num_jobs):
        jobs.append({
            "job_id": f"J{i+1}",
            "deadline": random.randint(1, req.max_deadline),
            "profit": random.randint(10, req.max_profit)
        })
    return {"jobs": jobs}


@app.post("/api/schedule")
def api_schedule(req: ScheduleRequest):
    core_jobs = [Job(j.job_id, j.deadline, j.profit) for j in req.jobs]
    m = req.m

    if not core_jobs:
        return {
            "m": m,
            "greedy": {"schedule": [], "rejected": [], "total_profit": 0, "max_time": 0},
            "edf": {"scheduled": [], "total_profit": 0},
            "fcfs": {"scheduled": [], "total_profit": 0},
            "comparison": {}
        }

    # 1. Greedy schedule
    sch_dict, rejected, greedy_profit = greedy_schedule(core_jobs, m)
    max_time = max(t for _, t in sch_dict) if sch_dict else max(j.deadline for j in core_jobs)

    schedule_list = []
    for (proc, time_slot), job in sch_dict.items():
        schedule_list.append({
            "processor": proc + 1,
            "time_slot": time_slot,
            "job_id": job.job_id,
            "deadline": job.deadline,
            "profit": job.profit
        })

    schedule_list.sort(key=lambda x: (x["processor"], x["time_slot"]))

    # 2. Baselines
    edf_done, edf_profit = naive_edf_schedule(core_jobs, m)
    fcfs_done, fcfs_profit = fcfs_schedule(core_jobs, m)

    # 3. Optional brute-force check if small
    brute_force_profit = None
    if len(core_jobs) <= 14:
        try:
            brute_force_profit = brute_force_best(core_jobs, m)
        except Exception:
            pass

    # Utilization
    total_slots = m * max_time if max_time > 0 else 1
    utilization_pct = round((len(schedule_list) / total_slots) * 100, 1)

    return {
        "m": m,
        "max_time": max_time,
        "greedy": {
            "schedule": schedule_list,
            "scheduled_count": len(schedule_list),
            "rejected": [{"job_id": j.job_id, "deadline": j.deadline, "profit": j.profit} for j in rejected],
            "rejected_count": len(rejected),
            "total_profit": greedy_profit,
            "utilization_pct": utilization_pct,
            "brute_force_optimal": brute_force_profit
        },
        "edf": {
            "scheduled": [{"job_id": j.job_id, "deadline": j.deadline, "profit": j.profit} for j in edf_done],
            "scheduled_count": len(edf_done),
            "total_profit": edf_profit,
            "greedy_advantage_pct": round(((greedy_profit - edf_profit) / edf_profit * 100), 1) if edf_profit > 0 else 0
        },
        "fcfs": {
            "scheduled": [{"job_id": j.job_id, "deadline": j.deadline, "profit": j.profit} for j in fcfs_done],
            "scheduled_count": len(fcfs_done),
            "total_profit": fcfs_profit,
            "greedy_advantage_pct": round(((greedy_profit - fcfs_profit) / fcfs_profit * 100), 1) if fcfs_profit > 0 else 0
        }
    }


@app.post("/api/trace")
def api_trace(req: ScheduleRequest):
    core_jobs = [Job(j.job_id, j.deadline, j.profit) for j in req.jobs]
    trace = step_by_step_trace(core_jobs, req.m)
    return trace


@app.get("/api/experiments/results")
def get_experiment_results():
    results_path = os.path.join(PROJECT_ROOT, "results.json")
    if os.path.exists(results_path):
        with open(results_path, "r") as f:
            return json.load(f)
    return {"profit": {}, "runtime": {}}


@app.get("/api/images/{img_name}")
def get_image(img_name: str):
    allowed = ["gantt.png", "profit.png"]
    if img_name not in allowed:
        raise HTTPException(status_code=404, detail="Image not found")
    path = os.path.join(PROJECT_ROOT, img_name)
    if os.path.exists(path):
        return FileResponse(path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Image not yet generated")


@app.post("/api/experiments/run")
def trigger_experiments(bg: BackgroundTasks):
    def run_exp():
        exp_script = os.path.join(os.path.dirname(__file__), "experiments.py")
        subprocess.run([sys.executable, exp_script], cwd=PROJECT_ROOT)
    bg.add_task(run_exp)
    return {"status": "Experiments job launched in background."}


@app.get("/", response_class=HTMLResponse)
def index_page():
    html_file = os.path.join(PROJECT_ROOT, "static", "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Scheduler Web UI loading... Please ensure static/index.html exists.</h1>"
