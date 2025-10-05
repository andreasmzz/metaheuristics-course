# Python 3.13.4

import time
import move
from auxiliary_functions import evaluate_packs, get_remaining_capacity
from typing import Union, Callable

TIME_LIMIT_DEFAULT:float = 30.0

# Improvement functions are integrated with find functions 

''' Special type '''

# To be used when referencing functions from this file
heuristic_type = Union[
    Callable[[list[bool], list[int], list[int], list[tuple[int, int]], int, list[str], float, int], move.move_type], # random, first and best
]

''' Functions '''

# pack_benefits:    list[int] =             [pack_0_benefit, pack_1_benefit, ..., pack_0_benefit_(num_pack-1)]
# dep_sizes:        list[int] =             [dep_0_size, dep_1_size, ..., dep_0_size_(num_dep-1)]
# pack_dep:         list[tuple[int, int]] = [(pack_id, dep_id), ...]
# select_dep:       list[bool] =            [False, False, ..., False] (length = num_dep)
# free_space:       int =                   capacity - sum(dep_sizes[i] for i in range(len(select_dep)) if select_dep[i])



# Returns a randomic better solution with the move name and parameters that reached new_sol
def random_best_step(sol: list[bool], pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, neighborhood_names:list[str] = [], time_limit: float = TIME_LIMIT_DEFAULT, max_tries: int = 1000) -> move.move_type:
    error_output: move.move_type = (sol, "error", -1)
    current_move_evaluation: int = evaluate_packs(pack_benefits, pack_dep, sol)
    count:int = 0
    start_time = time.time()
    while count < max_tries and time.time()-start_time < time_limit:
        new_move:move.move_type = move.random_move(sol[:], neighborhood_names)

        if get_remaining_capacity(dep_sizes, new_move[0], capacity) < 0:
            count+=1
            continue # invalid solution, try next

        if evaluate_packs(pack_benefits, pack_dep, new_move[0]) > current_move_evaluation:
            return new_move
        else:
            count+=1
    return error_output # Couldn't find a better solution

# Default neighborhood_names is [] -> all moves
def first_best_step(sol: list[bool], pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, neighborhood_names:list[str] = [], time_limit: float = TIME_LIMIT_DEFAULT, max_tries: int = 1000) -> move.move_type:
    error_output: move.move_type = (sol, "error", -1)
    current_move_evaluation: int = evaluate_packs(pack_benefits, pack_dep, sol)
    start_time: float = time.time() 
    for move_name in neighborhood_names: # if neighborhood_names == []: return error_output
        if time.time()-start_time >= time_limit:
            return error_output # didn't have enough time to find a better solution
        move_generator: move.neighborhood_generator_type = move.generate_move(sol, move_name)
        for move_input_tuple in move_generator:
            if time.time()-start_time >= time_limit:
                return error_output # didn't have enough time to find a better solution
            new_move: move.move_type = move.move_by_name(sol[:], move_input_tuple)

            if get_remaining_capacity(dep_sizes, new_move[0], capacity) < 0:
                continue # invalid solution, try next

            if new_move[1] != "error": # plegal move
                if evaluate_packs(pack_benefits, pack_dep, new_move[0]) > current_move_evaluation:
                    return new_move

    return error_output # Couldn't find a better solution

# Returns local optimum found in the available time (may not represent the real local optimum)
def absolute_best_step(sol: list[bool], pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, neighborhood_names:list[str] = [], time_limit: float = TIME_LIMIT_DEFAULT, max_tries: int = 1000) -> move.move_type:
    error_output: move.move_type = (sol, "error", -1)
    current_move: move.move_type = error_output
    current_move_evaluation: int = evaluate_packs(pack_benefits, pack_dep, sol)
    start_time = time.time()
    for move_name in neighborhood_names: # if neighborhood_names == []: return error_output
        if time.time()-start_time >= time_limit:
            return current_move # return better solution found until now
        move_generator: move.neighborhood_generator_type = move.generate_move(sol, move_name)
        for move_input_tuple in move_generator:
            if time.time()-start_time >= time_limit:
                return current_move # return better solution find until now
            new_move: move.move_type = move.move_by_name(sol[:], move_input_tuple)

            if get_remaining_capacity(dep_sizes, new_move[0], capacity) < 0:
                continue # invalid solution, try next

            if new_move[1] != "error": # plegal move
                if evaluate_packs(pack_benefits, pack_dep, new_move[0]) > current_move_evaluation:
                    current_move = new_move
                    current_move_evaluation = evaluate_packs(pack_benefits, pack_dep, current_move[0])

    if current_move_evaluation > evaluate_packs(pack_benefits, pack_dep, sol):
        return current_move
    else:
        return error_output # Couldn't find a better solution

''' Heuristic dictionary '''

# 
heuristics_dict:dict[str, heuristic_type] = {
    "random_best_step": random_best_step, 
    "first_best_step": first_best_step, 
    "absolute_best_step": absolute_best_step
}
