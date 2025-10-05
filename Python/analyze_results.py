# Python 3.13.4

import csv
import statistics
from pathlib import Path
from collections import defaultdict
from typing import Any

OUTPUT_DIR: Path = Path("output/experiments")
ANALYSIS_DIR: Path = Path("output/analysis")
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# Analyze and print constructive method results
def analyze_constructive() -> None:
    csv_file: Path = OUTPUT_DIR / "constructive.csv"
    
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        results: list[dict[str, str]] = list(reader)
    
    # Group by method
    by_method: dict[str, list[dict[str, float]]] = defaultdict(list)
    for row in results:
        key: str = row['method']
        by_method[key].append({
            "benefit": int(row["benefit"]),
            "time": float(row["time"])
        })
    
    # Compute and print statistics
    print("="*50)
    print("CONSTRUCTIVE METHODS ANALYSIS")
    print("="*50)
    print(f"{'Method':<60} {'Best':>10} {'Avg Benefit':>12} {'Std Dev':>10} {'Avg Time':>10}")
    print("-"*50)
    
    for method, runs in sorted(by_method.items()):
        
        # VERIFY ! benefits should allways be int
        benefits: list[float] = [r["benefit"] for r in runs]
        
        times: list[float] = [r["time"] for r in runs]
        
        best_benefit: int = int(max(benefits))
        avg_benefit: float = statistics.mean(benefits)
        std_benefit: float = statistics.stdev(benefits) if len(benefits) > 1 else 0.0
        avg_time: float = statistics.mean(times)
        
        print(f"{method:<60} {best_benefit:>10} {avg_benefit:>12.2f} {std_benefit:>10.2f} {avg_time:>10.6f}s")
    
    print("="*50 + "\n")

# Analyze and print local search results
def analyze_local_search() -> None:
    csv_file: Path = OUTPUT_DIR / "local_search.csv"
    
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        results: list[dict[str, str]] = list(reader)
    
    # Group by configuration
    by_config: dict[str, list[dict[str, float]]] = defaultdict(list)
    for row in results:
        key: str = f"{row['ls_method']} | {row['refinement_heuristics']} | {row['neighborhoods']}"
        by_config[key].append({
            "final": int(row["final_benefit"]),
            "improvement_pct": float(row["improvement_pct"]),
            "time": float(row["time"])
        })
    
    # Compute and print statistics
    print("="*50)
    print("LOCAL SEARCH ANALYSIS")
    print("="*50)
    print(f"{'Local Search Method':<30} {'Refinement':<30} {'Neighborhoods':<20} {'Best':>8} {'Avg':>8} {'Std':>8} {'Time':>8}")
    print("-"*50)
    
    for config, runs in sorted(by_config.items()):
        # Split the key back into parts
        parts = config.split(" | ")
        ls_method = parts[0]
        refinement = parts[1].replace("['", "").replace("']", "").replace("', '", ",")
        neighborhoods = parts[2].replace("['", "").replace("']", "").replace("', '", ",")
        
        finals: list[float] = [r["final"] for r in runs]
        times: list[float] = [r["time"] for r in runs]
        
        best_final: int = int(max(finals))
        avg_final: float = statistics.mean(finals)
        std_final: float = statistics.stdev(finals)
        avg_time: float = statistics.mean(times)
        
        print(f"{ls_method:<30} {refinement:<30} {neighborhoods:<20} {best_final:>8} {avg_final:>8.1f} {std_final:>8.1f} {avg_time:>8.2f}s")
    
    print("="*50 + "\n")
