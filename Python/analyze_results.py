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


def _get_benefit_stats(benefits: list[float]) -> dict[str, Any]:
    """Helper function to calculate common statistics (Best, Median, Avg, Std Dev, IQR)."""
    count: int = len(benefits)
    if count == 0:
        return {
            "count": 0, "best": 0.0, "median": 0.0, "avg": 0.0,
            "std": 0.0, "iqr": 0.0, "outliers_count": 0
        }

    best_benefit: float = float(max(benefits))
    median_benefit: float = statistics.median(benefits)
    avg_benefit: float = statistics.mean(benefits)
    std_benefit: float = statistics.stdev(benefits) if count > 1 else 0.0

    if count >= 3:
        # Quantiles requires at least 3 data points
        quartiles = statistics.quantiles(benefits, n=4)
        first_quartile = quartiles[0]
        third_quartile = quartiles[2]
        interquartile_range: float = third_quartile - first_quartile
    else:
        first_quartile = third_quartile = median_benefit
        interquartile_range = 0.0

    # Outlier detection (1.5 * IQR rule)
    outliers = [b for b in benefits if (b < first_quartile - 1.5 * interquartile_range) or (b > third_quartile + 1.5 * interquartile_range)] if interquartile_range > 0 else []

    return {
        "count": count,
        "best": best_benefit,
        "median": median_benefit,
        "avg": avg_benefit,
        "std": std_benefit,
        "iqr": interquartile_range,
        "outliers_count": len(outliers),
        "outliers_examples": outliers[:3]
    }


def analyze_simulated_annealing() -> None:
    """
    Analyzes Simulated Annealing results grouped by instance file and configuration.
    Configuration parameters used: initial_temp, alpha, and neighborhoods.
    """
    csv_file: Path = OUTPUT_DIR / "simulated_annealing.csv"
    if not csv_file.exists():
        print(f"No Simulated Annealing results found at {csv_file}")
        return

    print("Reading Simulated Annealing results...")
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        results: list[dict[str, str]] = list(reader)

    # Group by instance file and configuration
    by_config: defaultdict[str, list[dict[str, float]]] = defaultdict(list)
    for row in results:
        # Neighborhoods are stored as a list string in the CSV, clean them up for the key
        neighborhoods = row.get('initial_sol_neighborhood', '[]').replace("['", "").replace("']", "").replace("', '", ",")
        
        key: str = (
            f"{row['instance_file']} | "

            #f"T0:{float(row['initial_temp']):.0f} | "
            #f"Alpha:{float(row['alpha']):.2f} | "
            #f"Beta:{float(row['beta']):.2f} | "
            #f"Gamma:{float(row['gamma']):.2f} | "
            #f"Run Finding Initial Temp:{bool(row['run_finding_initial_temp'])} | "
            f"Initial temp:{float(row['initial_temp']):.6f} | "
            #f"Nbs:{neighborhoods} | "
        )
        by_config[key].append({
            "benefit": int(row["benefit"]),
            "time": float(row["time"])
        })

    # Compute and print statistics
    print("\n" + "="*80)
    print("SIMULATED ANNEALING ANALYSIS (Grouped by Instance and Configuration)")
    print("="*80)
    header_format: str = (
        f"{'Instance & Config':<60} {'Count':>6} {'Best':>10} {'Median':>8} {'Avg':>10} "
        f"{'Std Dev':>10} {'IQR':>8} {'Avg Time':>10}"
    )
    print(header_format)
    print("-"*120)

    summary_data: list[dict[str, Any]] = []

    for config, runs in sorted(by_config.items()):
        benefits: list[float] = [float(r["benefit"]) for r in runs]
        times: list[float] = [r["time"] for r in runs]

        stats = _get_benefit_stats(benefits)
        avg_time: float = statistics.mean(times) if times else 0.0

        # Extract file name for compact display
        instance_file_parts = config.split(' | ')[0].split('/')
        instance_file_short = instance_file_parts[-1]
        config_params = ' | '.join(config.split(' | ')[1:])
        
        display_config = f"{instance_file_short} | {config_params}"

        print(
            f"{display_config:<60} {stats['count']:>6} {stats['best']:>10.0f} {stats['median']:>8.0f} "
            f"{stats['avg']:>10.2f} {stats['std']:>10.2f} {stats['iqr']:>8.0f} {avg_time:>10.6f}s"
        )
        if stats['outliers_count'] > 0:
            print(f"    Note: {stats['outliers_count']} outlier(s) detected (examples: {stats['outliers_examples'][:3]})")

        # Prepare compact summary for later inspection
        summary_data.append({
            "config": config,
            "instance_file": instance_file_short,
            "count": stats['count'],
            "best": stats['best'],
            "median": stats['median'],
            "avg": stats['avg'],
            "std": stats['std'],
            "interquartile_range": stats['iqr'],
            "outliers": stats['outliers_count'],
            "avg_time": avg_time
        })
    
    # Write summary file
    summary_file = ANALYSIS_DIR / "sa_summary.csv"
    if summary_data:
        fieldnames = summary_data[0].keys()
        with open(summary_file, "w", newline='') as sf:
            writer = csv.DictWriter(sf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_data)
        print(f"\nCompact summary written to {summary_file}")
        
    print("="*80 + "\n")


def analyze_genetic_algorithm() -> None:
    """
    Analyzes Genetic Algorithm results grouped by instance file and configuration.
    Configuration parameters used: generations, elite_number, mutation_rate, parent_selection.
    """
    csv_file: Path = OUTPUT_DIR / "genetic_algorithm.csv"
    if not csv_file.exists():
        print(f"No Genetic Algorithm results found at {csv_file}")
        return

    print("Reading Genetic Algorithm results...")
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        results: list[dict[str, str]] = list(reader)

    # Group by instance file and configuration
    by_config: defaultdict[str, list[dict[str, float]]] = defaultdict(list)
    for row in results:
        # Crossover points might be a list string, clean it up
        crossover = row.get('crossover_points', '[]').replace("['", "").replace("']", "").replace("', '", ",")

        key: str = (
            f"{row['instance_file']} | "
            #f"Gen:{row['generations']} | "
            #f"Elite:{row['elite_number']} | "
            #f"Mut:{float(row['mutation_rate']):.3f} | "
            #f"Sel:{row['parent_selection']} | "
            #f"Crossover:{crossover} | "
        )
        by_config[key].append({
            "benefit": int(row["benefit"]),
            "time": float(row["time"])
        })

    # Compute and print statistics
    print("\n" + "="*80)
    print("GENETIC ALGORITHM ANALYSIS (Grouped by Instance and Configuration)")
    print("="*80)
    header_format: str = (
        f"{'Instance & Config':<60} {'Count':>6} {'Best':>10} {'Median':>8} {'Avg':>10} "
        f"{'Std Dev':>10} {'IQR':>8} {'Avg Time':>10}"
    )
    print(header_format)
    print("-"*120)
    
    summary_data: list[dict[str, Any]] = []

    for config, runs in sorted(by_config.items()):
        benefits: list[float] = [float(r["benefit"]) for r in runs]
        times: list[float] = [r["time"] for r in runs]

        stats = _get_benefit_stats(benefits)
        avg_time: float = statistics.mean(times) if times else 0.0

        # Extract file name for compact display
        instance_file_parts = config.split(' | ')[0].split('/')
        instance_file_short = instance_file_parts[-1]
        config_params = ' | '.join(config.split(' | ')[1:])
        
        display_config = f"{instance_file_short} | {config_params}"

        print(
            f"{display_config:<60} {stats['count']:>6} {stats['best']:>10.0f} {stats['median']:>8.0f} "
            f"{stats['avg']:>10.2f} {stats['std']:>10.2f} {stats['iqr']:>8.0f} {avg_time:>10.6f}s"
        )
        if stats['outliers_count'] > 0:
            print(f"    Note: {stats['outliers_count']} outlier(s) detected (examples: {stats['outliers_examples'][:3]})")

        # Prepare compact summary for later inspection
        summary_data.append({
            "config": config,
            "instance_file": instance_file_short,
            "count": stats['count'],
            "best": stats['best'],
            "median": stats['median'],
            "avg": stats['avg'],
            "std": stats['std'],
            "interquartile_range": stats['iqr'],
            "outliers": stats['outliers_count'],
            "avg_time": avg_time
        })
    
    # Write summary file
    summary_file = ANALYSIS_DIR / "ga_summary.csv"
    if summary_data:
        fieldnames = summary_data[0].keys()
        with open(summary_file, "w", newline='') as sf:
            writer = csv.DictWriter(sf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_data)
        print(f"\nCompact summary written to {summary_file}")
        
    print("="*80 + "\n")


def compare_GA_SA() -> None:
    """
    Compares the best achieved benefit of Genetic Algorithm (GA) vs.
    Simulated Annealing (SA) for each unique problem instance file.
    """
    ga_file: Path = OUTPUT_DIR / "genetic_algorithm.csv"
    sa_file: Path = OUTPUT_DIR / "simulated_annealing.csv"

    if not ga_file.exists() or not sa_file.exists():
        if not ga_file.exists():
            print(f"GA results file missing at {ga_file}")
        if not sa_file.exists():
            print(f"SA results file missing at {sa_file}")
        return

    def get_max_benefit_by_instance(file_path: Path) -> dict[str, int]:
        """Reads CSV and finds the maximum benefit for each instance_file."""
        max_benefits: defaultdict[str, int] = defaultdict(int)
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                instance = row['instance_file']
                benefit = int(row['benefit'])
                max_benefits[instance] = max(max_benefits[instance], benefit)
        return dict(max_benefits)

    max_ga_benefits = get_max_benefit_by_instance(ga_file)
    max_sa_benefits = get_max_benefit_by_instance(sa_file)

    all_instances = sorted(list(set(max_ga_benefits.keys()) | set(max_sa_benefits.keys())))
    
    if not all_instances:
        print("No common or unique instances found to compare.")
        return

    print("\n" + "="*70)
    print("GENETIC ALGORITHM (GA) vs. SIMULATED ANNEALING (SA) COMPARISON")
    print("="*70)
    print(f"{'Instance File':<35} {'GA Best':>10} {'SA Best':>10} {'Winner':>10} {'Diff (%)':>10}")
    print("-"*70)

    comparison_data: list[dict[str, Any]] = []

    for instance in all_instances:
        ga_best = max_ga_benefits.get(instance, 0)
        sa_best = max_sa_benefits.get(instance, 0)
        
        winner = ""
        difference_pct = 0.0

        if ga_best > sa_best:
            winner = "GA"
            difference_pct = 100 * (ga_best - sa_best) / ga_best if ga_best > 0 else 0
        elif sa_best > ga_best:
            winner = "SA"
            difference_pct = 100 * (sa_best - ga_best) / sa_best if sa_best > 0 else 0
        else:
            winner = "Tie"
            difference_pct = 0.0
        
        # Display instance file name in a shorter format
        instance_file_short = instance.split('/')[-1]

        print(
            f"{instance_file_short:<35} {ga_best:>10} {sa_best:>10} "
            f"{winner:>10} {difference_pct:>9.2f}%"
        )
        
        comparison_data.append({
            "instance_file": instance,
            "ga_best": ga_best,
            "sa_best": sa_best,
            "winner": winner,
            "difference_pct": difference_pct
        })

    # Write comparison summary file
    summary_file = ANALYSIS_DIR / "ga_sa_comparison.csv"
    if comparison_data:
        fieldnames = comparison_data[0].keys()
        with open(summary_file, "w", newline='') as sf:
            writer = csv.DictWriter(sf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(comparison_data)
        print(f"\nComparison summary written to {summary_file}")

    print("="*70 + "\n")






























