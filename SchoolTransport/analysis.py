# Python 3.10.0

import csv
from pathlib import Path
from typing import Dict, List, Any
import statistics
import re

def analyzeResults(folder_path: Path, output_file: str = "analysis_summary.csv") -> None:
    """
    Analyzes all result CSV files and creates a summary suitable for Google Sheets.
    
    For each instance configuration (numSchools, numStudents, maxRows, maxCols),
    aggregates results across all map instances (0-4) and runs.
    
    Output columns:
    - Instance parameters (numSchools, numStudents, maxRows, maxCols)
    - For each method (SA, RRT, GDA):
      - Average Euclidean Cost
      - Std Dev Euclidean Cost
      - Average Manhattan Cost
      - Std Dev Manhattan Cost
      - Best Cost Found (Euclidean)
      - Best Cost Found (Manhattan)
    """
    
    if not folder_path.exists():
        print(f"Folder {folder_path} does not exist.")
        return
    
    csv_files = list(folder_path.glob("results_school_transport_*.csv"))
    
    if not csv_files:
        print(f"No result files found in {folder_path}")
        return
    
    print(f"Found {len(csv_files)} result files to analyze.\n")
    
    # Dictionary to store results by configuration
    # Key: (numSchools, numStudents, maxRows, maxCols)
    # Value: Dict with method -> list of costs
    config_results: Dict[tuple, Dict[str, List[Dict[str, float]]]] = {}
    
    # Parse all files
    for csv_file in csv_files:
        # Extract parameters from filename
        # Format: results_school_transport_2_4_10_10_0_v1.csv
        match = re.search(r'results_school_transport_(\d+)_(\d+)_(\d+)_(\d+)_(\d+)_v(\d+)\.csv', csv_file.name)
        if not match:
            print(f"Skipping {csv_file.name} - unexpected filename format")
            continue
        
        numSchools = int(match.group(1))
        numStudents = int(match.group(2))
        maxRows = int(match.group(3))
        maxCols = int(match.group(4))
        mapInstance = int(match.group(5))
        version = int(match.group(6))
        
        config_key = (numSchools, numStudents, maxRows, maxCols)
        
        # Initialize if needed
        if config_key not in config_results:
            config_results[config_key] = {'SA': [], 'RRT': [], 'GDA': []}
        
        # Read the CSV
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    method = row.get('Method', '').strip()
                    if method not in ['SA', 'RRT', 'GDA']:
                        continue
                    
                    euclidean = row.get('EuclideanCost', '').strip()
                    manhattan = row.get('ManhattanCost', '').strip()
                    
                    exec_time = row.get('ExecutionTime', '').strip()
                    
                    if euclidean and manhattan:
                        config_results[config_key][method].append({
                            'euclidean': float(euclidean),
                            'manhattan': int(manhattan),
                            'executionTime': float(exec_time) if exec_time else 0.0,
                            'mapInstance': mapInstance
                        })
        except Exception as e:
            print(f"Error reading {csv_file.name}: {e}")
            continue
    
    # Generate summary statistics
    summary_rows = []
    
    for config_key in sorted(config_results.keys()):
        numSchools, numStudents, maxRows, maxCols = config_key
        results = config_results[config_key]
        
        row = {
            'numSchools': numSchools,
            'numStudents': numStudents,
            'maxRows': maxRows,
            'maxCols': maxCols,
            'totalRuns': sum(len(results[m]) for m in ['SA', 'RRT', 'GDA']) // 3
        }
        
        for method in ['SA', 'RRT', 'GDA']:
            data = results[method]
            
            if not data:
                row[f'{method}_AvgEuclidean'] = ''
                row[f'{method}_StdEuclidean'] = ''
                row[f'{method}_AvgManhattan'] = ''
                row[f'{method}_StdManhattan'] = ''
                row[f'{method}_BestEuclidean'] = ''
                row[f'{method}_BestManhattan'] = ''
                continue
            
            euclidean_costs = [d['euclidean'] for d in data]
            manhattan_costs = [d['manhattan'] for d in data]
            execution_times = [d['executionTime'] for d in data]
            
            row[f'{method}_AvgEuclidean'] = round(statistics.mean(euclidean_costs), 4)
            row[f'{method}_StdEuclidean'] = round(statistics.stdev(euclidean_costs), 4) if len(euclidean_costs) > 1 else 0
            row[f'{method}_AvgManhattan'] = round(statistics.mean(manhattan_costs), 2)
            row[f'{method}_StdManhattan'] = round(statistics.stdev(manhattan_costs), 2) if len(manhattan_costs) > 1 else 0
            row[f'{method}_BestEuclidean'] = round(min(euclidean_costs), 4)
            row[f'{method}_BestManhattan'] = int(min(manhattan_costs))
            row[f'{method}_AvgTime'] = round(statistics.mean(execution_times), 3)
            row[f'{method}_StdTime'] = round(statistics.stdev(execution_times), 3) if len(execution_times) > 1 else 0
        
        summary_rows.append(row)
    
    # Write summary to CSV
    output_path = folder_path / output_file
    
    fieldnames = [
        'numSchools', 'numStudents', 'maxRows', 'maxCols', 'totalRuns',
        'SA_AvgEuclidean', 'SA_StdEuclidean', 'SA_BestEuclidean',
        'SA_AvgManhattan', 'SA_StdManhattan', 'SA_BestManhattan',
        'SA_AvgTime', 'SA_StdTime',
        'RRT_AvgEuclidean', 'RRT_StdEuclidean', 'RRT_BestEuclidean',
        'RRT_AvgManhattan', 'RRT_StdManhattan', 'RRT_BestManhattan',
        'RRT_AvgTime', 'RRT_StdTime',
        'GDA_AvgEuclidean', 'GDA_StdEuclidean', 'GDA_BestEuclidean',
        'GDA_AvgManhattan', 'GDA_StdManhattan', 'GDA_BestManhattan',
        'GDA_AvgTime', 'GDA_StdTime'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    
    print(f"\n✓ Analysis complete! Summary saved to: {output_path}")
    print(f"  Total configurations analyzed: {len(summary_rows)}")
    print(f"  You can copy this CSV directly into Google Sheets.")
    
    # Print a quick preview
    print("\n=== Preview (first 3 rows) ===")
    for i, row in enumerate(summary_rows[:3]):
        print(f"\nConfig: {row['numSchools']} schools, {row['numStudents']} students")
        print(f"  SA  - Avg: {row['SA_AvgEuclidean']:.2f} (±{row['SA_StdEuclidean']:.2f}), Best: {row['SA_BestEuclidean']:.2f}, Time: {row['SA_AvgTime']:.3f}s")
        print(f"  RRT - Avg: {row['RRT_AvgEuclidean']:.2f} (±{row['RRT_StdEuclidean']:.2f}), Best: {row['RRT_BestEuclidean']:.2f}, Time: {row['RRT_AvgTime']:.3f}s")
        print(f"  GDA - Avg: {row['GDA_AvgEuclidean']:.2f} (±{row['GDA_StdEuclidean']:.2f}), Best: {row['GDA_BestEuclidean']:.2f}, Time: {row['GDA_AvgTime']:.3f}s")


def createMethodComparisonTable(folder_path: Path, output_file: str = "method_comparison.csv") -> None:
    """
    Creates a simpler comparison table showing which method performs best
    for each instance configuration.
    """
    
    # First, read the summary file
    summary_file = folder_path / "analysis_summary.csv"
    if not summary_file.exists():
        print("Run analyzeResults() first to generate analysis_summary.csv")
        return
    
    comparison_rows = []
    
    with open(summary_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Safely convert to float with defaults
            sa_avg = float(row.get('SA_AvgEuclidean', '') or 'inf')
            rrt_avg = float(row.get('RRT_AvgEuclidean', '') or 'inf')
            gda_avg = float(row.get('GDA_AvgEuclidean', '') or 'inf')
            
            sa_best = float(row.get('SA_BestEuclidean', '') or 'inf')
            rrt_best = float(row.get('RRT_BestEuclidean', '') or 'inf')
            gda_best = float(row.get('GDA_BestEuclidean', '') or 'inf')
            
            best_avg_method = min([('SA', sa_avg), ('RRT', rrt_avg), ('GDA', gda_avg)], key=lambda x: x[1])[0]
            best_overall_method = min([('SA', sa_best), ('RRT', rrt_best), ('GDA', gda_best)], key=lambda x: x[1])[0]
            
            comparison_rows.append({
                'numSchools': row['numSchools'],
                'numStudents': row['numStudents'],
                'bestAvgMethod': best_avg_method,
                'bestAvgCost': round(min(sa_avg, rrt_avg, gda_avg), 4),
                'bestOverallMethod': best_overall_method,
                'bestOverallCost': round(min(sa_best, rrt_best, gda_best), 4),
                'SA_Avg': sa_avg,
                'RRT_Avg': rrt_avg,
                'GDA_Avg': gda_avg
            })
    
    output_path = folder_path / output_file
    fieldnames = ['numSchools', 'numStudents', 'bestAvgMethod', 'bestAvgCost', 
                  'bestOverallMethod', 'bestOverallCost', 'SA_Avg', 'RRT_Avg', 'GDA_Avg']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(comparison_rows)
    
    print(f"\n✓ Method comparison saved to: {output_path}")


def createTimeQualityAnalysis(folder_path: Path, output_file: str = "time_quality_analysis.csv") -> None:
    """
    Creates an analysis showing the trade-off between execution time and solution quality.
    For each method, calculates quality per second metrics.
    """
    
    # First, read the summary file
    summary_file = folder_path / "analysis_summary.csv"
    if not summary_file.exists():
        print("Run analyzeResults() first to generate analysis_summary.csv")
        return
    
    analysis_rows = []
    
    with open(summary_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            config_row = {
                'numSchools': row['numSchools'],
                'numStudents': row['numStudents']
            }
            
            # For each method, calculate efficiency metrics
            for method in ['SA', 'RRT', 'GDA']:
                avg_cost_str = row.get(f'{method}_AvgEuclidean', '')
                avg_time_str = row.get(f'{method}_AvgTime', '')
                best_cost_str = row.get(f'{method}_BestEuclidean', '')
                
                avg_cost = float(avg_cost_str) if avg_cost_str else 0.0
                avg_time = float(avg_time_str) if avg_time_str else 1.0
                best_cost = float(best_cost_str) if best_cost_str else 0.0
                
                # Quality per second (lower is better - cost/time ratio)
                config_row[f'{method}_Efficiency'] = round(avg_cost / avg_time, 4) if avg_time > 0 else 0.0
                config_row[f'{method}_AvgCost'] = round(avg_cost, 4)
                config_row[f'{method}_AvgTime'] = round(avg_time, 3)
                config_row[f'{method}_BestCost'] = round(best_cost, 4)
            
            # Find most efficient method (lowest cost/time ratio)
            efficiencies = [
                ('SA', float(config_row['SA_Efficiency'])),
                ('RRT', float(config_row['RRT_Efficiency'])),
                ('GDA', float(config_row['GDA_Efficiency']))
            ]
            valid_efficiencies = [e for e in efficiencies if e[1] > 0]
            most_efficient = min(valid_efficiencies, key=lambda x: x[1]) if valid_efficiencies else ('N/A', 0.0)
            config_row['MostEfficient'] = most_efficient[0]
            
            # Find fastest method
            times = [
                ('SA', float(config_row['SA_AvgTime'])),
                ('RRT', float(config_row['RRT_AvgTime'])),
                ('GDA', float(config_row['GDA_AvgTime']))
            ]
            valid_times = [t for t in times if t[1] > 0]
            fastest = min(valid_times, key=lambda x: x[1]) if valid_times else ('N/A', 0.0)
            config_row['Fastest'] = fastest[0]
            config_row['FastestTime'] = round(fastest[1], 3)
            
            analysis_rows.append(config_row)
    
    output_path = folder_path / output_file
    fieldnames = [
        'numSchools', 'numStudents',
        'SA_AvgCost', 'SA_AvgTime', 'SA_Efficiency', 'SA_BestCost',
        'RRT_AvgCost', 'RRT_AvgTime', 'RRT_Efficiency', 'RRT_BestCost',
        'GDA_AvgCost', 'GDA_AvgTime', 'GDA_Efficiency', 'GDA_BestCost',
        'MostEfficient', 'Fastest', 'FastestTime'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(analysis_rows)
    
    print(f"\n✓ Time-quality analysis saved to: {output_path}")
    print("\nEfficiency = Average Cost / Average Time (lower is better)")


if __name__ == "__main__":
    # Example usage
    output_folder = Path("output")
    
    print("=== Analyzing Experiment Results ===\n")
    analyzeResults(output_folder)
    
    print("\n=== Creating Method Comparison ===\n")
    createMethodComparisonTable(output_folder)
    
    print("\n=== Creating Time-Quality Analysis ===\n")
    createTimeQualityAnalysis(output_folder)