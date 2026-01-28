import time
import random
import pandas as pd
from collections import deque

AUSTRALIA = {
    "WA": {"NT", "SA"},
    "NT": {"WA", "SA", "Q"},
    "SA": {"WA", "NT", "Q", "NSW", "V"},
    "Q": {"NT", "SA", "NSW"},
    "NSW": {"Q", "SA", "V"},
    "V": {"SA", "NSW"},
    "T": set()
}

USA = {
    "WA": {"OR", "ID"},
    "OR": {"WA", "ID", "NV", "CA"},
    "CA": {"OR", "NV", "AZ"},
    "ID": {"WA", "OR", "NV", "UT", "WY", "MT"},
    "NV": {"OR", "ID", "UT", "AZ", "CA"},
    "UT": {"ID", "WY", "CO", "AZ", "NV", "NM"},
    "AZ": {"CA", "NV", "UT", "CO", "NM"},
    "MT": {"ID", "WY", "SD", "ND"},
    "WY": {"MT", "ID", "UT", "CO", "SD", "NE"},
    "CO": {"WY", "UT", "AZ", "NM", "OK", "KS", "NE"},
    "NM": {"AZ", "UT", "CO", "OK", "TX"},
    "ND": {"MT", "SD", "MN"},
    "SD": {"ND", "MT", "WY", "NE", "IA", "MN"},
    "NE": {"SD", "WY", "CO", "KS", "MO", "IA"},
    "KS": {"NE", "CO", "OK", "MO"},
    "OK": {"CO", "NM", "TX", "AR", "MO", "KS"},
    "TX": {"NM", "OK", "AR", "LA"},
    "MN": {"ND", "SD", "IA", "WI"},
    "IA": {"MN", "SD", "NE", "MO", "IL", "WI"},
    "MO": {"IA", "NE", "KS", "OK", "AR", "TN", "KY", "IL"},
    "AR": {"MO", "OK", "TX", "LA", "MS", "TN"},
    "LA": {"TX", "AR", "MS"},
    "WI": {"MN", "IA", "IL", "MI"},
    "IL": {"WI", "IA", "MO", "KY", "IN", "MI"},
    "KY": {"IL", "MO", "TN", "VA", "WV", "OH", "IN"},
    "TN": {"KY", "MO", "AR", "MS", "AL", "GA", "NC", "VA"},
    "MS": {"TN", "AR", "LA", "AL"},
    "MI": {"WI", "IN", "OH"},
    "IN": {"IL", "KY", "OH", "MI"},
    "OH": {"IN", "KY", "WV", "PA", "MI"},
    "WV": {"OH", "PA", "MD", "VA", "KY"},
    "VA": {"KY", "WV", "MD", "DC", "NC", "TN"},
    "NC": {"VA", "TN", "GA", "SC"},
    "SC": {"NC", "GA"},
    "GA": {"TN", "NC", "SC", "FL", "AL"},
    "AL": {"TN", "MS", "FL", "GA"},
    "FL": {"GA", "AL"},
    "PA": {"OH", "WV", "MD", "DE", "NJ", "NY"},
    "NY": {"PA", "NJ", "CT", "MA", "VT"},
    "VT": {"NY", "NH", "MA"},
    "NH": {"VT", "ME", "MA"},
    "ME": {"NH"},
    "MA": {"NY", "VT", "NH", "RI", "CT"},
    "CT": {"NY", "MA", "RI"},
    "RI": {"CT", "MA"},
    "NJ": {"PA", "DE", "NY"},
    "DE": {"MD", "PA", "NJ"},
    "MD": {"PA", "DE", "VA", "WV", "DC"},
    "DC": {"MD", "VA"}
}

def symmetrize(adj):
    for u, nbrs in list(adj.items()):
        for v in nbrs:
            adj.setdefault(v, set()).add(u)
symmetrize(AUSTRALIA)
symmetrize(USA)

def consistent(var, val, assignment, adj):
    return all(assignment.get(n) != val for n in adj[var])

def forward_check(var, val, domains, adj):
    pruned = []
    for n in adj[var]:
        if val in domains[n]:
            domains[n].remove(val)
            pruned.append((n, val))
            if not domains[n]:
                return False, pruned
    return True, pruned

def singleton_propagation(domains, adj):
    q = deque([v for v in domains if len(domains[v]) == 1])
    pruned = []
    while q:
        v = q.popleft()
        if len(domains[v]) != 1:
            continue
        val = next(iter(domains[v]))
        for n in adj[v]:
            if val in domains[n]:
                domains[n].remove(val)
                pruned.append((n, val))
                if not domains[n]:
                    return False, pruned
                if len(domains[n]) == 1:
                    q.append(n)
    return True, pruned

def select_mrv_degree(domains, adj, assignment):
    unassigned = [v for v in domains if v not in assignment]
    m = min(len(domains[v]) for v in unassigned)
    candidates = [v for v in unassigned if len(domains[v]) == m]
    candidates.sort(key=lambda v: -len(adj[v]))
    return candidates[0]

def least_constraining_values(var, domains, adj, assignment):
    values = list(domains[var])
    scores = []
    for val in values:
        elim = sum(1 for n in adj[var] if n not in assignment and val in domains[n])
        scores.append((elim, val))
    scores.sort()
    return [v for _, v in scores]

def backtracking(adj, k, algo="DFS", heuristics=False, var_order=None, time_limit=5.0):
    vars_ = list(adj.keys())
    domains = {v: set(range(k)) for v in vars_}
    assign = {}
    backtracks = 0
    start = time.perf_counter()
    order = var_order or vars_

    def bt():
        nonlocal backtracks, domains
        if len(assign) == len(vars_):
            return True
        if time.perf_counter() - start > time_limit:
            return False
        var = select_mrv_degree(domains, adj, assign) if heuristics else next(v for v in order if v not in assign)
        values = least_constraining_values(var, domains, adj, assign) if heuristics else list(domains[var])
        if not heuristics:
            random.shuffle(values)
        for val in values:
            if consistent(var, val, assign, adj):
                assign[var] = val
                snapshot = {v: set(domains[v]) for v in vars_}
                ok = True
                if algo in ("DFS+FC", "DFS+FC+SP"):
                    ok, _ = forward_check(var, val, domains, adj)
                    if ok and algo == "DFS+FC+SP":
                        ok, _ = singleton_propagation(domains, adj)
                if ok and bt():
                    return True
                assign.pop(var)
                domains = snapshot
                backtracks += 1
        return False

    success = bt()
    elapsed = round(time.perf_counter() - start, 4)
    return success, assign, backtracks, elapsed

def find_chromatic_number(adj, heuristics=True):
    for k in range(1, 6):
        ok, _, _, _ = backtracking(adj, k, "DFS+FC+SP", heuristics)
        if ok:
            return k
    return None

def run_experiments(adj, name, trials=5):
    results = []
    chrom = find_chromatic_number(adj)
    print(f"\n🔹 Chromatic Number for {name}: {chrom}")
    for heur in [False, True]:
        print(f"   {'With' if heur else 'Without'} Heuristics:")
        for algo in ["DFS", "DFS+FC", "DFS+FC+SP"]:
            for t in range(trials):
                order = None
                if not heur:
                    order = list(adj.keys())
                    random.shuffle(order)
                ok, _, bt, tm = backtracking(adj, chrom, algo, heuristics=heur, var_order=order)
                print(f"     → {algo} | Trial {t+1} | Backtracks: {bt:<5} | Time: {tm:.4f}s")
                results.append({
                    "Map": name,
                    "Chromatic #": chrom,
                    "Heuristics": "Yes" if heur else "No",
                    "Algorithm": algo,
                    "Trial": t + 1,
                    "Backtracks": bt,
                    "Time (s)": tm
                })
    return pd.DataFrame(results)

print("Running full map coloring experiments... please wait ⏳")

chrom_australia = find_chromatic_number(AUSTRALIA)
chrom_usa = find_chromatic_number(USA)
print("==========================================")
print(f"Australia Map → {chrom_australia} colors required ")
print(f"USA (Lower 48 States) → {chrom_usa} colors required ")
print("==========================================\n")

aus = run_experiments(AUSTRALIA, "Australia", trials=5)
usa = run_experiments(USA, "USA (Lower 48)", trials=5)
all_results = pd.concat([aus, usa], ignore_index=True)

summary = all_results.groupby(["Map", "Heuristics", "Algorithm"]).agg(
    Chromatic_Number=("Chromatic #", "first"),
    Avg_Backtracks=("Backtracks", "mean"),
    Avg_Time_s=("Time (s)", "mean")
).reset_index()

print("\n\n===============================")
print("📊 FULL DETAILED RESULTS TABLE")
print("===============================")
print(all_results.to_string(index=False))

print("\n\n===============================")
print("📈 SUMMARY TABLE (AVERAGES)")
print("===============================")
print(summary.to_string(index=False, float_format="%.3f"))

# Save outputs
all_results.to_csv("map_coloring_results.csv", index=False)
summary.to_csv("map_coloring_summary.csv", index=False)

print("\n All experiments completed successfully.")

