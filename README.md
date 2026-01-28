# Map Coloring Using Constraint Satisfaction Problems (CSP)

This project implements the classic **Map Coloring Problem** using **Constraint Satisfaction Problem (CSP)** techniques in Python. The goal is to assign colors to regions such that no two adjacent regions share the same color, while minimizing the total number of colors used.

The project evaluates multiple CSP strategies and heuristics on two real-world maps:

- Australia  
- USA (Lower 48 States)

---

## 🚀 Features

- Depth-First Search (DFS) Backtracking
- Forward Checking (FC)
- Singleton Domain Propagation (SP)
- Heuristics:
  - Minimum Remaining Values (MRV)
  - Degree Heuristic
  - Least Constraining Value (LCV)
- Automatic chromatic number detection
- Multiple experimental trials
- Performance comparison using:
  - Backtracking count
  - Execution time
- Results exported to CSV files

---

## 🧠 Algorithms Implemented

1. **DFS** – Basic backtracking search  
2. **DFS + Forward Checking** – Prunes inconsistent values early  
3. **DFS + Forward Checking + Singleton Propagation** – Further reduces domains using forced assignments  

Each algorithm is tested both **with and without heuristics**.

---
## 📸 Screenshots

### 🔹 Program Execution & Results
![Screenshot 1](1.png)

### 🔹 Summary Table Output
![Screenshot 2](2.png)

## 🗺 Maps Used

- Australia (7 regions)
- USA Lower 48 States

Adjacency relationships are defined directly in the code.

---

## 📊 Output Files

After execution, the following files are generated:

- `map_coloring_results.csv` – Detailed trial results  
- `map_coloring_summary.csv` – Average backtracks and time per algorithm  

---

## ▶️ How to Run

### Requirements

Make sure Python is installed, then install dependencies:

```bash
pip install pandas
