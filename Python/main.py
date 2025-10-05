# Python 3.13.4

import time

import first_solution as fs
import auxiliary_functions as aux
import refinement_heuristic as rh
import move as move
from first_solution import first_solutions_dict
import run_experiment
import analyze_results


file_name = "input/prob-software-85-100-812-12180.txt"

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

    ''' Experiments '''

    print("-"*75)
    print("RUNNING ALL CURRENT EXPERIMENTS")
    print("-"*75)

    start_time:float = time.time()

    run_experiment.run_local_search_experiment()

    elapsed_total:float = time.time() - start_time

    print("-"*75)
    print(f"ALL EXPERIMENTS COMPLETED IN {elapsed_total:.2f} SECONDS")
    print("-"*75)

    ''' Analysis '''

    print("\n" + "-"*75)
    print("ANALYZING RESULTS")
    print("-"*75 + "\n")
    
    analyze_results.analyze_constructive()
    analyze_results.analyze_local_search()
    
    print("-"*75)
    print("ANALYSIS COMPLETE")
    print("-"*75)

if __name__ == "__main__":
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
