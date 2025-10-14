# Python 3.13.4

import random
import time
from auxiliary_functions import evaluate_packs, get_remaining_capacity
from move import move_type, get_valid_random_move, random_move
from math import e

INITIAL_TEMPERATURE_DEFAULT:int = 1000
TIME_LIMIT_DEFAULT:float = 90.0
MAX_TRIES_DEFAULT:int = 10000
ALPHA_DEFAULT:float = 0.95 # how slow temperature decreases in SA
BETA_DEFAULT:float = 1.125 # how temperature increases in find inital temperature
GAMMA_DEFAULT:float = 0.9 # acceptance rate in find initial temperature

#
def simulated_annealing(sol:list[bool], pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, neighborhood_names:list[str] = [], initial_temperature:float = INITIAL_TEMPERATURE_DEFAULT, alpha:float = ALPHA_DEFAULT, time_limit: float = TIME_LIMIT_DEFAULT, max_tries: int = MAX_TRIES_DEFAULT) -> tuple[list[bool], int, float, float, float]:
    current_sol:list[bool] = sol[:]
    current_benefit:int = evaluate_packs(pack_benefits, pack_dep, current_sol)
    tries:int = 0
    temperature:float = initial_temperature
    start_time:float = time.time()

    while temperature > 0/initial_temperature and time.time() - start_time < time_limit and tries < max_tries:
        if time.time() - start_time >= time_limit: print("Expired time"); break
        new_move:move_type = get_valid_random_move(current_sol, neighborhood_names, max_tries)
        if new_move[1] == "error": continue # couldn't find a new solution
        if get_remaining_capacity(dep_sizes, new_move[0], capacity) < 0: continue # invalid solution
        new_benefit:int = evaluate_packs(pack_benefits, pack_dep, new_move[0])
        delta:int = new_benefit - current_benefit
        if delta > 0 or random.random() < min(1, e**(delta / temperature)):
            current_sol = new_move[0]
            current_benefit = new_benefit
        tries += 1
        temperature *= alpha

    return (current_sol, current_benefit, initial_temperature, temperature, alpha)

# 
def find_initial_temperature(sol:list[bool], pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, neighborhood_names:list[str] = [], initial_temperature:float = INITIAL_TEMPERATURE_DEFAULT, beta:float =BETA_DEFAULT, gamma:float = GAMMA_DEFAULT, time_limit: float = TIME_LIMIT_DEFAULT, max_tries: int = MAX_TRIES_DEFAULT) -> tuple[float, float, float, float]:
    current_temp:float = initial_temperature
    current_sol:list[bool] = sol[:]
    current_benefit:int = evaluate_packs(pack_benefits, pack_dep, current_sol)
    start_time:float = time.time()
    while time.time() - start_time < time_limit:
        print(f"Trying T = {current_temp}")
        accepted:int = 0 # moves accepted with current T
        for tries in range (max_tries):
            if time.time() - start_time >= time_limit: print("Expired time"); break
            new_move:move_type = get_valid_random_move(current_sol, neighborhood_names)
            if new_move[1] == "error": continue # couldn't find a new solution
            if get_remaining_capacity(dep_sizes, new_move[0], capacity) < 0: continue # invalid solution
            new_benefit:int = evaluate_packs(pack_benefits, pack_dep, new_move[0])
            delta:int = new_benefit - current_benefit
            if delta > 0 or random.random() < min(1, e**(delta / current_temp)): 
                accepted += 1
                current_sol = new_move[0]
                current_benefit = new_benefit
        if accepted >= gamma * max_tries: 
            print(f"Found T = {current_temp} with acceptance rate {accepted / max_tries}")
            break
        else: current_temp *= beta
    return (current_temp, initial_temperature, beta, gamma)



