# Python 3.13.4

import random
import auxiliary_functions as aux
from typing import Callable, Union


''' !!! Notice !!! '''
# New create[...] functions must be added to the first_solutions dictionary at the bottom of this file

''' Constructive solution '''

# Dispatch function to select and execute the desired method from first_solutions dictionary
def create_first_solution(method_name:str, pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, *args) -> list[bool]:
    if method_name not in first_solutions_dict:
        raise ValueError(f"Method '{method_name}' not recognized. Available methods: {list(first_solutions_dict.keys())}")
    return first_solutions_dict[method_name](pack_benefits, dep_sizes, pack_dep, capacity, *args)


# Randomic first solution: always returns a valid solution (doesn't exceed capacity)
def create_randomic_solution(pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, args) -> list[bool]:
    free_space: int = capacity
    selec_dep: list[bool] = [False]*len(dep_sizes)
    deps: list[tuple[int, int]] = list(enumerate(dep_sizes)) # (dep_id, dep_size)
    random.shuffle(deps)
    for dep in deps:
        if free_space - dep[1] >= 0:
            free_space -= dep[1]
            selec_dep[dep[0]] = True
    return selec_dep

# Greedy ratio first solution: by default biggest benefit/size ratio first | valid solution (doesn't exceed capacity)
def create_ratio_greedy_solution(pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, biggest_first:bool=True)-> list[bool]:
    free_space: int = capacity
    selec_dep: list[bool] = [False]*len(dep_sizes)

    deps: list[tuple[int, float, int]] = [] # (dep_id, total_dep_benefit, size)
    dep_dict: dict[int, set[int]] = aux.get_dep_dict(pack_dep) # dep_id -> set of packages that depend on it

    for dep_id in range(len(dep_sizes)):
        total_dep_benefit: int = sum(pack_benefits[pack] for pack in dep_dict.get(dep_id, []))
        deps.append((dep_id, total_dep_benefit, dep_sizes[dep_id]))
    deps.sort(key=lambda x: x[1]/x[2], reverse=biggest_first) # sort by benefit/size ratio
    
    for dep in deps:
        if free_space - dep[2] >= 0:
            free_space -= dep[2]
            selec_dep[dep[0]] = True
    return selec_dep

# Greedy dependency size first solution: by default smallest dep size first | valid solution (doesn't exceed capacity)
def create_dep_size_greedy_solution(pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, biggest_first:bool=False)-> list[bool]:
    free_space: int = capacity
    selec_dep: list[bool] = [False]*len(dep_sizes)

    deps: list[tuple[int, int]] = list(enumerate(dep_sizes)) # (dep_id, dep_size)
    deps.sort(key=lambda x: x[1], reverse=biggest_first) # sort by size

    for dep in deps:
        if free_space - dep[1] >= 0:
            free_space -= dep[1]
            selec_dep[dep[0]] = True
    return selec_dep

# Greedy pack benefit first solution: by default biggest pack benefit first | valid solution (doesn't exceed capacity)
def create_pack_benefit_greedy_solution(pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, biggest_first:bool=True)-> list[bool]:
    free_space: int = capacity
    selec_dep: list[bool] = [False]*len(dep_sizes)

    packs: list[tuple[int, int]] = list(enumerate(pack_benefits)) # (pack_id, pack_benefit)
    packs.sort(key=lambda x: x[1], reverse=biggest_first) # sort by benefit
    pack_dict: dict[int, set[int]] = aux.get_pack_dict(pack_dep) # pack_id -> set of dependencies it needs

    for pack in packs:
        needed_deps = pack_dict.get(pack[0], set())
        total_size_needed = sum(dep_sizes[dep] for dep in needed_deps if not selec_dep[dep])
        if free_space - total_size_needed >= 0:
            free_space -= total_size_needed
            for dep in needed_deps:
                selec_dep[dep] = True
        else:
            continue
    return selec_dep

# Greedy pack benefit first solution: by default biggest pack benefit first | valid solution (doesn't exceed capacity)
# Difference with not economic: this one takes into account already selected dependencies and doesn't count them for needed space
def create_economic_pack_benefit_greedy_solution(pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, biggest_first:bool=True)-> list[bool]:
    free_space: int = capacity
    selec_dep: list[bool] = [False]*len(dep_sizes)

    packs: list[tuple[int, int]] = list(enumerate(pack_benefits)) # (pack_id, pack_benefit)
    packs.sort(key=lambda x: x[1], reverse=biggest_first) # sort by benefit
    pack_dict: dict[int, set[int]] = aux.get_pack_dict(pack_dep) # pack_id -> set of dependencies it needs
    pack_index:int = 0
    tries_since_last_add:int = 0
    num_packs:int = len(packs)

    while free_space > 0 and tries_since_last_add < num_packs: # stop if we have tried to add all packs without success
        needed_deps = pack_dict.get(packs[pack_index][0], set()) # set() is the default value to be returned if pack[0] not in pack_dict
        copy = needed_deps.copy()
        for dep in copy:
            if selec_dep[dep]:
                needed_deps.remove(dep)
        total_size_needed = sum(dep_sizes[dep] for dep in needed_deps if not selec_dep[dep])
        if free_space - total_size_needed >= 0:
            free_space -= total_size_needed
            for dep in needed_deps:
                selec_dep[dep] = True
            tries_since_last_add = 0
        else: # not enough space to add this package
            tries_since_last_add += 1
        pack_index = (pack_index + 1) % num_packs # move to next pack
    return selec_dep

# Greedy number of dependent packages first solution: by default biggest number of packs first | valid solution (doesn't exceed capacity)
def create_num_pack_greedy_solution(pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, biggest_first:bool=True)-> list[bool]:
    free_space: int = capacity
    selec_dep: list[bool] = [False]*len(dep_sizes)

    deps_dict: dict[int, set[int]] = aux.get_dep_dict(pack_dep) # dep_id -> set of packages that depend on it
    deps: list[tuple[int, int]] = [(dep, len(deps_dict[dep])) for dep in deps_dict] # (dep_id, num_packs)

    deps.sort(key=lambda x: x[1], reverse=biggest_first) # sort by num_packs

    for dep in deps:
        if free_space - dep_sizes[dep[0]] >= 0:
            free_space -= dep_sizes[dep[0]]
            selec_dep[dep[0]] = True
    return selec_dep

# Randomized greedy ratio first solution: by default *** | valid solution (doesn't exceed capacity)
def create_randomized_ratio_greedy_solution(pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, biggest_first:bool=True, cutoff:float=0.5)-> list[bool]:
    free_space: int = capacity
    selec_dep: list[bool] = [False]*len(dep_sizes)

    deps: list[tuple[int, float, int]] = [] # (dep_id, total_dep_benefit, size)
    dep_dict: dict[int, set[int]] = aux.get_dep_dict(pack_dep) # dep_id -> set of packages that depend on it
    
    for dep_id in range(len(dep_sizes)):
        total_dep_benefit: int = sum(pack_benefits[pack] for pack in dep_dict.get(dep_id, []))
        deps.append((dep_id, total_dep_benefit, dep_sizes[dep_id]))
    deps.sort(key=lambda x: x[1]/x[2], reverse=biggest_first) # sort by benefit/size ratio

    # Introduce randomness by selecting from the top cutoff*100% of the sorted list
    cutoff = int(cutoff*len(deps))
    while deps:
        dep = random.choice(deps[:cutoff])
        if free_space - dep[2] >= 0:
            free_space -= dep[2]
            selec_dep[dep[0]] = True
        deps.remove(dep)

    return selec_dep

# Randomized greedy dependency size first solution: by default *** | valid solution (doesn't exceed capacity)
def create_randomized_dep_size_greedy_solution(pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, biggest_first:bool=False, cutoff:float=0.5)-> list[bool]:
    free_space: int = capacity
    selec_dep: list[bool] = [False]*len(dep_sizes)

    deps: list[tuple[int, int]] = list(enumerate(dep_sizes)) # (dep_id, dep_size)
    deps.sort(key=lambda x: x[1], reverse=biggest_first) # sort by size

    # Introduce randomness by selecting from the top cutoff*100% of the sorted list
    cutoff = int(cutoff*len(deps))
    while deps:
        dep = random.choice(deps[:cutoff])
        if free_space - dep[1] >= 0:
            free_space -= dep[1]
            selec_dep[dep[0]] = True
        deps.remove(dep)

    return selec_dep

# Randomized greedy pack benefit first solution: by default *** | valid solution (doesn't exceed capacity)
def create_randomized_pack_benefit_greedy_solution(pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, biggest_first:bool=True, cutoff:float=0.5)-> list[bool]:
    free_space: int = capacity
    selec_dep: list[bool] = [False]*len(dep_sizes)

    packs: list[tuple[int, int]] = list(enumerate(pack_benefits)) # (pack_id, pack_benefit)
    packs.sort(key=lambda x: x[1], reverse=biggest_first) # sort by benefit
    pack_dict: dict[int, set[int]] = aux.get_pack_dict(pack_dep) # pack_id -> set of dependencies it needs

    # Introduce randomness by selecting from the top cutoff*100% of the sorted list
    cutoff = int(cutoff*len(packs))
    while packs:
        pack = random.choice(packs[:cutoff])
        needed_deps = pack_dict.get(pack[0], set())
        total_size_needed = sum(dep_sizes[dep] for dep in needed_deps if not selec_dep[dep])
        if free_space - total_size_needed >= 0:
            free_space -= total_size_needed
            for dep in needed_deps:
                selec_dep[dep] = True
        packs.remove(pack)

    return selec_dep

# Randomized greedy number of dependent packages first solution: by default *** | valid solution (doesn't exceed capacity)
def create_randomized_num_pack_greedy_solution(pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, biggest_first:bool=True, cutoff:float=0.5)-> list[bool]:
    free_space: int = capacity
    selec_dep: list[bool] = [False]*len(dep_sizes)

    deps_dict: dict[int, set[int]] = aux.get_dep_dict(pack_dep) # dep_id -> set of packages that depend on it
    deps: list[tuple[int, int]] = [(dep, len(deps_dict[dep])) for dep in deps_dict] # (dep_id, num_packs)

    deps.sort(key=lambda x: x[1], reverse=biggest_first) # sort by num_packs

    # Introduce randomness by selecting from the top cutoff*100% of the sorted list
    cutoff = int(cutoff*len(deps))
    while deps:
        dep = random.choice(deps[:cutoff])
        if free_space - dep_sizes[dep[0]] >= 0:
            free_space -= dep_sizes[dep[0]]
            selec_dep[dep[0]] = True
        deps.remove(dep)

    return selec_dep

# 
def create_best_deterministic_first_solution(pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, biggest_first:bool=True) -> tuple[list[bool], int, str, str]:
    solutions:list[tuple[list[bool], int, str, str]] = [] # (solution, benefit, first solution method, biggest_first)    
    for method_name in deterministic_first_solutions_list:
        for biggest_first in [True, False]:
            first_sol:list[bool] = create_first_solution(method_name, pack_benefits, dep_sizes, pack_dep, capacity, biggest_first)
            benefit:int = aux.evaluate_packs(pack_benefits, pack_dep, first_sol)
            solutions.append((first_sol, benefit, method_name, str(biggest_first)))

    (first_sol, benefit, method_name, biggest) = max(solutions, key=lambda x: x[1])
    return (first_sol, benefit, method_name, biggest)

# Acceptable input and corresponding output types for first solution functions
first_solution_function_type = Union[
    Callable[[list[int], list[int], list[tuple[int, int]], int], list[bool]], # randomic    
    Callable[[list[int], list[int], list[tuple[int, int]], int, bool], list[bool]], # greedy
    Callable[[list[int], list[int], list[tuple[int, int]], int, bool, float], list[bool]] # randomized greedy
]

''' Dictionaries and lists '''

# Dictionary mapping heuristic names to their corresponding functions
first_solutions_dict: dict[str, first_solution_function_type] = {
    "create_randomic_solution": create_randomic_solution,
    "create_ratio_greedy_solution": create_ratio_greedy_solution,
    "create_dep_size_greedy_solution": create_dep_size_greedy_solution,
    "create_pack_benefit_greedy_solution": create_pack_benefit_greedy_solution,
    #"create_economic_pack_benefit_greedy_solution": create_economic_pack_benefit_greedy_solution,
    "create_num_pack_greedy_solution": create_num_pack_greedy_solution,
    "create_randomized_ratio_greedy_solution": create_randomized_ratio_greedy_solution,
    "create_randomized_dep_size_greedy_solution": create_randomized_dep_size_greedy_solution,
    "create_randomized_pack_benefit_greedy_solution": create_randomized_pack_benefit_greedy_solution,
    "create_randomized_num_pack_greedy_solution": create_randomized_num_pack_greedy_solution
}

# Deterministic solutions dictionary
deterministic_first_solutions_list: list[str] = [
    "create_ratio_greedy_solution",
    "create_dep_size_greedy_solution",
    "create_pack_benefit_greedy_solution",
    #"create_economic_pack_benefit_greedy_solution",
    "create_num_pack_greedy_solution"
]

# Random adn randomized first solution functions list
randomized_first_solutions_list:list = [
    "create_randomic_solution",
    "create_randomized_ratio_greedy_solution",
    "create_randomized_dep_size_greedy_solution",
    "create_randomized_pack_benefit_greedy_solution",
    "create_randomized_num_pack_greedy_solution"
]

# All create solution functions list
first_solutions_list:list = [
    "create_randomic_solution",
    "create_ratio_greedy_solution",
    "create_dep_size_greedy_solution",
    "create_pack_benefit_greedy_solution",
    #"create_economic_pack_benefit_greedy_solution",
    "create_num_pack_greedy_solution",
    "create_randomized_ratio_greedy_solution",
    "create_randomized_dep_size_greedy_solution",
    "create_randomized_pack_benefit_greedy_solution",
    "create_randomized_num_pack_greedy_solution"
]

