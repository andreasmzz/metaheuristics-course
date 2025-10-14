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
import simulated_annealing as sa
import genetic_algorithm as ga

# Configuration
OUTPUT_DIR: Path = Path("output/experiments")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Run all constructive method experiments and save to .csv -> First report
def run_constructive_experiment(files:list[str], files_to_run: list[int]) -> None:
    for file_id in files_to_run:
        if file_id >= len(files): break
        print("Starting constructive experiments...")
        
        pack_benefits, dep_sizes, pack_dep, capacity = aux.load_instance(files[file_id])
        
        results: list[dict[str, Any]] = []
        run_id: int = aux.get_next_run_id_number("constructive", OUTPUT_DIR)
        
        # Ignored for now
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
                "instance_file": files[file_id],
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
                    "instance_file": files[file_id],
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
def run_local_search_experiment(files:list[str], files_to_run: list[int]) -> None:
    print("Starting local search experiments...")
    for file_id in files_to_run:
        pack_benefits, dep_sizes, pack_dep, capacity = aux.load_instance(files[file_id])
        
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
                        dep_sizes=dep_sizes,
                        pack_dep=pack_dep,
                        capacity=capacity,
                        refinement_heuristics=exp["refinement_funcs"],
                        neighborhood_names=exp["neighborhoods"],
                        time_limit=30.0,
                        max_tries=1000
                    )
                elif exp["ls_method"] == "variable_neighborhood_descent":
                    final_move = ls.variable_neighborhood_descent(
                        sol=initial_sol,
                        pack_benefits=pack_benefits,
                        dep_sizes=dep_sizes,
                        pack_dep=pack_dep,
                        capacity=capacity,
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
                capacity_ramaining:int = aux.get_remaining_capacity(dep_sizes, final_move[0], capacity)

                results.append({
                    "run_id": f"local_search_{run_id}",
                    "instance_file": files[file_id],
                    "ls_method": exp["ls_method"],
                    "refinement_heuristics": str(exp["refinement_names"]),
                    "neighborhoods": str(exp["neighborhoods"]),
                    "initial_method": "create_ratio_greedy_solution",
                    "seed": seed,
                    "initial_benefit": initial_benefit,
                    "final_benefit": final_benefit,
                    "improvement": improvement,
                    "improvement_pct": improvement_pct,
                    "capacity_remaining": capacity_ramaining,
                    "time": elapsed,
                    "evaluations": evals,
                    "timestamp": datetime.now().isoformat()
                })
                run_id += 1
            print(f"    Completed 30 runs for {exp["ls_method"]}")
        
        # Save to .csv
        aux.append_to_csv("local_search", results, OUTPUT_DIR)

    print(f" OK Local search experiments complete! Saved to local_search.csv\n")

# Runs simulated annealing 30 times on all files and saves each run to .csv -> Third report
# outer_time_limit: may stop without getting through every file -> no solution for files
# inner_time_timit: may stop a SA before lowering temperature enough -> solution not good enough
def run_simulated_annealing_experiment(files:list[str], files_to_run:list[int], outer_time_limit:float, inner_time_limit:float, runs_per_file:int) -> None:
    outer_start_time:float = time.time()
    print("Starting simulated annealing experiments...")
    
    run_with_initial_temp:bool = False # if false: will use useful_temp found in first run per file-parameters
    
    # Parameters to be tested:
    test_alpha:list[float] = [0.95, 0.75]
    test_beta:list[float] = [1.5, 2.0]
    test_gamma:list[float] = [0.9, 0.8]
    test_initial_temp:list[int] = [1000, 500]


    for file_id in files_to_run:
        if outer_time_limit < time.time() - outer_start_time: break
        if file_id >= len(files): break
            
        pack_benefits, dep_sizes, pack_dep, capacity = aux.load_instance(files[file_id])
        
        results: list[dict[str, Any]] = [] # for each file
        run_id: int = aux.get_next_run_id_number("simulated_annealing", OUTPUT_DIR)
        seed: int = aux.get_next_seed_per_file_name("simulated_annealing", files[file_id], OUTPUT_DIR)
        
        for alpha in test_alpha:
            for beta in test_beta:
                for gamma in test_gamma:
                    for initial_temp in test_initial_temp:



                        for run in range(runs_per_file):
                            inner_start_time:float = time.time()
                            if outer_time_limit < time.time() - outer_start_time or inner_time_limit < time.time() -  inner_start_time: break
                            run_seed: int = aux.get_next_seed_per_file_name("simulated_annealing", files[file_id], OUTPUT_DIR)
                            random.seed(run_seed)
                            aux.reset_evaluation_count()
                        

                            if run_with_initial_temp or run == 0:
                                (useful_temp, starting_temperature, beta, gamma) = sa.find_initial_temperature(
                                        sol = fs.create_randomic_solution(pack_benefits, dep_sizes, pack_dep, capacity),
                                        pack_benefits = pack_benefits,
                                        dep_sizes = dep_sizes,
                                        pack_dep = pack_dep,
                                        capacity = capacity,
                                        beta = beta,
                                        gamma = gamma,
                                        initial_temperature = initial_temp,
                                        time_limit = inner_time_limit - time.time() + inner_start_time)

                            (solution, benefit, initial_temperature, final_temperature, alpha) = sa.simulated_annealing(
                                sol = fs.create_randomic_solution(pack_benefits, dep_sizes, pack_dep, capacity),
                                pack_benefits = pack_benefits,
                                dep_sizes = dep_sizes,
                                pack_dep = pack_dep,
                                capacity = capacity,
                                initial_temperature = useful_temp, # type: ignore
                                alpha = alpha,
                                time_limit = inner_time_limit - time.time() + inner_start_time
                                )
                            
                            elapsed: float = time.time() - inner_start_time # takes find initial temp into account, since it's done for every run
                            evals: int = aux.get_evaluation_count()
                            capacity_used: int = capacity - aux.get_remaining_capacity(dep_sizes, solution, capacity)
                            
                            results.append({
                                "run_id": f"simulated_annealing_{run_id}",
                                "instance_file": files[file_id],
                                "run_seed": run_seed,
                                "solution": aux.list_bool_to_int(solution),
                                "benefit": benefit,
                                "starting_find_temp": starting_temperature, # tracking find temperature is that important? # type: ignore
                                "initial_temp": initial_temperature,
                                "final_temp": final_temperature,
                                "alpha": alpha,
                                "beta": beta,
                                "gamma": gamma,
                                "run_finding_initial_temp": run_with_initial_temp,
                                "start_time": inner_start_time,
                                "time": elapsed,
                                "evaluations": evals,
                                "capacity_used": capacity_used,
                                "timestamp": datetime.now().isoformat()})

                            print(f"  Run_id:{run_id} Seed: {run_seed} run for {files[file_id]} in {elapsed/60}min - Benefit: {benefit}")
                            print(f"\tAlpha={alpha}, Beta={beta}, Gamma={gamma}, Start_temp={initial_temp}")
                            run_id += 1

                            # Save to .csv
                            aux.append_to_csv("simulated_annealing", results, OUTPUT_DIR)



        print(f" OK Simulated annealing experiments complete! Saved to simulated_annealing.csv\n")


#
def run_genetic_algorithm_experiment(files:list[str], files_to_run:list[int], outer_time_limit:float, inner_time_limit:float, runs_per_file:int, verbose:bool = False) -> None:
    outer_start_time:float = time.time()
    print("Starting genetic algorithm experiments...")
    for file_id in files_to_run:
        if outer_time_limit < time.time() - outer_start_time: break
        if file_id >= len(files): break
            
        pack_benefits, dep_sizes, pack_dep, capacity = aux.load_instance(files[file_id])
        
        results: list[dict[str, Any]] = [] # for each file
        run_id: int = aux.get_next_run_id_number("genetic_algorithm", OUTPUT_DIR)
        seed: int = aux.get_next_seed_per_file_name("genetic_algorithm", files[file_id], OUTPUT_DIR)
            
        for run in range(runs_per_file):
            inner_start_time:float = time.time()
            if outer_time_limit < time.time() - outer_start_time or inner_time_limit < time.time() -  inner_start_time: break
            run_seed:int = seed+run
            random.seed(run_seed)
            aux.reset_evaluation_count()

            (solution, benefit, initial_sol, neighborhood_names, generations, elite_number, parents_per_generation, 
             parents_survive, parent_selection_name, two_offsprings, crossover_points, mutation, mutations_per_gene, time_limit) = ga.genetic_algorithm(
                sol = [],
                pack_benefits = pack_benefits,
                dep_sizes = dep_sizes,
                pack_dep = pack_dep,
                capacity = capacity,
                time_limit = inner_time_limit - time.time() + inner_start_time,
                elite_number=0,
                parents_survive=False,
                mutation = 0.1, # 10%
                mutations_per_gene = 10, # 10 bits will change,
                verbose = verbose)
            
            elapsed: float = time.time() - inner_start_time # takes find initial temp into account, since it's done for every run
            evals: int = aux.get_evaluation_count()
            capacity_used: int = capacity - aux.get_remaining_capacity(dep_sizes, solution, capacity)
            
            results.append({
                "run_id": f"genetic_algorithm_{run_id}",
                "instance_file": files[file_id],
                "run_seed": run_seed,
                "solution": aux.list_bool_to_int(solution),
                "benefit": benefit,
                "initial_sol": aux.list_bool_to_int(initial_sol),
                "initial_sol_neighborhood": neighborhood_names,
                "generations": generations,
                "elite_number": elite_number,
                "parents_per_generation": parents_per_generation,
                "parents_survive": parents_survive,
                "parent_selection": parent_selection_name,
                "two_offsprings": two_offsprings,
                "crossover_points": crossover_points,
                "mutation_rate": mutation,
                "mutations_per_gene": mutations_per_gene,
                "start_time": inner_start_time,
                "time": elapsed,
                "evaluations": evals,
                "capacity_used": capacity_used,
                "timestamp": datetime.now().isoformat()})

            print(f"  [{run_id}] {run_seed} run for {files[file_id]} - Benefit: {benefit}")
            run_id += 1

        # Save to .csv
        aux.append_to_csv("genetic_algorithm", results, OUTPUT_DIR)

        print(f" OK Genetic algorithm experiments complete! Saved to genetic_algorithm.csv\n")
