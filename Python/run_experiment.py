# Python 3.13.4

import random
import time
import csv
from datetime import datetime
from pathlib import Path
from typing import Any

import first_solution as fs
import auxiliary_functions as aux
import local_search as ls
import refinement_heuristic as rh

# Configuration
INSTANCE_FILE:list[str] = [
    "input/prob-software-85-100-812-12180.txt"
]
OUTPUT_DIR: Path = Path("output/experiments")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Run all constructive method experiments and save to .csv -> First report
def run_constructive_experiment() -> None:
    print("Starting constructive experiments...")
    pack_benefits, dep_sizes, pack_dep, capacity = aux.load_instance(INSTANCE_FILE[0])
    
    results: list[dict[str, Any]] = []
    run_id: int = aux.get_next_run_id_number("constructive", OUTPUT_DIR)
    
    # DIgnored for now
    deterministic_methods: list[tuple[str, dict[str, bool]]] = [
        ("create_ratio_greedy_solution", {"biggest_first": True}),
        ("create_ratio_greedy_solution", {"biggest_first": False}), # but this duality would have been good to explore
        ("create_dep_size_greedy_solution", {"biggest_first": False}),
        ("create_pack_benefit_greedy_solution", {"biggest_first": True}),
        ("create_num_pack_greedy_solution", {"biggest_first": True})
    ]
    
    for method_name in fs.deterministic_first_solutions_list:
        aux.reset_evaluation_count()
        start_time: float = time.time()
        
        solution: list[bool] = fs.create_first_solution(method_name, pack_benefits, dep_sizes, pack_dep, capacity, "default")
        
        elapsed: float = time.time() - start_time
        benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, solution)
        evals: int = aux.get_evaluation_count()
        capacity_used: int = capacity - aux.get_remaining_capacity(dep_sizes, solution, capacity)
        
        results.append({
            "run_id": f"constructive_{run_id}",
            "instance_file": INSTANCE_FILE[0],
            "method": method_name,
            "params": "default",
            "seed": None,
            "benefit": benefit,
            "time": elapsed,
            "evaluations": evals,
            "capacity_used": capacity_used,
            "timestamp": datetime.now().isoformat()
        })
        print(f"  [{run_id}] {method_name} default - Benefit: {benefit}")
        run_id += 1
    
    # Randomized methods - 30 runs each
    randomized_methods: list[str] = [
        "create_randomic_solution",
        "create_randomized_ratio_greedy_solution",
        "create_randomized_dep_size_greedy_solution",
        "create_randomized_pack_benefit_greedy_solution",
        "create_randomized_num_pack_greedy_solution"
    ]
    
    for method_name in fs.randomized_first_solutions_list:
        print(f"  Running {method_name} - 30 runs...")
        for seed in range(30):
            random.seed(seed)
            aux.reset_evaluation_count()
            start_time = time.time()
            
            solution = fs.create_first_solution(method_name, pack_benefits, dep_sizes, pack_dep, capacity)
            
            elapsed = time.time() - start_time
            benefit = aux.evaluate_packs(pack_benefits, pack_dep, solution)
            evals = aux.get_evaluation_count()
            capacity_used = capacity - aux.get_remaining_capacity(dep_sizes, solution, capacity)
            
            results.append({
                "run_id": f"constructive_{run_id}",
                "instance_file": INSTANCE_FILE[0],
                "method": method_name,
                "params": "{}",
                "seed": seed,
                "benefit": benefit,
                "time": elapsed,
                "evaluations": evals,
                "capacity_used": capacity_used,
                "timestamp": datetime.now().isoformat()
            })
            run_id += 1
        print(f"    Completed 30 runs for {method_name}")
    
    # Save to .csv
    aux.append_to_csv("constructive", results, OUTPUT_DIR)

    print(f" OK Constructive experiments complete! Saved to constructive.csv\n")

# Runs a specific set of 4 runs and saves to .csv -> Second report
def run_local_search_experiment() -> None:
    print("Starting local search experiments...")
    pack_benefits, dep_sizes, pack_dep, capacity = aux.load_instance(INSTANCE_FILE[0])
    
    results: list[dict[str, Any]] = []
    run_id: int = aux.get_next_run_id_number("local_search", OUTPUT_DIR)
    
    # Configuration: 2 local search * 2 setups each * 30 runs
    experiments: list[dict[str, Any]] = [
        {
            "ls_method": "hill_climbing",
            "refinement_names": ["random_best_step"],
            "refinement_funcs": [rh.random_best_step],
            "neighborhoods": ["flip_bit", "swap_bits"],
        },
        {
            "ls_method": "hill_climbing",
            "refinement_names": ["first_best_step"],
            "refinement_funcs": [rh.first_best_step],
            "neighborhoods": ["flip_bit"],
        },
        {
            "ls_method": "variable_neighborhood_descent",
            "refinement_names": ["random_best_step", "first_best_step"],
            "refinement_funcs": [rh.random_best_step, rh.first_best_step],
            "neighborhoods": ["flip_bit", "swap_bits"],
        },
        {
            "ls_method": "variable_neighborhood_descent",
            "refinement_names": ["absolute_best_step"],
            "refinement_funcs": [rh.absolute_best_step],
            "neighborhoods": ["flip_bit"],
        }
    ]
    
    for exp in experiments:
        label: str = f"{exp['ls_method']}_{'_'.join(exp['refinement_names'])}_{'_'.join(exp['neighborhoods'])}"
        print(f"  Running {label} - 30 runs...")
        
        for seed in range(30):
            random.seed(seed)
            aux.reset_evaluation_count()
            
            # Generate initial solution
            initial_sol: list[bool] = fs.create_first_solution("create_ratio_greedy_solution", pack_benefits, dep_sizes, pack_dep, capacity)
            initial_benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, initial_sol)
            
            # Apply local search
            start_time: float = time.time()

            # This needs to be generalized as soon as possible !!
            if exp["ls_method"] == "hill_climbing":
                final_move = ls.hill_climbing(
                    sol=initial_sol,
                    pack_benefits=pack_benefits,
                    pack_dep=pack_dep,
                    refinement_heuristics=exp["refinement_funcs"],
                    neighborhood_names=exp["neighborhoods"],
                    time_limit=30.0,
                    max_tries=1000
                )
            elif exp["ls_method"] == "variable_neighborhood_descent":
                final_move = ls.variable_neighborhood_descent(
                    sol=initial_sol,
                    pack_benefits=pack_benefits,
                    pack_dep=pack_dep,
                    refinement_heuristics=exp["refinement_funcs"],
                    neighborhood_names=exp["neighborhoods"],
                    time_limit=30.0,
                    max_tries=1000
                )
            else:
                raise ValueError(f"Unknown local search method: {exp['ls_method']}")

            ''' Find a way to make this work
            final_move = ls.local_search_dict[exp["ls_method"]](
                sol=initial_sol,
                pack_benefits=pack_benefits,
                pack_dep=pack_dep,
                refinement_heuristics=exp["refinement_funcs"],
                neighborhood_names=exp["neighborhoods"],
                time_limit=30.0,
                max_tries=1000
            )
            '''

            elapsed: float = time.time() - start_time
            
            final_benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, final_move[0])
            evals: int = aux.get_evaluation_count()
            improvement: int = final_benefit - initial_benefit
            improvement_pct: float = 100.0 * improvement / initial_benefit if initial_benefit > 0 else 0.0
            
            results.append({
                "run_id": f"local_search_{run_id}",
                "instance_file": INSTANCE_FILE[0],
                "ls_method": exp["ls_method"],
                "refinement_heuristics": str(exp["refinement_names"]),
                "neighborhoods": str(exp["neighborhoods"]),
                "initial_method": "create_ratio_greedy_solution",
                "seed": seed,
                "initial_benefit": initial_benefit,
                "final_benefit": final_benefit,
                "improvement": improvement,
                "improvement_pct": improvement_pct,
                "time": elapsed,
                "evaluations": evals,
                "timestamp": datetime.now().isoformat()
            })
            run_id += 1
        print(f"    Completed 30 runs for {exp["ls_method"]}")
    
    # Save to .csv
    aux.append_to_csv("local_search", results, OUTPUT_DIR)

    print(f" OK Local search experiments complete! Saved to local_search.csv\n")