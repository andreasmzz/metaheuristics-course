# Python 3.13.4

import csv
import statistics
from pathlib import Path
from collections import defaultdict
from typing import Any

OUTPUT_DIR: Path = Path("output/experiments")
ANALYSIS_DIR: Path = Path("output/analysis")
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# Statistical terms used in this file:
# - first_quartile (Q1): the 25th percentile of the sample
# - third_quartile (Q3): the 75th percentile of the sample
# - interquartile_range (IQR): Q3 - Q1, a robust measure of spread
# We use the 1.5 * IQR rule to flag outliers: values < Q1 - 1.5*IQR or > Q3 + 1.5*IQR

# Analyze and print constructive method results
def analyze_constructive() -> None:
    csv_file: Path = OUTPUT_DIR / "constructive.csv"
    if not csv_file.exists():
        print(f"No constructive results found at {csv_file}")
        return

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
    print(f"{'Method':<60} {'Count':>6} {'Best':>10} {'Median':>8} {'Avg':>10} {'Std Dev':>10} {'IQR':>8} {'Avg Time':>10}")
    print("-"*90)

    for method, runs in sorted(by_method.items()):
        benefits: list[float] = [r["benefit"] for r in runs]
        times: list[float] = [r["time"] for r in runs]

        count: int = len(benefits)
        best_benefit: int = int(max(benefits))
        median_benefit: float = statistics.median(benefits)
        avg_benefit: float = statistics.mean(benefits)
        std_benefit: float = statistics.stdev(benefits) if len(benefits) > 1 else 0.0

        if len(benefits) >= 3:
            first_quartile = statistics.quantiles(benefits, n=4)[0]
            third_quartile = statistics.quantiles(benefits, n=4)[2]
            interquartile_range: float = third_quartile - first_quartile
        else:
            first_quartile = third_quartile = median_benefit
            interquartile_range = 0.0

        avg_time: float = statistics.mean(times) if times else 0.0

        outliers = [b for b in benefits if (b < first_quartile - 1.5 * interquartile_range) or (b > third_quartile + 1.5 * interquartile_range)] if interquartile_range > 0 else []

        print(f"{method:<60} {count:>6} {best_benefit:>10} {median_benefit:>8.0f} {avg_benefit:>10.2f} {std_benefit:>10.2f} {interquartile_range:>8.0f} {avg_time:>10.6f}s")
        if outliers:
            print(f"    Note: {len(outliers)} outlier(s) detected for {method} (examples: {outliers[:3]})")

        # Append a compact summary for later inspection
        summary_file = ANALYSIS_DIR / "constructive_summary.csv"
        header = False
        if not summary_file.exists():
            header = True
        with open(summary_file, "a") as sf:
            if header:
                sf.write("method,count,best,median,avg,std,interquartile_range,outliers\n")
            sf.write(f"{method},{count},{best_benefit},{median_benefit:.0f},{avg_benefit:.2f},{std_benefit:.2f},{interquartile_range:.2f},{len(outliers)}\n")
    
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
        avg_time: float = statistics.mean(times)

        # guard stdev for single-sample groups
        std_final: float = statistics.stdev(finals) if len(finals) > 1 else 0.0
        print(f"{ls_method:<30} {refinement:<30} {neighborhoods:<20} {best_final:>8} {avg_final:>8.1f} {std_final:>8.1f} {avg_time:>8.2f}s")
    
    print("="*50 + "\n")


#
def analyze_genetic_algorithm() -> None:
    csv_file: Path = OUTPUT_DIR / "genetic_algorithm.csv"
    if not csv_file.exists():
        print(f"No genetic_algorithm results found at {csv_file}")
        return

    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        results: list[dict[str, str]] = list(reader)

    # Group by parent selection method and population size for better breakdown
    by_config: dict[str, list[dict[str, float]]] = defaultdict(list)
    for row in results:
        # Use parent_selection and parents_per_generation as grouping key
        sel = row.get("parent_selection", "unknown")
        ppg = row.get("parents_per_generation", "")
        key: str = f"{sel} | parents={ppg}"
        by_config[key].append({
            "benefit": int(row.get("benefit", 0)),
            "time": float(row.get("time", 0.0))
        })

    # Print header
    print("="*50)
    print("GENETIC ALGORITHM ANALYSIS")
    print("="*50)
    print(f"{'Config':<50} {'Count':>6} {'Best':>10} {'Median':>8} {'Avg':>10} {'Std Dev':>10} {'IQR':>8} {'Avg Time':>10}")
    print("-"*110)

    summary_file = ANALYSIS_DIR / "genetic_algorithm_summary.csv"
    header_written = False
    if not summary_file.exists():
        header_written = True

    for config, runs in sorted(by_config.items()):
        benefits: list[float] = [r["benefit"] for r in runs]
        times: list[float] = [r["time"] for r in runs]

        count: int = len(benefits)
        best_benefit: int = int(max(benefits)) if benefits else 0
        median_benefit: float = statistics.median(benefits) if benefits else 0.0
        avg_benefit: float = statistics.mean(benefits) if benefits else 0.0
        std_benefit: float = statistics.stdev(benefits) if len(benefits) > 1 else 0.0

        if len(benefits) >= 3:
            first_quartile = statistics.quantiles(benefits, n=4)[0]
            third_quartile = statistics.quantiles(benefits, n=4)[2]
            interquartile_range: float = third_quartile - first_quartile
        else:
            first_quartile = third_quartile = median_benefit
            interquartile_range = 0.0

        avg_time: float = statistics.mean(times) if times else 0.0

        outliers = [b for b in benefits if (b < first_quartile - 1.5 * interquartile_range) or (b > third_quartile + 1.5 * interquartile_range)] if interquartile_range > 0 else []

        print(f"{config:<50} {count:>6} {best_benefit:>10} {median_benefit:>8.0f} {avg_benefit:>10.2f} {std_benefit:>10.2f} {interquartile_range:>8.0f} {avg_time:>10.6f}s")
        if outliers:
            print(f"    Note: {len(outliers)} outlier(s) detected for {config} (examples: {outliers[:3]})")

        # append summary
        with open(summary_file, "a") as sf:
            if header_written:
                sf.write("config,count,best,median,avg,std,interquartile_range,outliers\n")
                header_written = False
            sf.write(f"{config},{count},{best_benefit},{median_benefit:.0f},{avg_benefit:.2f},{std_benefit:.2f},{interquartile_range:.2f},{len(outliers)}\n")

    print("="*50 + "\n")



