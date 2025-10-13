# Python 3.13.4

import random
import time
from typing import Callable
from move import move_type, get_valid_random_move
from auxiliary_functions import evaluate_packs, get_remaining_capacity, get_pack_dict, ga_debug_report, ga_debug_close
from first_solution import create_randomic_solution

GENERATIONS_DEFAULT: int = 20
GENES_PER_GENERATION_DEFAULT:int = 200
ELITISM_DEFAULT:int = 1
MUTATION_DEFAULT:float = 0.01 # 1%
MUTATIONS_PER_GENE_DEFAULT:int = 1
PARENTS_DEFAULT:int = 100 # OFFSPRING_DEFAULT = GENES_PER_GENERATION_DEFAULT - PARENTS_DEFAULT
LINEAR_RANK_SELECTION_PRESSURE:float = 1.5
TOURNAMENT_SIZE_DEFAULT:int = 10
TIME_LIMIT_DEFAULT:float = 90.0
CROSSOVER_MIN_GAP: int = 5

#
def genetic_algorithm (sol:list[bool], pack_benefits: list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, neighborhood_names:list[str] = [], generations:int=GENERATIONS_DEFAULT, genes_per_generation:int = GENES_PER_GENERATION_DEFAULT, parents_per_generation:int = PARENTS_DEFAULT, parent_selection_id:int = 2, parents_survive:bool = True, elite_number:int = ELITISM_DEFAULT, two_offsprings:bool = True, crossover_points:list[int] = [], mutation:float = MUTATION_DEFAULT, mutations_per_gene:int = MUTATIONS_PER_GENE_DEFAULT, time_limit:float = TIME_LIMIT_DEFAULT, verbose:bool = False) -> tuple:
    start_time: float = time.time()

    if len(sol) == 0: sol = create_randomic_solution(pack_benefits, dep_sizes, pack_dep, capacity) # no solution was submited
    population: list[list[bool]] = generate_first_generation(sol[:], neighborhood_names, genes_per_generation)
    population_fitness:list[int] = evaluate_population(population, pack_benefits, pack_dep)
    # state used by ga_debug_report to persist CSV writer/file across calls
    debug_state: dict | None = None

    for gen in range(generations):
        if time.time() - start_time >= time_limit: print("Expired time - starting generation"); break
        print(f"Running generation {gen}")

        # Delegate verbose debug printing and CSV logging to auxiliary function
        # Log diagnostics to a single CSV file but avoid printing samples to stdout
        debug_state = ga_debug_report(gen, population, population_fitness, pack_benefits, pack_dep, dep_sizes, capacity, verbose=verbose, debug_state=debug_state, print_to_stdout=False)

        # Compute elite and selected parents up front
        elite:list[list[bool]] = elitism(population, population_fitness, elite_number)
        elite_set = set(map(tuple, elite))
        selected_parents = select_parents(population, population_fitness, parents_per_generation, list(parents_selection_dict.keys())[parent_selection_id])

        # Keep surviving parents if requested; avoid duplicating elites (fast membership)
        survivors: list[list[bool]] = [p[:] for p in selected_parents if tuple(p) not in elite_set] if parents_survive else []

        # Build a set of existing individuals (elites + survivors) so we can reject duplicates O(1)
        existing_keys:set[tuple] = set(map(tuple, elite)) | set(map(tuple, survivors))

        # Determine how many offsprings we still need to fill the generation
        needed_offsprings = genes_per_generation - (len(survivors) + len(elite))
        if needed_offsprings < 0:
            needed_offsprings = 0

        # Breed offspring while ensuring uniqueness by checking existing_keys (no nested loops)
        offsprings: list[list[bool]] = []
        attempts = 0
        max_attempts = max(1000, needed_offsprings * 10 + 100)
        while len(offsprings) < needed_offsprings and attempts < max_attempts:
            if time.time() - start_time >= time_limit: print("Expired time - breeding"); break
            attempts += 1

            parent1:list[bool] = random.choice(selected_parents)
            parent2:list[bool] = random.choice(selected_parents)
            if parent1 == parent2: continue # avoid crossover with itself

            new_offsprings = [kid for kid in crossover(parent1, parent2, crossover_points, two_offsprings) if get_remaining_capacity(dep_sizes, kid, capacity) >= 0]
            if len(new_offsprings) == 0: continue # crossover failed

            for kid in new_offsprings:
                if time.time() - start_time >= time_limit: print("Expired time - breeding"); break
                k = tuple(kid)
                if k in existing_keys:
                    continue
                offsprings.append(kid)
                existing_keys.add(k)
                if len(offsprings) >= needed_offsprings:
                    break

        # If for some reason we couldn't generate enough unique offsprings, we will fill the rest
        # with generated valid random moves (keeping uniqueness) as a minimal, deterministic fallback.
        fill_attempts = 0
        while len(offsprings) < needed_offsprings and fill_attempts < 1000:
            if time.time() - start_time >= time_limit: print("Expired time - breeding"); break
            fill_attempts += 1
            new_move = get_valid_random_move(sol[:], neighborhood_names)
            if new_move[1] == "error":
                continue
            kid = new_move[0][:]
            k = tuple(kid)
            if get_remaining_capacity(dep_sizes, kid, capacity) < 0:
                continue
            if k in existing_keys:
                continue
            offsprings.append(kid)
            existing_keys.add(k)

        # Build new population and mutate
        new_population: list[list[bool]] = survivors + offsprings + elite
        random.shuffle(new_population)
        new_population = mutate_population(new_population, mutation, mutations_per_gene)
        population = new_population
        population_fitness = evaluate_population(population, pack_benefits, pack_dep)

    # return best individual found (consistent return shape even on failure)
    parent_selection_name = list(parents_selection_dict.keys())[parent_selection_id]
    if len(population) == 0:
        # ensure debug CSV is flushed/closed
        ga_debug_close(debug_state)
        # return a safe, consistent tuple so the caller can handle it without crashing
        return ([], 0, sol[:], neighborhood_names, generations, elite_number,
                parents_per_generation, parents_survive, parent_selection_name, two_offsprings, crossover_points,
                mutation, mutations_per_gene, time_limit)

    best_index:int = max(range(len(population_fitness)), key=lambda i: population_fitness[i])
    # ensure debug CSV is flushed/closed
    ga_debug_close(debug_state)
    return (population[best_index][:], population_fitness[best_index], sol[:], neighborhood_names, generations, elite_number,
            parents_per_generation, parents_survive, parent_selection_name, two_offsprings, crossover_points,
            mutation, mutations_per_gene, time_limit)

# Returns a list of valid solutions
def generate_first_generation(sol:list[bool] = [], neighborhood_names:list[str] = [], genes_per_generation:int = GENES_PER_GENERATION_DEFAULT) -> list[list[bool]]:
    population: list[list[bool]] = []
    num_genes:int = 0
    expected_len: int | None = len(sol) if sol else None
    existing_keys:set[tuple] = set()
    attempts = 0
    max_attempts = genes_per_generation * 50 + 100
    while num_genes < genes_per_generation and attempts < max_attempts:
        attempts += 1
        new_move: move_type = get_valid_random_move(sol[:], neighborhood_names)
        # get_valid_random_move returns a tuple (solution, status). If status == "error", try again.
        if new_move[1] == "error":
            continue
        # Ensure consistent gene length across population
        if expected_len is None:
            expected_len = len(new_move[0])
        if len(new_move[0]) != expected_len:
            # skip inconsistent individuals
            continue
        k = tuple(new_move[0])
        if k in existing_keys:
            continue
        population.append(new_move[0][:])
        existing_keys.add(k)
        num_genes += 1

    return population

# Sorted list of population's evaluations
def evaluate_population(population:list[list[bool]], pack_benefits:list[int], pack_dep:list[tuple[int, int]]) -> list[int]:
    genes_per_population:int = len(population)
    # evaluate each individual and return a list of evaluations
    evaluations: list[int] = []
    for i in range(genes_per_population):
        evaluations.append(evaluate_packs(pack_benefits, pack_dep, population[i][:]))
    return evaluations

#
def select_parents(population:list[list[bool]], population_fitness:list, num_parents:int, selection_method:str, linear_rank:bool = False, selection_pressure:float = LINEAR_RANK_SELECTION_PRESSURE, linear_rank2:bool = False, tournament_size:int = TOURNAMENT_SIZE_DEFAULT) -> list[list[bool]]:
    if linear_rank:
        population_fitness = linear_rank_selection(population, population_fitness, selection_pressure, linear_rank2)
    
    match selection_method:
        case "roulette": # returns n
            return roulette_wheel_selection(population, population_fitness, num_parents)
        case "stochastic": # returns n 
            return stochastic_universal_sampling(population, population_fitness, num_parents)
        case "tournament": # returns 1 -> run n times
            selected:list[list[bool]] = []
            for i in range(num_parents):
                selected.append(tournament_selection(population, population_fitness, tournament_size))
            return selected
        case _:
            raise ValueError(f"Unknown selection method: {selection_method}")

# Returns n list[bool] -  can have duplicates
# Doesn't sort the fitness list
# Bad if a member has a really large fitness compared to other members
def roulette_wheel_selection(population:list[list[bool]], population_fitness:list[int], number_parents:int) -> list[list[bool]]:
    genes_per_population:int = len(population)
    if genes_per_population == 0: return []
    total_fitness:float = sum(population_fitness)
    if total_fitness == 0:
        # fallback: choose uniformly at random with replacement
        return [random.choice(population)[:] for _ in range(number_parents)]

    selected:list[list[bool]] = []
    rand:list[float] = [random.uniform(0, total_fitness) for _ in range(number_parents)]
    cumulative_sum:float = 0
    for i in range(genes_per_population):
        cumulative_sum += population_fitness[i]
        for j in range(number_parents):
            if cumulative_sum >= rand[j]:
                selected.append(population[i][:])
                break
    
    return selected

# Returns n list[bool] - no duplicates
# Selects multiple parents at once - doesn't pair them - doesn't sort the fitness list
# No bias and minimal spread 
def stochastic_universal_sampling(population:list[list[bool]], population_fitness:list[int], number_parents:int) -> list[list[bool]]:
    genes_per_population:int = len(population)
    if genes_per_population == 0: return []
    total_fitness:int = sum(population_fitness)
    if total_fitness == 0:
        # fallback: choose uniformly at random with replacement
        return [random.choice(population)[:] for _ in range(number_parents)]
    
    # Use float step and uniform start like standard SUS
    point_distance:float = total_fitness/number_parents
    start:float = random.uniform(0, point_distance)
    points:list[float] = [start + i*point_distance for i in range(number_parents)] # already sorted

    selected:list[list[bool]] = []
    for point in points:
        i:int = 0
        fitness_sum:float = population_fitness[i]
        while fitness_sum < point:
            i += 1
            fitness_sum += population_fitness[i]
        selected.append(population[i][:])
    return selected

# Returns 1 list[float] of probabilities of each individual being selected -> be used on other selection functions
# Uses roulette or random choice based on prob_selection or prob_selection2
# selection_pressure: 1 (uniform - no selection pressure) to 2 (strong bias to best individuals - high selection pressure)
def linear_rank_selection(population:list[list[bool]], population_fitness:list[int], selection_pressure:float, use_prob_selection2:bool) -> list[float]:
    # Compute rank-based selection probabilities without reordering the population.
    genes_per_population:int = len(population)
    if genes_per_population == 0: return []
    if not (1 <= selection_pressure <= 2): return [] # invalid selection pressure

    # rank 1..N assigned from worst->best (1 = worst)
    sorted_indices = sorted(range(genes_per_population), key=lambda i: population_fitness[i])
    ranks = [0]*genes_per_population
    for rank_pos, idx in enumerate(sorted_indices, start=1):
        ranks[idx] = rank_pos

    if not use_prob_selection2:
        # linear ranking formula mapped to ranks (rank 1..N)
        prob_selection = [ (1/genes_per_population) * (selection_pressure - (2*selection_pressure - 2)*((r-1)/(genes_per_population - 1))) for r in ranks ]
    else:
        prob_selection = [ (2*(genes_per_population - r + 1))/(genes_per_population*(genes_per_population + 1)) for r in ranks ]

    return prob_selection

# Returns n list[bool] who are the best individuals in the population
# sort the fitness list - no duplicates
# To be used as a part of the new generation
def elitism(population:list[list[bool]], population_fitness:list[int], number_to_keep:int) -> list[list[bool]]:
    # Keep the top 'number_to_keep' individuals (highest fitness)
    paired = sorted(zip(population_fitness, population), key=lambda x: x[0], reverse=True)
    genes_per_population:int = len(paired)
    if genes_per_population == 0 or number_to_keep <= 0: return []
    if number_to_keep > genes_per_population: number_to_keep = genes_per_population

    kept = [p for _, p in paired[:number_to_keep]]
    return [k[:] for k in kept]

# Returns 1 list[bool] of the best found
# Doesn't sort the fitness list
def tournament_selection(population:list[list[bool]], population_fitness:list[int], tournament_size:int) -> list[bool]:
    genes_per_population:int = len(population)
    if genes_per_population == 0: return []
    total_fitness:int = sum(population_fitness)
    if total_fitness == 0: return [] # all individuals have fitness 0, cannot select parents
    if tournament_size <= 0: return [] # invalid tournament size
    if tournament_size > genes_per_population: tournament_size = genes_per_population

    selected_indices:list[int] = random.sample(range(0, genes_per_population), tournament_size)
    best_index:int = selected_indices[0]
    for i in selected_indices[1:]:
        if population_fitness[i] > population_fitness[best_index]:
            best_index = i
    return population[best_index][:]

# Crosses and switches reference parent at every break point
# No break points -> random break point
def crossover(parent1:list[bool], parent2:list[bool], break_points:list[int], two_offsprings:bool) -> list[list[bool]]:
    len_sol:int = len(parent1)
    if len_sol != len(parent2) or len_sol < 2: return []
    # avoid mutating caller list
    points = sorted(set(break_points)) if break_points else []
    # if no explicit break points provided, choose one respecting a min gap from ends
    if not points:
        # only enforce a minimum gap when feasible
        if len_sol > 2 * CROSSOVER_MIN_GAP:
            points = [random.randint(CROSSOVER_MIN_GAP, len_sol - CROSSOVER_MIN_GAP)]
        else:
            points = [random.randint(1, len_sol - 1)]
    # validate points are within (0, len_sol)
    # and respect min gap from edges
    points = [p for p in points if 0 < p < len_sol and p >= CROSSOVER_MIN_GAP and p <= (len_sol - CROSSOVER_MIN_GAP)]
    if not points:
        # fallback to single mid-point
        mid = len_sol // 2
        if mid <= 0 or mid >= len_sol:
            return []
        points = [mid]
    # ensure the final point covers to the end (use len_sol as exclusive end)
    if len_sol not in points:
        points.append(len_sol)

    offsprings:list[list[bool]] = []
    offspring1 = [False]*len_sol
    offspring2 = [False]*len_sol
    previous_point = 0
    offspring1_parent = 1
    for point in points:
        if offspring1_parent == 1:
            offspring1[previous_point:point] = parent1[previous_point:point]
            offspring2[previous_point:point] = parent2[previous_point:point]
            previous_point = point
            offspring1_parent = 2
        else:
            offspring1[previous_point:point] = parent2[previous_point:point]
            offspring2[previous_point:point] = parent1[previous_point:point]
            previous_point = point
            offspring1_parent = 1
    
    offsprings.append(offspring1)
    if two_offsprings: offsprings.append(offspring2)
    return offsprings

# Chooses randomly mutation*len(population) elements and changes mutation_per_gene points in each chosen element
# Mutations can be undone if the same bit of the same element is changed an even number of times
def mutate_population(population:list[list[bool]], mutation:float, mutation_per_gene:int) -> list[list[bool]]:
    genes_per_population:int = len(population)
    if genes_per_population == 0: return population
    # handle variable-length individuals safely: select indices per-individual
    # compute how many individuals to mutate
    num_to_mutate = int(genes_per_population * mutation)
    if num_to_mutate <= 0: return population

    mutated_indices:list[int] = random.sample(range(0, genes_per_population), num_to_mutate)
    for i in mutated_indices:
        gene_size = len(population[i])
        if gene_size == 0:
            continue
        for _ in range(mutation_per_gene):
            idx = random.randint(0, gene_size - 1)
            # guard against any accidental index errors
            if 0 <= idx < len(population[i]):
                population[i][idx] = not population[i][idx]
    return population

''' Dictionaries '''

parents_selection_dict: dict[str, Callable] = {
    "roulette": roulette_wheel_selection,
    "stochastic": stochastic_universal_sampling,
    "tournament": tournament_selection
}

