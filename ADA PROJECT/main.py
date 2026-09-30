"""
Master Entry Point: Cloud Computing Job Scheduler
=================================================
Analysis and Design of Algorithms (ADA) Project
Greedy Job Sequencing with Deadlines on Identical Processors via Disjoint Set Union (DSU).

Usage:
    python main.py                    # Interactive menu
    python main.py --demo             # Standard demonstration
    python main.py --verify [N]       # Verify optimality against brute-force (default 300)
    python main.py --experiments      # Run benchmarks & generate plots
    python main.py --web              # Launch web GUI dashboard
    python main.py --test             # Run pytest test suite
    python main.py --interactive      # Interactive CLI scheduler
"""

import sys
import os
import argparse
import subprocess
import webbrowser
import json

from backend.scheduler import (
    Job,
    greedy_schedule,
    naive_edf_schedule,
    fcfs_schedule,
    print_schedule,
    demo,
    verify
)
from backend.experiments import run_all_experiments


def interactive_cli():
    print("\n" + "=" * 60)
    print("           INTERACTIVE JOB SCHEDULER (CLI)")
    print("=" * 60)

    try:
        m_input = input("Enter number of identical processors / VMs (e.g. 2): ").strip()
        m = int(m_input) if m_input else 2
        if m < 1:
            print("Processor count must be >= 1. Defaulting to 1.")
            m = 1
    except ValueError:
        print("Invalid number. Defaulting to 2.")
        m = 2

    print("\nEnter jobs in the format:  JOB_ID DEADLINE PROFIT")
    print("Example:  J1 2 100")
    print("Type 'done' or press Enter on an empty line when finished.")
    print("Type 'preset' to load the standard 8-job demo workload.\n")

    jobs = []
    idx = 1
    while True:
        line = input(f"Job #{idx} > ").strip()
        if not line or line.lower() == "done":
            break
        if line.lower() == "preset":
            jobs = [
                Job("J1", 2, 100), Job("J2", 1, 19), Job("J3", 2, 27), Job("J4", 1, 25),
                Job("J5", 3, 15), Job("J6", 3, 60), Job("J7", 2, 40), Job("J8", 4, 35)
            ]
            print(f"Loaded {len(jobs)} preset jobs.")
            break

        parts = line.split()
        if len(parts) == 3:
            jid, d_str, p_str = parts
            try:
                d = int(d_str)
                p = int(p_str)
                jobs.append(Job(jid, d, p))
                idx += 1
            except ValueError:
                print("Error: Deadline and profit must be integers. Try again.")
        else:
            print("Error: Expected 3 space-separated tokens: JOB_ID DEADLINE PROFIT")

    if not jobs:
        print("No jobs provided. Exiting interactive scheduler.")
        return

    print(f"\nScheduling {len(jobs)} jobs on {m} processor(s)...")
    sch, rej, total = greedy_schedule(jobs, m)
    edf_done, edf_total = naive_edf_schedule(jobs, m)
    fcfs_done, fcfs_total = fcfs_schedule(jobs, m)

    print("\n--- GREEDY (DSU) SCHEDULE ---")
    print_schedule(sch, m)
    print("\nScheduled Jobs :", sorted(j.job_id for j in sch.values()))
    print("Rejected Jobs  :", sorted(j.job_id for j in rej))
    print(f"Total Profit   : ${total}")

    print("\n--- BASELINE COMPARISON ---")
    print(f"Greedy (DSU)              : ${total} (Optimal)")
    print(f"Earliest Deadline First   : ${edf_total} ({len(edf_done)} jobs)")
    print(f"First-Come First-Served   : ${fcfs_total} ({len(fcfs_done)} jobs)")
    if edf_total > 0:
        gain = ((total - edf_total) / edf_total) * 100
        print(f"Greedy profit advantage vs EDF : +{gain:.1f}%")
    if fcfs_total > 0:
        gain = ((total - fcfs_total) / fcfs_total) * 100
        print(f"Greedy profit advantage vs FCFS: +{gain:.1f}%")
    print("=" * 60 + "\n")


def run_experiments_script():
    print("\nRunning benchmark experiments suite (this tests scaling up to 500,000 jobs)...")
    run_all_experiments()
    print("\nExperiments complete! Generated:")
    print("  - profit.png   (Average profit comparison bar chart)")
    print("  - gantt.png    (Gantt timeline visualization)")
    print("  - results.json (Empirical runtime scaling & profit data)")


def run_tests():
    print("\nRunning automated unit tests with pytest...")
    subprocess.run([sys.executable, "-m", "pytest", "-v"], check=False)


def launch_web(host="127.0.0.1", port=8000, open_browser=True):
    import uvicorn
    url = f"http://{host}:{port}"
    print("\n" + "=" * 60)
    print(f"  Launching Cloud Computing Job Scheduler Web Dashboard")
    print(f"  URL: {url}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 60 + "\n")

    if open_browser:
        def open_tab():
            import time
            time.sleep(1.2)
            webbrowser.open(url)
        import threading
        threading.Thread(target=open_tab, daemon=True).start()

    uvicorn.run("backend.app:app", host=host, port=port, reload=False)


def schedule_from_file(filepath, m):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return
    with open(filepath, "r") as f:
        data = json.load(f)
    jobs = [Job(item["job_id"], item["deadline"], item["profit"]) for item in data]
    print(f"Loaded {len(jobs)} jobs from {filepath}. Scheduling on {m} processor(s)...")
    sch, rej, total = greedy_schedule(jobs, m)
    print_schedule(sch, m)
    print(f"Total Profit: ${total}")


def main_menu():
    while True:
        print("\n" + "=" * 68)
        print("    CLOUD COMPUTING JOB SCHEDULER (GREEDY WITH DSU & DEADLINES)")
        print("=" * 68)
        print("  [1] Run Standard Demo (8 jobs on 1 & 2 processors)")
        print("  [2] Interactive CLI Scheduler (Custom jobs & comparison)")
        print("  [3] Verify Correctness (Greedy vs Brute Force on 300 tests)")
        print("  [4] Run Performance Benchmarks (Generate charts & JSON)")
        print("  [5] Launch Interactive Web Dashboard (FastAPI GUI)")
        print("  [6] Run Automated Unit Tests (pytest)")
        print("  [0] Exit")
        print("-" * 68)

        choice = input("Select an option (0-6): ").strip()
        if choice == "1":
            demo()
        elif choice == "2":
            interactive_cli()
        elif choice == "3":
            verify(300)
        elif choice == "4":
            run_experiments_script()
        elif choice == "5":
            launch_web()
            break
        elif choice == "6":
            run_tests()
        elif choice in ("0", "q", "exit"):
            print("Exiting. Have a great day!")
            break
        else:
            print("Invalid selection. Please choose an option from 0 to 6.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloud Computing Multi-Processor Job Scheduler (Greedy DSU)")
    parser.add_argument("--demo", action="store_true", help="Run standard 8-job demonstration")
    parser.add_argument("--verify", nargs="?", const=300, type=int, help="Verify optimality against brute-force (default: 300 trials)")
    parser.add_argument("--experiments", action="store_true", help="Run benchmarks and generate plots")
    parser.add_argument("--web", action="store_true", help="Launch interactive web GUI dashboard")
    parser.add_argument("--port", type=int, default=8000, help="Web server port (default 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser when launching web GUI")
    parser.add_argument("--test", action="store_true", help="Run pytest unit test suite")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive CLI scheduler")
    parser.add_argument("--file", type=str, help="Path to JSON file containing jobs list")
    parser.add_argument("-m", "--processors", type=int, default=2, help="Number of processors when using --file (default: 2)")

    args = parser.parse_args()

    if args.demo:
        demo()
    elif args.verify is not None:
        verify(args.verify)
    elif args.experiments:
        run_experiments_script()
    elif args.web:
        launch_web(port=args.port, open_browser=not args.no_browser)
    elif args.test:
        run_tests()
    elif args.interactive:
        interactive_cli()
    elif args.file:
        schedule_from_file(args.file, args.processors)
    else:
        main_menu()
