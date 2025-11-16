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
    
    # Group by instance + method so we compute per-instance statistics first
    by_instance_and_method: defaultdict[str, list[dict[str, float]]] = defaultdict(list)
    for row in results:
        instance = row.get("instance_file") or ""
        method = row.get("method") or ""
        key = f"{instance} | {method}"
        by_instance_and_method[key].append({
            "benefit": float(row.get("benefit", 0.0)),
            "time": float(row.get("time", 0.0))
        })

    # Print header for per-instance constructive results
    print("="*50)
    print("CONSTRUCTIVE METHODS ANALYSIS")
    print("="*50)
    print(f"{'Instance':<30} {'Method':<40} {'Count':>6} {'Best':>10} {'Median':>8} {'Avg':>10} {'Std Dev':>10} {'Avg Time':>10}")
    print("-"*120)

    # Collect per-instance summary rows and medians for aggregation
    summary_rows: list[dict[str, Any]] = []
    per_method_medians: defaultdict[str, dict[str, float]] = defaultdict(dict)

    for key, runs in sorted(by_instance_and_method.items()):
        instance, method = key.split(" | ")
        benefits = [r["benefit"] for r in runs]
        times = [r["time"] for r in runs]

        stats = _get_benefit_stats(benefits)
        avg_time = statistics.mean(times) if times else 0.0

        print(f"{instance.split('/')[-1]:<30} {method:<40} {stats['count']:>6} {stats['best']:>10.0f} {stats['median']:>8.0f} {stats['avg']:>10.2f} {stats['std']:>10.2f} {avg_time:>10.6f}s")

        summary_rows.append({
            "instance_file": instance.split('/')[-1],
            "method": method,
            "count": stats['count'],
            "best": stats['best'],
            "median": stats['median'],
            "avg": stats['avg'],
            "std": stats['std'],
            "iqr": stats['iqr'],
            "outliers": stats['outliers_count'],
            "avg_time": avg_time
        })

        per_method_medians[method][instance] = stats['median']

    # Write per-instance summary
    per_instance_file = ANALYSIS_DIR / "constructive_by_instance.csv"
    if summary_rows:
        fieldnames = summary_rows[0].keys()
        with open(per_instance_file, "w", newline='') as pf:
            writer = csv.DictWriter(pf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"\nPer-instance constructive summary written to {per_instance_file}")

    # Aggregate across instances: median-of-medians and wins per method
    aggregate_rows: list[dict[str, Any]] = []
    wins_counter: dict[str, int] = defaultdict(int)

    # Build instance -> list of (method, median)
    instance_map: defaultdict[str, list[tuple[str, float]]] = defaultdict(list)
    for method, inst_map in per_method_medians.items():
        for inst, med in inst_map.items():
            instance_map[inst].append((method, med))

    for inst, method_list in instance_map.items():
        if not method_list:
            continue
        best_med = max(m for (_, m) in method_list)
        for method, med in method_list:
            if med == best_med:
                wins_counter[method] += 1

    for method, inst_map in per_method_medians.items():
        medians = list(inst_map.values())
        median_of_medians = statistics.median(medians) if medians else 0.0
        aggregate_rows.append({
            "method": method,
            "instances": len(medians),
            "median_of_medians": median_of_medians,
            "wins": wins_counter.get(method, 0)
        })

    aggregate_file = ANALYSIS_DIR / "constructive_aggregate.csv"
    if aggregate_rows:
        fieldnames = aggregate_rows[0].keys()
        with open(aggregate_file, "w", newline='') as af:
            writer = csv.DictWriter(af, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted(aggregate_rows, key=lambda r: (-r['wins'], -r['median_of_medians'])))
        print(f"Aggregated constructive summary written to {aggregate_file}")

    print("="*50 + "\n")

# Analyze and print local search results
def analyze_local_search() -> None:
    csv_file: Path = OUTPUT_DIR / "local_search.csv"
    
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        results: list[dict[str, str]] = list(reader)
    
    # Group by instance + configuration to compute per-instance statistics first
    by_instance_and_config: defaultdict[str, list[dict[str, float]]] = defaultdict(list)
    for row in results:
        instance = row.get("instance_file") or ""
        neighborhoods_field = row.get("neighborhoods") or row.get("neighborhood_names") or ""
        ls_method_field = row.get("ls_method") or row.get("ils_method") or ""
        refinement_field = row.get("refinement_heuristics") or ""

        key: str = f"{instance} | {ls_method_field} | {refinement_field} | {neighborhoods_field}"
        by_instance_and_config[key].append({
            "final": float(row.get("benefit", row.get("final_benefit", 0.0))),
            "improvement_pct": float(row.get("improvement_pct", 0.0)),
            "time": float(row.get("time", 0.0))
        })

    # Print header for per-instance local search results
    print("="*50)
    print("LOCAL SEARCH ANALYSIS (Per Instance)")
    print("="*50)
    print(f"{'Instance':<25} {'Local Search Method':<30} {'Refinement':<25} {'Neighborhoods':<20} {'Best':>8} {'Median':>8} {'Std':>8} {'Time':>8}")
    print("-"*120)

    # Collect per-instance summary rows and medians for aggregation
    summary_rows: list[dict[str, Any]] = []
    per_config_medians: defaultdict[str, dict[str, float]] = defaultdict(dict)

    for key, runs in sorted(by_instance_and_config.items()):
        parts = key.split(" | ")
        instance = parts[0]
        ls_method = parts[1]
        refinement = parts[2].replace("['", "").replace("']", "").replace("', '", ",")
        neighborhoods = parts[3].replace("['", "").replace("']", "").replace("', '", ",")

        finals: list[float] = [r["final"] for r in runs]
        times: list[float] = [r["time"] for r in runs]

        stats = _get_benefit_stats(finals)
        avg_time: float = statistics.mean(times) if times else 0.0

        print(f"{instance.split('/')[-1]:<25} {ls_method:<30} {refinement:<25} {neighborhoods:<20} {stats['best']:>8.0f} {stats['median']:>8.2f} {stats['std']:>8.2f} {avg_time:>8.2f}s")

        summary_rows.append({
            "instance_file": instance.split('/')[-1],
            "config": f"{ls_method} | {refinement} | {neighborhoods}",
            "count": stats['count'],
            "best": stats['best'],
            "median": stats['median'],
            "avg": stats['avg'],
            "std": stats['std'],
            "interquartile_range": stats['iqr'],
            "outliers": stats['outliers_count'],
            "avg_time": avg_time
        })

        config_key = f"{ls_method} | {refinement} | {neighborhoods}"
        per_config_medians[config_key][instance] = stats['median']

    # Write per-instance summary file
    per_instance_file = ANALYSIS_DIR / "local_search_by_instance.csv"
    if summary_rows:
        fieldnames = summary_rows[0].keys()
        with open(per_instance_file, "w", newline='') as pf:
            writer = csv.DictWriter(pf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"\nPer-instance local search summary written to {per_instance_file}")

    # Aggregate across instances
    aggregate_rows: list[dict[str, Any]] = []
    wins_counter: dict[str, int] = defaultdict(int)

    instance_to_config_medians: defaultdict[str, list[tuple[str, float]]] = defaultdict(list)
    for cfg, inst_map in per_config_medians.items():
        for inst, med in inst_map.items():
            instance_to_config_medians[inst].append((cfg, med))

    for inst, cfg_list in instance_to_config_medians.items():
        if not cfg_list:
            continue
        best_med = max(m for (_, m) in cfg_list)
        for cfg, med in cfg_list:
            if med == best_med:
                wins_counter[cfg] += 1

    for cfg, inst_map in per_config_medians.items():
        medians = list(inst_map.values())
        median_of_medians = statistics.median(medians) if medians else 0.0
        aggregate_rows.append({
            "config": cfg,
            "instances": len(medians),
            "median_of_medians": median_of_medians,
            "wins": wins_counter.get(cfg, 0)
        })

    aggregate_file = ANALYSIS_DIR / "local_search_aggregate.csv"
    if aggregate_rows:
        fieldnames = aggregate_rows[0].keys()
        with open(aggregate_file, "w", newline='') as af:
            writer = csv.DictWriter(af, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted(aggregate_rows, key=lambda r: (-r['wins'], -r['median_of_medians'])))
        print(f"Aggregated local search summary written to {aggregate_file}")

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

# 
def analyze_iterated_local_search() -> None:
    csv_file: Path = OUTPUT_DIR / "iterated_local_search.csv"
    if not csv_file.exists():
        print(f"No Iterated Local Search results found at {csv_file}")
        return

    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        results: list[dict[str, str]] = list(reader)
    
    # Group by instance file + configuration. Some harness versions write the
    # neighborhood column as `neighborhoods` while others use
    # `neighborhood_names`. Be tolerant and use whichever is present.
    by_instance_and_config: defaultdict[str, list[dict[str, float]]] = defaultdict(list)
    for row in results:
        instance = row.get("instance_file") or ""
        neighborhoods_field = row.get("neighborhoods") or row.get("neighborhood_names") or ""
        ls_method_field = row.get("ls_method") or row.get("ils_method") or ""
        refinement_field = row.get("refinement_heuristics") or ""

        # Key includes instance so we compute per-instance stats first
        key: str = f"{instance} | {ls_method_field} | {refinement_field} | {neighborhoods_field}"
        by_instance_and_config[key].append({
            "final": float(row.get("benefit", row.get("final_benefit", 0.0))),
            "improvement_pct": float(row.get("improvement_pct", 0.0)),
            "time": float(row.get("time", 0.0))
        })
    
    # Compute and print statistics
    print("="*50)
    print("ITERATED LOCAL SEARCH ANALYSIS")
    print("="*50)
    print(f"{'Instance':<25} {'ILS Method':<30} {'Refinement':<25} {'Neighborhoods':<20} {'Best':>8} {'Median':>8} {'Std':>8} {'Time':>8}")
    print("-"*50)
    
    # For each (instance, config) compute stats and print per-instance results
    summary_data: list[dict[str, Any]] = []
    per_instance_medians: defaultdict[str, dict[str, float]] = defaultdict(dict)

    for key, runs in sorted(by_instance_and_config.items()):
        # Key format: instance | ls_method | refinement | neighborhoods
        parts = key.split(" | ")
        instance = parts[0]
        ls_method = parts[1]
        refinement = parts[2].replace("['", "").replace("']", "").replace("', '", ",")
        neighborhoods = parts[3].replace("['", "").replace("']", "").replace("', '", ",")

        finals: list[float] = [r["final"] for r in runs]
        times: list[float] = [r["time"] for r in runs]

        stats = _get_benefit_stats(finals)
        avg_time: float = statistics.mean(times) if times else 0.0

        print(f"{instance.split('/')[-1]:<25} {ls_method:<30} {refinement:<25} {neighborhoods:<20} {stats['best']:>8.0f} {stats['median']:>8.2f} {stats['std']:>8.2f} {avg_time:>8.2f}s")

        summary_data.append({
            "instance_file": instance.split('/')[-1],
            "config": f"{ls_method} | {refinement} | {neighborhoods}",
            "count": stats['count'],
            "best": stats['best'],
            "median": stats['median'],
            "avg": stats['avg'],
            "std": stats['std'],
            "interquartile_range": stats['iqr'],
            "outliers": stats['outliers_count'],
            "avg_time": avg_time
        })

        # Save median per-instance for later aggregation
        config_key = f"{ls_method} | {refinement} | {neighborhoods}"
        per_instance_medians[config_key][instance] = stats['median']

    # Write per-instance summary file
    summary_file = ANALYSIS_DIR / "ils_summary.csv"
    if summary_data:
        fieldnames = summary_data[0].keys()
        with open(summary_file, "w", newline='') as sf:
            writer = csv.DictWriter(sf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_data)
        print(f"\nPer-instance summary written to {summary_file}")

    # Aggregate across instances: compute median-of-medians and wins per config
    aggregate_rows: list[dict[str, Any]] = []
    # Count wins per instance
    wins_counter: dict[str, int] = defaultdict(int)

    # For each instance, find the config with highest median
    instance_to_config_medians: defaultdict[str, list[tuple[str, float]]] = defaultdict(list)
    for cfg, inst_map in per_instance_medians.items():
        for inst, med in inst_map.items():
            instance_to_config_medians[inst].append((cfg, med))

    for inst, cfg_list in instance_to_config_medians.items():
        # Find best median (ties allowed)
        if not cfg_list:
            continue
        best_med = max(m for (_, m) in cfg_list)
        for cfg, med in cfg_list:
            if med == best_med:
                wins_counter[cfg] += 1

    for cfg, inst_map in per_instance_medians.items():
        medians = list(inst_map.values())
        median_of_medians = statistics.median(medians) if medians else 0.0
        aggregate_rows.append({
            "config": cfg,
            "instances": len(medians),
            "median_of_medians": median_of_medians,
            "wins": wins_counter.get(cfg, 0)
        })

    # Write aggregate summary file
    aggregate_file = ANALYSIS_DIR / "ils_aggregate.csv"
    if aggregate_rows:
        fieldnames = aggregate_rows[0].keys()
        with open(aggregate_file, "w", newline='') as af:
            writer = csv.DictWriter(af, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted(aggregate_rows, key=lambda r: (-r['wins'], -r['median_of_medians'])))
        print(f"Aggregated summary written to {aggregate_file}")

# 
def analyze_best_runs_per_instance(target_files: list[str] | None = None, *, combine: bool = False, print_solution: bool = True) -> None:
    """
    Find and report the best runs per instance.

    Behavior:
    - Scans the standard experiment CSVs (or `target_files` if provided) and
      collects all rows.
    - For each instance, finds the best run for each distinct "method"
      (method name inferred from several possible columns) and prints a
      per-instance section listing each method's best run. Each printed line
      includes a simple identifier `SOURCE:RUN_ID` so you can locate the
      original CSV row easily.
    - Finally, prints a summary with the best run found across all methods
      for each instance and writes two CSVs into `output/analysis`:
        - `best_per_method_by_instance.csv` : one row per (instance, method)
        - `combined_best_runs_by_instance.csv` : one row per instance (best overall)

    The function is tolerant to varying CSV schemas (different column names
    for benefit/time/method). Tie-breaking: larger benefit wins; on equal
    benefit, smaller time wins.
    """
    default_files = [
        "constructive.csv",
        "local_search.csv",
        "simulated_annealing.csv",
        "iterated_local_search.csv",
        "genetic_algorithm.csv",
    ]

    files_to_check = target_files if target_files is not None else default_files

    # Collect all rows from the selected files so we can produce cross-method
    # per-instance summaries.
    combined_rows: list[dict[str, str]] = []
    for fname in files_to_check:
        csv_file = OUTPUT_DIR / fname
        if not csv_file.exists():
            continue
        with open(csv_file, "r", newline='') as f:
            reader = csv.DictReader(f)
            for i, r in enumerate(reader):
                # mark source so printed identifiers and CSVs point back to origin
                r['_source_file'] = fname
                # ensure there is an easy-to-find run identifier; prefer `run_id`,
                # fall back to `run_seed` or the row index when missing
                if not r.get('run_id'):
                    r['run_id'] = r.get('run_seed') or str(i)
                combined_rows.append(r)

    if not combined_rows:
        print("No experiment rows found in the selected files.")
        return

    # --- Per-file bests: for each CSV (method type) print the best run per instance ---
    file_map: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in combined_rows:
        src = r.get('_source_file') or '<unknown>'
        file_map[src].append(r)

    print("\n" + "=" * 80)
    print("BEST PER INPUT FILE (best run per instance within each CSV)")
    print("=" * 80)
    for fname in sorted(file_map.keys()):
        rows = file_map[fname]
        print(f"\nFile: {fname}")
        # compute best per instance inside this file
        best_by_instance: dict[str, dict[str, str]] = {}
        for r in rows:
            inst = r.get('instance_file') or r.get('instance') or 'unknown'
            cur = best_by_instance.get(inst)
            if cur is None:
                best_by_instance[inst] = r
                continue
            b_new = float(r.get('benefit', r.get('final_benefit', r.get('final', 0))))
            b_cur = float(cur.get('benefit', cur.get('final_benefit', cur.get('final', 0))))
            if b_new > b_cur or (b_new == b_cur and float(r.get('time', 0.0)) < float(cur.get('time', 0.0))):
                best_by_instance[inst] = r

        print(f"{'Instance':<30} {'Benefit':>10} {'Time':>10} {'ID':<25}")
        print('-' * 90)
        for inst in sorted(best_by_instance.keys()):
            r = best_by_instance[inst]
            inst_short = inst.split('/')[-1]
            b = float(r.get('benefit', r.get('final_benefit', r.get('final', 0))))
            t = float(r.get('time', 0.0))
            identifier = f"{r.get('_source_file')}:{r.get('run_id')}"
            print(f"{inst_short:<30} {b:>10.0f} {t:>10.3f} {identifier:<25}")

        # write CSV with best-by-instance for this file
        out_file = ANALYSIS_DIR / f"{Path(fname).stem}_best_per_file.csv"
        # determine union of keys for writer
        all_keys = set()
        for r in best_by_instance.values():
            all_keys.update(r.keys())
        all_keys = {k for k in all_keys if k is not None}
        preferred = ["instance_file", "run_id", "benefit", "time", "_source_file"]
        present_pref = [k for k in preferred if k in all_keys]
        rest = sorted(all_keys - set(present_pref), key=lambda x: str(x))
        fieldnames = present_pref + rest
        with open(out_file, 'w', newline='') as of:
            writer = csv.DictWriter(of, fieldnames=fieldnames)
            writer.writeheader()
            for inst in sorted(best_by_instance.keys()):
                writer.writerow(best_by_instance[inst])
        print(f"Wrote per-file bests to {out_file}")

    # Group rows by instance file
    instance_map: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for r in combined_rows:
        instance = r.get('instance_file') or r.get('instance') or 'unknown'
        instance_map[instance].append(r)

    def get_method_name(rr: dict[str, str]) -> str:
        """Return a best-effort method name for a row (type-hinted)."""
        return (rr.get('method') or rr.get('ls_method') or rr.get('ils_method') or
                rr.get('initial_method') or rr.get('Solution') or rr.get('solver') or '')

    def benefit_of(rr: dict[str, str]) -> float:
        return float(rr.get('benefit', rr.get('final_benefit', rr.get('final', 0))))

    def time_of(rr: dict[str, str]) -> float:
        return float(rr.get('time', 0.0))

    # Prepare containers for CSV output
    per_method_best_rows: list[dict[str, str]] = []
    best_overall_by_instance: dict[str, dict[str, str]] = {}

    # Print per-instance sections
    print("\n" + "=" * 80)
    print("BEST RUNS PER INSTANCE (best per method)")
    print("=" * 80)
    for inst in sorted(instance_map.keys()):
        rows = instance_map[inst]
        inst_short = inst.split('/')[-1]
        print(f"\nInstance: {inst_short}")
        print(f"{'Method':<30} {'Benefit':>10} {'Time':>10} {'ID':<25} {'Source':<25}")
        print('-' * 110)

        # find best run per method for this instance
        method_best: dict[str, dict[str, str]] = {}
        for r in rows:
            m = get_method_name(r) or '<unknown>'
            cur = method_best.get(m)
            b = benefit_of(r)
            t = time_of(r)
            if cur is None:
                method_best[m] = r
            else:
                if b > benefit_of(cur) or (b == benefit_of(cur) and t < time_of(cur)):
                    method_best[m] = r

        # Print and collect per-method bests for this instance
        for m in sorted(method_best.keys()):
            r = method_best[m]
            b = benefit_of(r)
            t = time_of(r)
            identifier = f"{r.get('_source_file')}:{r.get('run_id')}"
            source = r.get('_source_file', '')
            print(f"{m:<30} {b:>10.0f} {t:>10.3f} {identifier:<25} {source:<25}")
            per_method_best_rows.append({**r, "method_inferred": m})

        # Determine best overall for this instance among the method-best rows
        best_for_inst: dict[str, str] | None = None
        for r in method_best.values():
            if best_for_inst is None:
                best_for_inst = r
                continue
            if benefit_of(r) > benefit_of(best_for_inst) or (
                benefit_of(r) == benefit_of(best_for_inst) and time_of(r) < time_of(best_for_inst)
            ):
                best_for_inst = r

        if best_for_inst is not None:
            # Print best overall for this instance immediately inside the section
            bm = best_for_inst
            bm_method = get_method_name(bm) or '<unknown>'
            bm_b = benefit_of(bm)
            bm_t = time_of(bm)
            bm_id = f"{bm.get('_source_file')}:{bm.get('run_id')}"
            print('\nBest overall for this instance:')
            print(f"{bm_method:<30} {bm_b:>10.0f} {bm_t:>10.3f} {bm_id:<25} {bm.get('_source_file',''):<25}")
            # store for the combined final summary
            best_overall_by_instance[inst] = best_for_inst

    # Write per-method-per-instance CSV (union of keys)
    if per_method_best_rows:
        all_keys = set()
        for r in per_method_best_rows:
            all_keys.update(r.keys())
        all_keys = {k for k in all_keys if k is not None}
        preferred = ["instance_file", "run_id", "method_inferred", "benefit", "time", "_source_file"]
        present_pref = [k for k in preferred if k in all_keys]
        rest = sorted(all_keys - set(present_pref), key=lambda x: str(x))
        fieldnames = present_pref + rest

        out_file = ANALYSIS_DIR / "best_per_method_by_instance.csv"
        with open(out_file, 'w', newline='') as pf:
            writer = csv.DictWriter(pf, fieldnames=fieldnames)
            writer.writeheader()
            for r in per_method_best_rows:
                writer.writerow(r)
        print(f"\nWrote per-method bests to {out_file}")

    # Print and write best overall per instance
    print("\n" + "=" * 80)
    print("BEST OVERALL PER INSTANCE (across all methods)")
    print("=" * 80)
    print(f"{'Instance':<30} {'Benefit':>10} {'Time':>10} {'ID':<25} {'Source':<25}")
    print('-' * 110)
    for inst in sorted(best_overall_by_instance.keys()):
        r = best_overall_by_instance[inst]
        inst_short = inst.split('/')[-1]
        b = benefit_of(r)
        t = time_of(r)
        identifier = f"{r.get('_source_file')}:{r.get('run_id')}"
        source = r.get('_source_file', '')
        print(f"{inst_short:<30} {b:>10.0f} {t:>10.3f} {identifier:<25} {source:<25}")

    if best_overall_by_instance:
        # write combined CSV
        all_keys = set()
        for r in best_overall_by_instance.values():
            all_keys.update(r.keys())
        all_keys = {k for k in all_keys if k is not None}
        preferred_present = [k for k in ["instance_file", "run_id", "benefit", "time", "_source_file"] if k in all_keys]
        rest = sorted(all_keys - set(preferred_present), key=lambda x: str(x))
        fieldnames = preferred_present + rest

        out_file = ANALYSIS_DIR / "combined_best_runs_by_instance.csv"
        with open(out_file, 'w', newline='') as of:
            writer = csv.DictWriter(of, fieldnames=fieldnames)
            writer.writeheader()
            for inst in sorted(best_overall_by_instance.keys()):
                writer.writerow(best_overall_by_instance[inst])
        print(f"Wrote combined best-runs-per-instance to {out_file}")


