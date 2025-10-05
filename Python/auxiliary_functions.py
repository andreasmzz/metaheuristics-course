# Python 3.13.4

import csv
from pathlib import Path
from typing import Any

''' Global varibales '''

# Used on every run to track performance
_evaluation_count:int = 0

# 
def reset_evaluation_count() -> None:
    global _evaluation_count
    _evaluation_count = 0

# 
def get_evaluation_count() -> int:
    return _evaluation_count


# Evaluates the total benefit of packages related to selected dependencies
def evaluate_packs(pack_benefits:list[int], pack_dep:list[tuple[int, int]], select_dep:list[bool]) -> int:
    global _evaluation_count
    _evaluation_count += 1
    
    total_benefits: int = 0
    pack_all_deps: dict[int, set[int]] = get_pack_dict(pack_dep)

    for pack in pack_all_deps:
        if pack_all_deps[pack].issubset(set(i for i in range(len(select_dep)) if select_dep[i])): # if all dependencies of the package are selected
            total_benefits += pack_benefits[pack]

    return total_benefits

def get_remaining_capacity(dep_sizes:list[int], selec_dep:list[bool], capacity:int) -> int:
    used_space: int = sum(dep_sizes[i] for i in range(len(selec_dep)) if selec_dep[i])
    return capacity - used_space

# pack_id -> set of dependencies it needs
def get_pack_dict(pack_dep:list[tuple[int, int]]) -> dict[int, set[int]]:
    pack_dict: dict[int, set[int]] = {}
    for (pack, dep) in pack_dep:
        if pack not in pack_dict: # first time seeing this package
            pack_dict[pack] = set()
        pack_dict[pack].add(dep)
    return pack_dict

# dep_id -> set of packages that depend on it
def get_dep_dict(pack_dep:list[tuple[int, int]]) -> dict[int, set[int]]:
    dep_dict: dict[int, set[int]] = {}
    for (pack, dep) in pack_dep:
        if dep not in dep_dict: # first time seeing this dependency
            dep_dict[dep] = set()
        dep_dict[dep].add(pack)
    return dep_dict

# Old - not used
def register_results(results: list[list[bool]], pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, terminal:bool=True, external_file:bool=False, file_name:str="results.txt", file_mode:str="a") -> None:
    avaluation_values:list[int] = [evaluate_packs(pack_benefits, pack_dep, sol) for sol in results]
    capacities_left:list[int] = [get_remaining_capacity([dep_size for dep_size in dep_sizes], sol, capacity) for sol in results]
    
    with open(file_name, file_mode) as file:
        for i, sol in enumerate(results):
            if terminal:
                print(f"Solution {i+1}: Benefit = {avaluation_values[i]}, Capacity left = {capacities_left[i]}, Selected dependencies = {[index for index, val in enumerate(sol) if val]}")
            if external_file:
                file.write(f"Solution {i+1}: Benefit = {avaluation_values[i]}, Capacity left = {capacities_left[i]}, Selected dependencies = {[index for index, val in enumerate(sol) if val]}\n")
    pass

# Load instance data from file
def load_instance(filename: str) -> tuple[list[int], list[int], list[tuple[int, int]], int]:
    with open(filename, 'r') as file:
        num_pack, num_dep, num_pack_dep, capacity = map(int, file.readline().split())
        pack_benefits: list[int] = list(map(int, file.readline().split()))
        dep_sizes: list[int] = list(map(int, file.readline().split()))
        pack_dep: list[tuple[int, int]] = [(p, d) for line in file if len(line.split()) == 2 for p, d in [map(int, line.split())]]
    return pack_benefits, dep_sizes, pack_dep, capacity

# Read last run_id from CSV, increment, return new ID
def get_next_run_id_number(experiment_type: str, output_dir: Path) -> int:
    csv_file: Path = output_dir / f"{experiment_type}.csv"
    
    if not csv_file.exists():
        return 1
    
    # Read last row to get last ID
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        rows: list[dict[str, str]] = list(reader)
        
        if not rows:
            return 1
        
        last_id: str = rows[-1]["run_id"] # gets value from run_id in the last row 
        last_num: int = int(last_id.split("_")[-1]) # gets last segment from the split (experiment, type, number)
        return last_num + 1

# Append new results to existing .csv or create new file
def append_to_csv(experiment_type: str, new_results: list[dict[str, Any]], output_dir) -> None:
    csv_file: Path = output_dir / f"{experiment_type}.csv"
    fieldnames: list[str] = list(new_results[0].keys())
    
    file_exists: bool = csv_file.exists()
    
    with open(csv_file, "a", newline='') as f: # "a" is for append
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(new_results)