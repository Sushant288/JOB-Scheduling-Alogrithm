# Cloud Computing Job Scheduler
### Greedy Job Sequencing with Deadlines on $m$ Identical Processors via Disjoint Set Union (DSU)
*Analysis and Design of Algorithms (ADA) Project*

---

## 📌 Problem Formulation

In a cloud computing cluster with $m$ identical virtual machines (processors):
- Each job $j_i$ takes **1 unit of processor time**.
- Each job has a **deadline** $d_i$ (latest time slot by which it must finish).
- Each job yields an **earned profit** $p_i$ if completed by its deadline, and $0$ otherwise.
- At most one job can run on processor $k$ during time slot $[t-1, t]$.

**Objective:** Maximize the total earned profit across all processors:
$$\max \sum_{j \in S} p_j \quad \text{subject to } S \text{ being feasible on } m \text{ processors.}$$

---

## 💡 Algorithmic Strategy & The DSU Trick

1. **Greedy Choice**: Sort all jobs by profit in descending order ($p_1 \ge p_2 \ge \dots \ge p_n$).
2. **Optimal Placement**: Place each job into the **latest available time slot** $\le d_i$ across any of the $m$ processors. This frees up earlier slots for subsequent jobs with tighter deadlines.
3. **The DSU "Unrolling" Trick**:
   - The 2D timeline ($m$ processors $\times D$ time slots) is unrolled into a 1D discrete array of $m \times D$ slots:
     $$\text{Flattened Index } i \implies \text{Time Slot } t = \lfloor i / m \rfloor + 1, \quad \text{Processor } p = i \bmod m$$
   - The latest slot for deadline $d$ is at index $(d \cdot m - 1)$.
   - A **Disjoint Set Union (DSU)** structure with path compression tracks the latest available slot $\le i$ in near $O(1)$ amortized time ($\alpha(mD)$).
   - Once a slot is occupied, its pointer merges into slot $- 1$.

### Theoretical Complexity Comparison
| Strategy | Time Complexity | Space Complexity | Optimality Guarantee |
| :--- | :--- | :--- | :--- |
| **Greedy + DSU (This Project)** | **$O(n \log n + m \cdot D)$** | **$O(m \cdot D)$** | **Guaranteed Optimal** (Matroid Theory) |
| Naive Greedy (Linear Search) | $O(n \log n + n \cdot D)$ | $O(m \cdot D)$ | Guaranteed Optimal |
| Earliest Deadline First (EDF) | $O(n \log n)$ | $O(m \cdot D)$ | Suboptimal (ignores profit) |
| First-Come First-Served (FCFS) | $O(n)$ | $O(m \cdot D)$ | Suboptimal (no optimization) |
| Brute Force | $O(2^n \cdot n \log n)$ | $O(n)$ | Optimal (intractable for $n > 20$) |

---

## 🚀 Quickstart Guide

### 1. Prerequisites & Installation
Ensure Python 3.8+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Running the Interactive Application Menu
Simply run:
```bash
python main.py
```
Or on Windows, double-click **`run.bat`**.

You will be greeted with an interactive CLI menu:
```text
====================================================================
    CLOUD COMPUTING JOB SCHEDULER (GREEDY WITH DSU & DEADLINES)
====================================================================
  [1] Run Standard Demo (8 jobs on 1 & 2 processors)
  [2] Interactive CLI Scheduler (Custom jobs & comparison)
  [3] Verify Correctness (Greedy vs Brute Force on 300 tests)
  [4] Run Performance Benchmarks (Generate charts & JSON)
  [5] Launch Interactive Web Dashboard (FastAPI GUI)
  [6] Run Automated Unit Tests (pytest)
  [0] Exit
--------------------------------------------------------------------
```

---

## 💻 CLI Commands & Direct Flags

You can invoke any mode directly using command-line arguments:

```bash
# 1. Run standard demonstration (8 jobs on 1 & 2 processors)
python main.py --demo

# 2. Launch interactive web dashboard GUI
python main.py --web

# 3. Verify optimality against brute-force (300 random test instances)
python main.py --verify 300

# 4. Run performance benchmark experiments & generate plots
python main.py --experiments

# 5. Run automated unit test suite
python main.py --test

# 6. Interactive terminal scheduler
python main.py --interactive

# 7. Schedule jobs from a JSON file
python main.py --file sample_jobs.json -m 2
```

You can also run individual modules directly:
```bash
python scheduler.py demo
python scheduler.py verify 500
python experiments.py
pytest -v
```

---

## 🌐 Interactive Web GUI Dashboard

Launch the browser-based dashboard with:
```bash
python main.py --web
```
Or with Uvicorn:
```bash
uvicorn app:app --port 8000
```
Then visit **`http://127.0.0.1:8000`** in your browser.

### Key Features of the Web Dashboard:
1. **Interactive Gantt Timeline**: Visualizes job allocations across $m$ processors with color coding, profit badges, and hover tooltips.
2. **Step-by-Step DSU Tracer**: Step through the Greedy algorithm one job at a time. Watch the DSU find and path compression operations in real time!
3. **Multi-Algorithm Comparison**: Compares Greedy total profit against Earliest Deadline First (EDF) and First-Come First-Served (FCFS).
4. **Preset & Random Workloads**: Test the textbook 8-job instance, high-contention burst loads, or generate custom synthetic workloads.
5. **Benchmark Analytics**: Inspect live runtime scaling curves ($n = 1,000$ to $500,000$ jobs) and profit distribution charts.

---

## 📊 Experimental Results & Empirical Verification

Ran 40 independent random workloads (200 jobs each) across different processor counts:
- **Profit Advantage**: Greedy achieves **+46% to +70% higher profit** compared to EDF and FCFS baselines.
- **Runtime Scaling**:
  - $n = 1,000$ jobs: ~0.0008 seconds
  - $n = 10,000$ jobs: ~0.015 seconds
  - $n = 100,000$ jobs: ~0.33 seconds
  - $n = 500,000$ jobs: ~1.74 seconds
  - Scales near-linearly $O(n \log n)$ up to 500,000 jobs!

---

## 📂 Project Architecture

```text
ADA PROJECT/
│
├── main.py              # Master entry point (Interactive menu + CLI flags)
├── sample_jobs.json     # Sample input workload for file-based runs
├── requirements.txt     # Python package dependencies
├── pytest.ini           # Pytest test discovery config
├── run.bat              # One-click Windows launcher
├── README.md            # Comprehensive project documentation
│
├── backend/             # Core Backend Modules
│   ├── __init__.py      # Backend package definition
│   ├── scheduler.py     # Core Greedy DSU scheduler, EDF, FCFS, Brute Force & Verification
│   ├── app.py           # FastAPI backend serving REST APIs and dashboard
│   └── experiments.py   # Empirical benchmark experiments & chart generation
│
├── static/              # Frontend Web UI
│   └── index.html       # Modern responsive glassmorphic Web Dashboard
│
├── tests/               # Test Suite
│   ├── conftest.py      # Pytest environment setup
│   └── test_scheduler.py# Automated unit test suite (pytest)
│
└── [Generated Artifacts]
    ├── profit.png       # Profit comparison chart across 40 workloads
    ├── gantt.png        # Generated Gantt chart
    └── results.json     # Benchmark metrics data
```

---

## 🧪 Testing

Run all unit tests with:
```bash
python -m pytest -v
```
All tests verify:
- Empty job handling
- Valid processor boundaries
- Deadline constraint compliance ($\text{slot} \le d_i$)
- Processor non-collision (no two jobs on the same processor at the same slot)
- Equivalence between Greedy and Brute Force optimum
- Step-by-step trace consistency
