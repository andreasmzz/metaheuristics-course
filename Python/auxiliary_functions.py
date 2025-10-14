# Python 3.13.4

import csv
import random
import time
from pathlib import Path
from typing import Any

''' Global varibales '''

# Used on every run to track performance
_evaluation_count:int = 0

# Module-level GA debug state to ensure a single CSV writer/file per process
#_ga_debug_state: dict | None = None

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
    return (pack_benefits, dep_sizes, pack_dep, capacity)

# Read last run_id from CSV, increment, return new ID
def get_next_run_id_number(experiment_type: str, output_dir: Path) -> int:
    csv_file: Path = output_dir / f"{experiment_type}.csv"
    
    if not csv_file.exists():
        return 0
    
    # Read last row to get last ID
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        rows: list[dict[str, str]] = list(reader)
        
        if not rows:
            return 1
        
        last_id: str = rows[-1]["run_id"] # gets value from run_id in the last row 
        last_num: int = int(last_id.split("_")[-1]) # gets last segment from the split (experiment, type, number)
        return last_num + 1

#
def get_next_seed_per_file_name(experiment_type: str, file_name: str, output_dir: Path) -> int:
    csv_file: Path = output_dir / f"{experiment_type}.csv"
    
    if not csv_file.exists():
        return 0
    
    # Read all rows to get max seed for the file
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        rows: list[dict[str, str]] = list(reader)
        
        if not rows:
            return 0
        # Collect seeds from rows that match the instance file. Some CSVs use
        # the header 'seed' while others (newer experiments) use 'run_seed'.
        seeds_for_file: list[int] = []
        for row in rows:
            try:
                if row.get("instance_file") != file_name:
                    continue
                # prefer 'run_seed' if present, fall back to 'seed'
                val = row.get("run_seed") if row.get("run_seed") not in (None, "") else row.get("seed")
                if val in (None, ""):
                    continue
                seeds_for_file.append(int(val))
            except (ValueError, TypeError):
                # skip malformed seed values
                continue

        if not seeds_for_file:
            return 0
        
        return max(seeds_for_file) + 1

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

# 
def list_bool_to_int(sol:list[bool]) -> int:
    # Defensive: if sol is None or empty, return 0
    if sol is None:
        return 0
    if len(sol) == 0:
        return 0

    # Build bitstring safely and convert. Use a fallback integer build to avoid
    # ValueError from int('', 2) in edge cases.
    try:
        bits: str = "".join(str(int(bool(b))) for b in sol)
        return int(bits, 2) if bits else 0
    except Exception:
        # Fallback: compute integer by shifting bits (most-significant-bit first)
        val: int = 0
        for b in sol:
            val = (val << 1) | (1 if b else 0)
        return val

#
def int_to_list_bool(sol:int) -> list[bool]:
    num_bits = max(len(bin(sol)[2:]), 1)
    return [bool(int(bit)) for bit in bin(sol)[2:].zfill(num_bits)]

'''
def ga_debug_report(gen: int, population: list[list[bool]], population_fitness: list[int], pack_benefits: list[int], pack_dep: list[tuple[int, int]], dep_sizes: list[int], capacity: int, verbose: bool = False, debug_state: dict | None = None, sample_n: int = 5, print_to_stdout: bool = True) -> dict | None:
    """Verbose-only GA diagnostics and optional CSV logging.

    debug_state is a mutable dict used to persist the CSV writer and file handle
    across multiple calls. Callers should pass the returned debug_state back on
    subsequent calls and pass it to ga_debug_close(debug_state) at the end.

    Returns the (possibly initialized) debug_state or None if not used.
    """
    # allow assignment to module-level singleton
    global _ga_debug_state

    # If not verbose and no CSV requested, do nothing
    if not verbose and debug_state is None and _ga_debug_state is None:
        return debug_state

    import statistics as _stats
    from pathlib import Path
    try:
        top5 = sorted(population_fitness, reverse=True)[:5]
        avg = _stats.mean(population_fitness) if population_fitness else 0.0
        med = _stats.median(population_fitness) if population_fitness else 0.0
        std = _stats.stdev(population_fitness) if len(population_fitness) > 1 else 0.0
        unique_fitness = len(set(population_fitness))
        unique_individuals = len(set(map(tuple, population))) if population else 0

        # Phenotype diagnostics (satisfied packages per individual)
        unique_phenotypes = -1
        try:
            pack_all_deps = get_pack_dict(pack_dep)
            phenotypes = []
            for ind in population:
                selected_set = set(i for i, v in enumerate(ind) if v)
                satisfied = tuple(sorted([p for p, deps in pack_all_deps.items() if deps.issubset(selected_set)]))
                phenotypes.append(satisfied)
            unique_phenotypes = len(set(phenotypes))
        except Exception:
            unique_phenotypes = -1

        uph = unique_phenotypes if unique_phenotypes >= 0 else 'n/a'
        if print_to_stdout:
            print(f"[GA DEBUG] gen={gen} top5={top5} avg={avg:.2f} med={med:.2f} std={std:.2f} unique_fitness={unique_fitness} unique_individuals={unique_individuals} unique_phenotypes={uph}")

        if print_to_stdout:
            if avg == 0:
                print(f"[GA WARNING] average fitness is 0 at generation {gen}")
            if unique_individuals <= 1 and len(population) > 0:
                print(f"[GA WARNING] population is homogeneous at generation {gen}")
            try:
                if unique_phenotypes >= 0 and unique_phenotypes < unique_individuals:
                    print(f"[GA NOTE] genotype->phenotype collapse: unique_individuals={unique_individuals} unique_phenotypes={unique_phenotypes}")
            except Exception:
                pass

        # quick check: best individual all-false?
        if population_fitness:
            best_idx = max(range(len(population_fitness)), key=lambda i: population_fitness[i])
            if print_to_stdout and sum(1 for b in population[best_idx] if b) == 0:
                print(f"[GA WARNING] best individual is all-False at generation {gen}")

            # Sample a few individuals to inspect genotype -> phenotype mapping
            try:
                best_ind = population[best_idx]
                sample_indices = random.sample(range(len(population)), min(sample_n, len(population)))
                for si in sample_indices:
                    ind = population[si]
                    fit = population_fitness[si]
                    selected = [i for i, v in enumerate(ind) if v]
                    ham = sum(1 for a, b in zip(ind, best_ind) if a != b)
                    if print_to_stdout:
                        print(f"[GA SAMPLE] idx={si} fitness={fit} selected_count={len(selected)} selected_preview={selected[:10]} hamming_to_best={ham}")
            except Exception:
                pass

        # Prepare or use debug_state for CSV logging. Prefer the module-level
        # singleton so multiple GA runs in the same process append to the same file.
        global _ga_debug_state
        if debug_state is None and _ga_debug_state is not None:
            debug_state = _ga_debug_state

        if debug_state is None:
            debug_state = {}

        try:
            if 'writer' not in debug_state:
                out_dir = Path('output') / 'analysis'
                out_dir.mkdir(parents=True, exist_ok=True)
                csv_path = out_dir / f"ga_debug.csv"
                file_exists = csv_path.exists()
                f = open(csv_path, 'a', newline='')
                writer = csv.DictWriter(f, fieldnames=["gen", "top5", "avg", "med", "std", "unique_fitness", "unique_individuals", "unique_phenotypes"])
                if not file_exists:
                    writer.writeheader()
                debug_state['file'] = f
                debug_state['writer'] = writer
                # persist singleton
                _ga_debug_state = debug_state

            # write row
            try:
                writer = debug_state.get('writer')
                if writer:
                    writer.writerow({
                        'gen': gen,
                        'top5': ','.join(str(x) for x in top5),
                        'avg': f"{avg:.2f}",
                        'med': f"{med:.2f}",
                        'std': f"{std:.2f}",
                        'unique_fitness': unique_fitness,
                        'unique_individuals': unique_individuals,
                        'unique_phenotypes': unique_phenotypes if unique_phenotypes >= 0 else 'n/a'
                    })
            except Exception:
                pass
        except Exception:
            # don't fail because of logging
            pass

        # control terminal printing separately (backwards compatible)
        if not print_to_stdout:
            return debug_state

        return debug_state
    except Exception:
        # Keep non-fatal for GA runs
        return debug_state


def ga_debug_close(debug_state: dict | None) -> None:
    """Close any open CSV writer/file created by ga_debug_report."""
    if not debug_state:
        return
    try:
        f = debug_state.get('file')
        if f is not None:
            f.close()
    except Exception:
        pass
    # clear module-level singleton if it matches
    global _ga_debug_state
    try:
        if _ga_debug_state is debug_state:
            _ga_debug_state = None
    except Exception:
        pass
        
'''