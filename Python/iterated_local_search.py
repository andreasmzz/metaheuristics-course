# Python 3.13.4

import random
import time

import move
import local_search as ls
from refinement_heuristic import heuristic_type
from local_search import local_search_dict, local_search_type
from auxiliary_functions import evaluate_packs

TIME_LIMIT_DEFAULT:float = 30.0
ILS_MAX_TRIES_DEFAULT:int = 1000
LS_MAX_TRIES_DEFAULT:int = 1000


# perturbation_moves is a list of moves to be used as perturbation, may be different from neighborhood moves
# if perturbation_moves == [] it uses a random move as perturbation (may disturb the solution too much)
def iterated_local_search(sol:list[bool], pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, perturbation_moves:list[str] = [], local_search_methods: list[local_search_type] = [], refinement_heuristics:list[heuristic_type] = [], neighborhood_names:list[str] = [], time_limit: float = TIME_LIMIT_DEFAULT, ils_max_tries: int = ILS_MAX_TRIES_DEFAULT, ls_max_tries:int = LS_MAX_TRIES_DEFAULT) -> move.move_type:
    start_time:float = time.time()
    best_try:int = 0
    tries:int = 0
    level:int = 0
    
    if local_search_methods == []:
        local_search_methods = list(local_search_dict.values())
    
    current_sol:move.move_type = (sol[:], "error", -1)
    chosen_ls:int = random.randint(0, max(0, len(local_search_methods)-1))
    current_sol = local_search_methods[chosen_ls](list(sol[:]), pack_benefits, dep_sizes, pack_dep, capacity, refinement_heuristics, neighborhood_names, time_limit - (time.time() - start_time), ls_max_tries)
    current_benefit:int = evaluate_packs(pack_benefits, pack_dep, current_sol[0])

    while time_limit > time.time() - start_time  and tries-best_try < ils_max_tries:
        tries += 1
        perturbed_sol:move.move_type = perturbation(list(current_sol[0]), perturbation_moves, level) # disturbs an already local optimum
        new_sol = random.choice(local_search_methods)(list(perturbed_sol[0]), pack_benefits, dep_sizes, pack_dep, capacity, refinement_heuristics, neighborhood_names, time_limit - (time.time() - start_time), ls_max_tries)
        new_benefit:int = evaluate_packs(pack_benefits, pack_dep, new_sol[0])
        if new_benefit > current_benefit:
            current_sol = new_sol
            current_benefit = new_benefit
            best_try = tries
            level = 0
        else: level += 1
    
    return current_sol

#
def perturbation(sol:list[bool], moves:list[str], level:int = 0) -> move.move_type:
    new_sol:move.move_type = (sol[:], "error", -1)
    num_perturb:int = level + 1
    for cont in range(num_perturb):
        new_sol = move.random_move(list(new_sol[0]), moves)  # extract solution list from tuple
    return new_sol

