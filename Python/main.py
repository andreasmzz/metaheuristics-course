# Python 3.13.4

import time
import pprint

import auxiliary_functions as aux
import move
import first_solution as fs
import simulated_annealing as sa
import run_experiment
import analyze_results

import dp

csv_files_paths:list[str] = [
    "output/experiments/constructive.csv",
    "output/experiments/local_search.csv",
    "output/experiments/simulated_annealing.csv",
    "output/experiments/genetic_algorithm.csv"
]

file_names:list[str] = [
    "input/prob-software-85-100-812-12180.txt", # 00
    "input/sukp03_100_100_0.10_0.75.txt",       # 01
    "input/sukp06_200_200_0.10_0.75.txt",       # 02
    "input/sukp12_400_400_0.10_0.75.txt",       # 03
    "input/sukp18_100_100_0.15_0.85.txt",       # 04
    "input/sukp24_300_300_0.15_0.85.txt",       # 05
    "input/sukp29_500_485_0.15_0.85.txt",       # 06
    "input/sukp02_100_85_0.10_0.75.txt",        # 07
    "input/sukp07_285_300_0.10_0.75.txt",       # 08
    "input/sukp28_485_500_0.15_0.85.txt",       # 09
]

BIGGER_TIME_LIMIT: float = 10.0 *60.0 # change only the minutes
SMALLER_TIME_LIMIT: float = 1.0 *60.0 # change only the minutes



''' Input file format:'''

# 1st line = num_pack num_dep num_pack_dep capacity -> int, int, int, int
# 2nd line = num_pack pack_benefits                 -> list[int]
# 3rd line = num_dep dep_sizes                      -> list[int]
# num_pack_dep lines = pack_id dep_id               -> pack_dep:list[tuple[int]] = [(pack_id, dep_id)]

''' Variables format: '''

# pack_benefits:    list[int] =             [pack_0_benefit, pack_1_benefit, ..., pack_0_benefit_(num_pack-1)]
# dep_sizes:        list[int] =             [dep_0_size, dep_1_size, ..., dep_0_size_(num_dep-1)]
# pack_dep:         list[tuple[int, int]] = [(pack_id, dep_id), ...]
# select_dep:       list[bool] =            [False, False, ..., False] (length = num_dep)
# free_space:       int =                   capacity - sum(dep_sizes[i] for i in range(len(select_dep)) if select_dep[i])

''' Solution format: '''

# select_dep:   list[bool] =    [False, False, ..., False] (length = num_dep)
#   if a select_dep[i] is True, then dep_i is a dep selected to be installed



   

# Run current relevant experiments and their analysis
def main() -> None:
    start_time:float = time.time()
    outer_time_limit:float = BIGGER_TIME_LIMIT
    inner_time_limit: float = SMALLER_TIME_LIMIT

    
    print("Test")
    # for test only use
    pack_benefits02, dep_sizes02, pack_dep02, capacity02 = aux.load_instance(file_names[7])
    pack_benefits07, dep_sizes07, pack_dep07, capacity07 = aux.load_instance(file_names[8])
    pack_benefits28, dep_sizes28, pack_dep28, capacity28 = aux.load_instance(file_names[9])

    count:int = 0
    best_sol:list[bool] = []
    best_sol_eval: int = 0
    new_temp:float = 0.0

    print("Starting all experiments\n")
    #run_experiment.run_constructive_experiment(file_names, [7, 8, 9])
    #run_experiment.run_local_search_experiment(file_names, [7, 8, 9], 3)
    #run_experiment.run_simulated_annealing_experiment(file_names, [7, 8, 9], outer_time_limit, inner_time_limit, 3)
    #run_experiment.run_iterated_local_search(file_names, [9], outer_time_limit, inner_time_limit, 3)
    
    #analyze_results.analyze_constructive()
    #analyze_results.analyze_local_search()
    #analyze_results.analyze_simulated_annealing()
    #analyze_results.analyze_iterated_local_search()

    #analyze_results.analyze_best_runs_per_instance()
    
    sol02 = 38232241861191956890123770
    sol07 = 1622252848154648481779052703966520678253594508686293007238790315653024432251702490831218685
    sol28 = 3247810853942772854849805152669990462352800874858491026973391874935536644212212298334294083651391478398907758046693351966416062716417065771926573546495

    print(f"Sol 02 benefit: {aux.evaluate_packs(pack_benefits02, pack_dep02, aux.int_to_list_bool(sol02, len(dep_sizes02)))}")
    print(f"Sol 07 benefit: {aux.evaluate_packs(pack_benefits07, pack_dep07, aux.int_to_list_bool(sol07, len(dep_sizes07)))}")
    print(f"Sol 28 benefit: {aux.evaluate_packs(pack_benefits28, pack_dep28, aux.int_to_list_bool(sol28, len(dep_sizes28)))}")
    print()
    print(f"Sol 02 space left: {aux.get_remaining_capacity(dep_sizes02, aux.int_to_list_bool(sol02, len(dep_sizes02)), capacity02)}")
    print(f"Sol 07 space left: {aux.get_remaining_capacity(dep_sizes07, aux.int_to_list_bool(sol07, len(dep_sizes07)), capacity07)}")
    print(f"Sol 28 space left: {aux.get_remaining_capacity(dep_sizes28, aux.int_to_list_bool(sol28, len(dep_sizes28)), capacity28)}")
    print()
    print("Sol 02 to int list: ", aux.int_to_list_int(sol02, len(dep_sizes02)))
    print("Sol 07 to int list: ", aux.int_to_list_int(sol07, len(dep_sizes07)))
    print("Sol 28 to int list: ", aux.int_to_list_int(sol28, len(dep_sizes28)))
    print()
    print("Pack sol 02: ", aux.list_bool_to_list_int(aux.get_package_solution(aux.int_to_list_bool(sol02, len(dep_sizes02)), pack_benefits02, pack_dep02)))
    print("Pack sol 07: ", aux.list_bool_to_list_int(aux.get_package_solution(aux.int_to_list_bool(sol07, len(dep_sizes07)), pack_benefits07, pack_dep07)))
    print("Pack sol 28: ", aux.list_bool_to_list_int(aux.get_package_solution(aux.int_to_list_bool(sol28, len(dep_sizes28)), pack_benefits28, pack_dep28))) 

    '''
    print("Starting ILS")
    run_experiment.run_iterated_local_search(file_names, [7, 8, 9], outer_time_limit, inner_time_limit, 3)
    print("Ended ILS")
    '''

    #run_experiment.run_constructive_experiment(file_names, [7,8,9])

    #pprint.pprint(aux.get_best_benefit_row_per_instance(csv_files_paths[0]))
    
    
    '''
    a02 = [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1]
    a07 = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    a28 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    '''
    '''
    new_sol:list[bool] = fs.create_randomic_solution(pack_benefits, dep_sizes, pack_dep, capacity)
    
    new_sol:list[bool] = [False for i in range(len(dep_sizes))]
    space_left:int = capacity
    for (pack, dep) in pack_dep:
        if space_left > dep_sizes[dep]:
            if not new_sol[dep]:
                new_sol[dep] = True
                space_left -= dep_sizes[dep]

    
    print("Packages benefits: ", pack_benefits)
    print("\nDependencies sizes: ", dep_sizes)
    #print("\nPackage and one of its dependencies: ", pack_dep)
    print("Disk capacity: ", capacity)
    
    print("\nFirst solution: ", (new_sol))
    print("\nBenefits: ", aux.evaluate_packs(pack_benefits, pack_dep, new_sol))
    print("Space left: ", aux.get_remaining_capacity(dep_sizes, new_sol, capacity))
    '''

    # problematic instances: 3, 5 and 6

    #run_experiment.run_simulated_annealing_experiment(file_names, [3, 5, 6], outer_time_limit, inner_time_limit, 5)

    '''
    # Perfect solution
    #sol = dp.solve_sukp(pack_benefits, dep_sizes, pack_dep, capacity)
    #print("For the perfect solution")
    #print(f"Sol: {aux.list_bool_to_int(sol)}\n\tBenefict: {aux.evaluate_packs(pack_benefits, pack_dep, sol)}\n\n")

    print("TEST FOR FIRST SOLUTIONS\n")

    # RATIO GREDDY
    sol1 = fs.create_ratio_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity, False) # terrible - 0
    sol2 = fs.create_ratio_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity, True) # terrible - 748

    print("For create greedy solution")
    print(f"For sol1: \n\tSol: {aux.list_bool_to_int(sol1)}\n\tBenefit: {aux.evaluate_packs(pack_benefits, pack_dep, sol1)}")
    print(f"For sol2: \n\tSol: {aux.list_bool_to_int(sol2)}\n\tBenefit: {aux.evaluate_packs(pack_benefits, pack_dep, sol2)}\n\n")
    
    # DEP SIZE
    sol1 = fs.create_dep_size_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity, False) # baD - 1032
    sol2 = fs.create_dep_size_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity, True) # terrible - 0 

    print("For create dep size greddy solution")
    print(f"For sol1: \n\tSol: {aux.list_bool_to_int(sol1)}\n\tBenefit: {aux.evaluate_packs(pack_benefits, pack_dep, sol1)}")
    print(f"For sol2: \n\tSol: {aux.list_bool_to_int(sol2)}\n\tBenefit: {aux.evaluate_packs(pack_benefits, pack_dep, sol2)}\n\n")

    # PACK BENEFIT
    sol1 = fs.create_pack_benefit_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity, False) # bad - 1109
    sol2 = fs.create_pack_benefit_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity, True) # acceptable - 6983

    print("For create pack benefit greddy solution")
    print(f"For sol1: \n\tSol: {aux.list_bool_to_int(sol1)}\n\tBenefit: {aux.evaluate_packs(pack_benefits, pack_dep, sol1)}")
    print(f"For sol2: \n\tSol: {aux.list_bool_to_int(sol2)}\n\tBenefit: {aux.evaluate_packs(pack_benefits, pack_dep, sol2)}\n\n")

    # ECONOMIC PACK BENEFIT
    sol1 = fs.create_economic_pack_benefit_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity, False) # bad 1109
    sol2 = fs.create_economic_pack_benefit_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity, True) # acceptable - 6983

    print("For create economic pack benefit greddy solution")
    print(f"For sol1: \n\tSol: {aux.list_bool_to_int(sol1)}\n\tBenefit: {aux.evaluate_packs(pack_benefits, pack_dep, sol1)}")
    print(f"For sol2: \n\tSol: {aux.list_bool_to_int(sol2)}\n\tBenefit: {aux.evaluate_packs(pack_benefits, pack_dep, sol2)}\n\n")

    # NUM PACK
    sol1 = fs.create_num_pack_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity, False) # terrible - 0
    sol2 = fs.create_num_pack_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity, True) # terrible - 0
    print("For num pack greedy solution")
    print(f"For sol1: \n\tSol: {aux.list_bool_to_int(sol1)}\n\tBenefit: {aux.evaluate_packs(pack_benefits, pack_dep, sol1)}")
    print(f"For sol2: \n\tSol: {aux.list_bool_to_int(sol2)}\n\tBenefit: {aux.evaluate_packs(pack_benefits, pack_dep, sol2)}\n\n")
    '''


    #(initial_temp, start_temp, beta, gamma) = sa.find_initial_temperature(new_sol, pack_benefits, dep_sizes, pack_dep, capacity)
    #print(f"found temp: {initial_temp}, start temp: {start_temp}, beta: {beta}, gamma: {gamma}")
    #(found_sol, ) = sa.simulated_annealing(new_sol, pack_benefits, dep_sizes, pack_dep, capacity)


    '''
    # skiped 3, 5 and 6 - each run takes 1.5 minutes without benefit
    run_experiment.run_simulated_annealing_experiment(file_names, [3,5,6], outer_time_limit, inner_time_limit, 3)
    SA_time:float = time.time() - start_time
    print(f"\nEnd of SA the experiment in {SA_time}\n")
    '''

    '''
    run_experiment.run_genetic_algorithm_experiment(file_names, [0, 1, 2, 3, 4, 5, 6], outer_time_limit, inner_time_limit, 1, verbose=True)
    GA_time:float = time.time() - start_time
    print(f"\nEnd of GA the experiment in {GA_time}\n")
    '''

    #analyze_results.analyze_simulated_annealing()
    #analyze_results.analyze_genetic_algorithm()
    #analyze_results.compare_GA_SA()


if __name__ == "__main__":
    print("Main")
    main()


''' Old main
def main() -> None:
    try:
        with open(file_name, 'r') as file:
            num_pack, num_dep, num_pack_dep, capacity = list(map(int, file.readline().split()))
            
            pack_benefits:list[int] = list(map(int, file.readline().split()))
            dep_sizes:list[int] = list(map(int, file.readline().split()))
            pack_dep: list[tuple[int, int]] = [(p, d) for line in file if len(line.split()) == 2 for p, d in [map(int, line.split())]]

            # Sanity checks:
            assert len(pack_benefits) == num_pack, f"Expected {num_pack} package benefits, got {len(pack_benefits)}"
            assert len(dep_sizes) == num_dep, f"Expected {num_dep} dependency sizes, got {len(dep_sizes)}"
            assert len(pack_dep) == num_pack_dep, f"Expected {num_pack_dep} package-dependency pairs, got {len(pack_dep)}"
            assert all(0 <= p < num_pack for p, d in pack_dep), f"Package IDs in pack_dep must be between 0 and {num_pack-1}"
            assert all(0 <= d < num_dep for p, d in pack_dep), f"Dependency IDs in pack_dep must be between 0 and {num_dep-1}"

            # First solution calls:
            sol_randomic: list[bool] = fs.create_randomic_solution(pack_benefits, dep_sizes, pack_dep, capacity)
            sol_ratio_greedy: list[bool] = fs.create_ratio_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity)
            sol_dep_size_greedy: list[bool] = fs.create_dep_size_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity)
            sol_pack_benefit_greedy: list[bool] = fs.create_pack_benefit_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity)
            sol_num_pack_greedy: list[bool] = fs.create_num_pack_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity)
            sol_randomized_ratio_greedy: list[bool] = fs.create_randomized_ratio_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity)
            sol_randomized_dep_size_greedy: list[bool] = fs.create_randomized_dep_size_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity)
            sol_randomized_pack_benefit_greedy: list[bool] = fs.create_randomized_pack_benefit_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity)
            sol_randomized_num_pack_greedy: list[bool] = fs.create_randomized_num_pack_greedy_solution(pack_benefits, dep_sizes, pack_dep, capacity)

            # Evaluate solutions:
            sol_randomic_benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, sol_randomic)
            sol_ratio_greedy_benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, sol_ratio_greedy)
            sol_dep_size_greedy_benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, sol_dep_size_greedy)
            sol_pack_benefit_greedy_benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, sol_pack_benefit_greedy)
            sol_num_pack_greedy_benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, sol_num_pack_greedy)
            sol_randomized_ratio_greedy_benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, sol_randomized_ratio_greedy)
            sol_randomized_dep_size_greedy_benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, sol_randomized_dep_size_greedy)
            sol_randomized_pack_benefit_greedy_benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, sol_randomized_pack_benefit_greedy)
            sol_randomized_num_pack_greedy_benefit: int = aux.evaluate_packs(pack_benefits, pack_dep, sol_randomized_num_pack_greedy)

            # Capacity left:
            sol_randomic_cap_left: int = aux.get_remaining_capacity(dep_sizes, sol_randomic, capacity)
            sol_ratio_greedy_cap_left: int = aux.get_remaining_capacity(dep_sizes, sol_ratio_greedy, capacity)
            sol_dep_size_greedy_cap_left: int = aux.get_remaining_capacity(dep_sizes, sol_dep_size_greedy, capacity)
            sol_pack_benefit_greedy_cap_left: int = aux.get_remaining_capacity(dep_sizes, sol_pack_benefit_greedy, capacity)
            sol_num_pack_greedy_cap_left: int = aux.get_remaining_capacity(dep_sizes, sol_num_pack_greedy, capacity)
            sol_randomized_ratio_greedy_cap_left: int = aux.get_remaining_capacity(dep_sizes, sol_randomized_ratio_greedy, capacity)
            sol_randomized_dep_size_greedy_cap_left: int = aux.get_remaining_capacity(dep_sizes, sol_randomized_dep_size_greedy, capacity)
            sol_randomized_pack_benefit_greedy_cap_left: int = aux.get_remaining_capacity(dep_sizes, sol_randomized_pack_benefit_greedy, capacity)
            sol_randomized_num_pack_greedy_cap_left: int = aux.get_remaining_capacity(dep_sizes, sol_randomized_num_pack_greedy, capacity)

            # Register solution data
            print(f"Randomic Solution: \n\tBenefit: {sol_randomic_benefit} \n\tCapacity left: {sol_randomic_cap_left}")
            print(f"Ratio Greedy Solution: \n\tBenefit: {sol_ratio_greedy_benefit} \n\tCapacity left: {sol_ratio_greedy_cap_left}")
            print(f"Dep Size Greedy Solution: \n\tBenefit: {sol_dep_size_greedy_benefit} \n\tCapacity left: {sol_dep_size_greedy_cap_left}")
            print(f"Pack Benefit Greedy Solution: \n\tBenefit: {sol_pack_benefit_greedy_benefit} \n\tCapacity left: {sol_pack_benefit_greedy_cap_left}")
            print(f"Num Pack Greedy Solution: \n\tBenefit: {sol_num_pack_greedy_benefit} \n\tCapacity left: {sol_num_pack_greedy_cap_left}")
            print(f"Randomized Ratio Greedy Solution: \n\tBenefit: {sol_randomized_ratio_greedy_benefit} \n\tCapacity left: {sol_randomized_ratio_greedy_cap_left}")
            print(f"Randomized Dep Size Greedy Solution: \n\tBenefit: {sol_randomized_dep_size_greedy_benefit} \n\tCapacity left: {sol_randomized_dep_size_greedy_cap_left}")
            print(f"Randomized Pack Benefit Greedy Solution: \n\tBenefit: {sol_randomized_pack_benefit_greedy_benefit} \n\tCapacity left: {sol_randomized_pack_benefit_greedy_cap_left}")
            print(f"Randomized Num Pack Greedy Solution: \n\tBenefit: {sol_randomized_num_pack_greedy_benefit} \n\tCapacity left: {sol_randomized_num_pack_greedy_cap_left}")

            print(f"Test for full True: \n\tBenefit: {aux.evaluate_packs(pack_benefits, pack_dep, [True]*num_dep)} \n\tCapacity left: {aux.get_remaining_capacity(dep_sizes, [True]*num_dep, capacity)}")


            print("\n" + "="*50)
            print("TESTE DAS HEURÍSTICAS DE REFINAMENTO (1 PASSO)")
            print("="*50)

            # Solução inicial para teste (usando uma cópia da solução aleatória)
            test_sol = sol_randomic[:] 
            test_benefit = aux.evaluate_packs(pack_benefits, pack_dep, test_sol)
            print(f"Solução de Partida (Randomic): Benefício = {test_benefit}")

            # Definir a vizinhança para o teste
            # Usaremos 'flip_bit' e 'swap_bits' para garantir uma vizinhança mista
            test_neighborhood_names = ["flip_bit", "swap_bits"] 

            # Você pode usar todos os geradores com:
            # all_generators = list(move.generators_dict.keys())
            # print(f"\nVizinhanças de teste: {all_generators}")

            print(f"\nVizinhanças de teste: {test_neighborhood_names}")

            # --- Teste 1: Random Best Step (RS/FindAny) ---
            print("\n--- 1. Random Best Step (RS) ---")
            # Usando tempo e max_tries curtos para um teste rápido
            new_sol_rs = rh.random_best_step(
                test_sol, 
                pack_benefits, 
                pack_dep, 
                test_neighborhood_names, 
                time_limit=0.1, 
                max_tries=1000
            )
            new_benefit_rs = aux.evaluate_packs(pack_benefits, pack_dep, new_sol_rs[0])
            print(f"Movimento RS: {new_sol_rs[1:]}")
            print(f"Benefício após RS: {new_benefit_rs}. Melhora: {new_benefit_rs > test_benefit}")


            # --- Teste 2: First Best Step (FI/FindFirst) ---
            print("\n--- 2. First Best Step (FI) ---")
            new_sol_fi = rh.first_best_step(
                test_sol, 
                pack_benefits, 
                pack_dep, 
                test_neighborhood_names, 
                time_limit=0.1
            )
            new_benefit_fi = aux.evaluate_packs(pack_benefits, pack_dep, new_sol_fi[0])
            print(f"Movimento FI: {new_sol_fi[1:]}")
            print(f"Benefício após FI: {new_benefit_fi}. Melhora: {new_benefit_fi > test_benefit}")


            # --- Teste 3: Absolute Best Step (BI/FindBest) ---
            print("\n--- 3. Absolute Best Step (BI) ---")
            new_sol_bi = rh.absolute_best_step(
                test_sol, 
                pack_benefits, 
                pack_dep, 
                test_neighborhood_names, 
                time_limit=0.1
            )
            new_benefit_bi = aux.evaluate_packs(pack_benefits, pack_dep, new_sol_bi[0])
            print(f"Movimento BI: {new_sol_bi[1:]}")
            print(f"Benefício após BI: {new_benefit_bi}. Melhora: {new_benefit_bi > test_benefit}")

            # Fim do teste




    except FileNotFoundError:
        print(f"File {file_name} was not found.")
'''
