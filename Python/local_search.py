# Python 3.13.4

import random
import time
from typing import Callable, Union
from refinement_heuristic import heuristic_type, heuristics_dict
from move import move_type

TIME_LIMIT_DEFAULT:float = 30.0

''' Special type '''

# To be used when referencing functions from this file
local_search_type = Union[
    Callable[[list[bool], list[int], list[tuple[int, int]], list[heuristic_type], list[str], float, int], move_type]
]

''' Functions '''

# Differences between my Hill Climbing and my VND:
#       Hill Climbing takes refinement_heuristics list as a circular list and return when a solution fails to get better through all submited heuristics
#       VND resetes the number of failed heuristics and uses it as an index for refinement_heuristics list

# Searches for a local optimum by iteratively applying a submited list of refinement heuristic
# Keeps searching as long there's time. If heuristics list ends, it just starts over, still searching for a better
def hill_climbing(sol: list[bool], pack_benefits:list[int], pack_dep:list[tuple[int, int]], refinement_heuristics: list[heuristic_type] = [], neighborhood_names:list[str] = [], time_limit: float = TIME_LIMIT_DEFAULT, max_tries: int = 1000) -> move_type:
    current_move: move_type = (sol[:], "error", -1) # starts as error_output but may or may not change into something valuable
    failed_heuristics_for_current_move:int = 0 # increases if with a sol the function goes through one heuristic and there's no improvement
    start_time: float = time.time()

    while time.time() - start_time < time_limit:
        for heuristic in refinement_heuristics: # if refinement_heuristics == []: return current_move (aka, error_output)
            if time.time()-start_time >= time_limit: # end of time
                return current_move # return better solution found until now
            new_move:move_type = heuristic(current_move[0][:], pack_benefits, pack_dep, neighborhood_names, time_limit - (time.time() - start_time), max_tries)
            if new_move[1] is not "error": # new_move provides a better solution
                current_move = new_move
                failed_heuristics_for_current_move = 0
            else: # no better solution was obtained with this heuristic
                # if with current_move we go though all heuristics and couldn't get a better solution
                # it's impossible to get a better solution with curren_move, so return it
                if failed_heuristics_for_current_move == len(refinement_heuristics) -1 :
                    return current_move
                else:
                    failed_heuristics_for_current_move += 1

    return current_move

# While there's time and tries, chooses at reandom the heuristic used
# When the same solution is submited to all heuristics and can't get better -> returns
def random_descent_method(sol: list[bool], pack_benefits:list[int], pack_dep:list[tuple[int, int]], refinement_heuristics: list[heuristic_type] = [], neighborhood_names:list[str] = [], time_limit: float = TIME_LIMIT_DEFAULT, max_tries: int = 1000) -> move_type:
    current_move: move_type = (sol[:], "error", -1) # starts as error_output but may or may not change into something valuable
    failed_heuristics_current_move:set[heuristic_type] = set()
    submited_heuristics: set[heuristic_type] = set(refinement_heuristics)
    count:int = 0
    start_time: float = time.time()

    while count < max_tries and time.time() - start_time < time_limit:
        new_heuristic:heuristic_type = random.choice(refinement_heuristics)
        new_move:move_type = new_heuristic(current_move[0][:], pack_benefits, pack_dep, neighborhood_names, time_limit - (time.time() - start_time), max_tries)
        if new_move[1] is not "error": # new_move provides a better solution
            current_move = new_move
            failed_heuristics_current_move.clear() # not yet failed heuristics for current solution
        elif new_heuristic not in failed_heuristics_current_move: # first time current solution fails to get better with this new heuristic
            failed_heuristics_current_move.add(new_heuristic) 
            if set(failed_heuristics_current_move) == set(refinement_heuristics): # current solution failed to get better with all submited heuristics
                return current_move
        count += 1

    return current_move

# Searchs for a better solution through all refinement heuristics and resets to the first heuristics if a better solution is found
# Repeately restarting search each time a better solution is found -> as if hill_climbing as recursive
def variable_neighborhood_descent(sol: list[bool], pack_benefits:list[int], pack_dep:list[tuple[int, int]], refinement_heuristics: list[heuristic_type] = [], neighborhood_names:list[str] = [], time_limit: float = TIME_LIMIT_DEFAULT, max_tries: int = 1000) -> move_type:
    current_move: move_type = (sol[:], "error", -1) # starts as error_output but may or may not change into something valuable
    current_heuristic:int = 0
    len_heuristics_list:int = len(refinement_heuristics)
    start_time: float = time.time()

    while current_heuristic < len_heuristics_list and time.time() - start_time < time_limit:
        new_move:move_type = refinement_heuristics[current_heuristic](current_move[0][:], pack_benefits, pack_dep, neighborhood_names, time_limit - (time.time() - start_time), max_tries)
        if new_move[1] is not "error": # new_move provides a better solution
            current_move = new_move
            current_heuristic = 0 # new better move -> restart the search though heuristics
        else:
            current_heuristic += 1 # no better solution -> keep seraching with our current move

    return current_move

# A slightly different version of VND so that it shuffles refinement_heuristics list before exploring or during reset
def randomized_variable_neighborhood_descent(sol: list[bool], pack_benefits:list[int], pack_dep:list[tuple[int, int]], refinement_heuristics: list[heuristic_type] = [], neighborhood_names:list[str] = [], time_limit: float = TIME_LIMIT_DEFAULT, max_tries: int = 1000) -> move_type:
    current_move: move_type = (sol[:], "error", -1) # starts as error_output but may or may not change into something valuable
    current_heuristic:int = 0
    len_heuristics_list:int = len(refinement_heuristics)
    
    # I need to try to put this as a paremeter, somehow dealing with different inputs for local_search_type and fuse it with regular VND
    outter_shuffle:bool = False
    inner_shuffle:bool = True
    
    start_time: float = time.time()

    if outter_shuffle:
        random.shuffle(refinement_heuristics)

    while current_heuristic < len_heuristics_list and time.time() - start_time < time_limit:
        if inner_shuffle and current_heuristic == 0: # only shuffle if we're restarting the try outs, so we don't lose track of what we are doing
            random.shuffle(refinement_heuristics)
        new_move:move_type = refinement_heuristics[current_heuristic](current_move[0][:], pack_benefits, pack_dep, neighborhood_names, time_limit - (time.time() - start_time), max_tries)
        if new_move[1] is not "error": # new_move provides a better solution
            current_move = new_move
            current_heuristic = 0 # new better move -> restart the search though heuristics
        else:
            current_heuristic += 1 # no better solution -> keep seraching with our current move

    return current_move

''' Local Search Dictionary '''

# To be used as a list of the functions from this file
local_search_dict:dict[str, local_search_type] = {
    "hill_climbing": hill_climbing,
    "random_descent_method": random_descent_method,
    "variable_neighborhood_descent": variable_neighborhood_descent,
    "randomized_variable_neighborhood_descent": randomized_variable_neighborhood_descent
}
