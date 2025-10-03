# Python 3.13.4

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

''' Basic function parameters ''' # Mind exceptions
# pack_benefits:list[int], pack_dep:list[tuple[int, int]], select_dep:list[bool]

''' Dependencies'''

# main.py
#   first_solution.py
#       auxiliary_functions.py
#   refinement_heiristics.py
#       auxiliary_functions.py
#       move
#   local_search


''' File descriptions: '''

'''docs.py:'''
#       This file, general documentation of the project

'''main.py:'''
#       Main file, defines the input files, the tecniques to be used, the metrics to be analyzed
#       Calls functions from basically all other files

'''auxiliary_functions.py:'''
#       Diverse purpose auxiliary functions used across all the project

        # def evaluate_packs(pack_benefits:list[int], pack_dep:list[tuple[int, int]], select_dep:list[bool]) -> int
        # def get_remaining_capacity(dep_sizes:list[int], selec_dep:list[bool], capacity:int) -> int
        # def get_pack_dict(pack_dep:list[tuple[int, int]]) -> dict[int, set[int]]
        # def get_dep_dict(pack_dep:list[tuple[int, int]]) -> dict[int, set[int]]
        # def register_results(results: list[list[bool]], pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, terminal:bool=True, external_file:bool=False, file_name:str="results.txt", file_mode:str="a") -> None

'''move.py:'''
#       Five different "move" functions that modify a given list[bool] solution and a random_move function
#       move_by_name and random_move that can call either of the five move functions
#       Five generator of neighborhoods, one for each move, and a generic generator by a move name
#       Dictionaries for moves and generators
#       Special types for move, move functions, neighborhood and neighborhood generator

'''first_solution.py:'''
#       All "create_[...]_solution" functions to start with various greedy and randomic solutions

'''refinement_heuristic.py:'''
#       Three different refinement heuristics to improve a given solution with one step
#       Special type for heuristic

'''local_search.py:'''
#       Smart Hill Climbing, Random Descent Method, Variable Neighborhood Descent and Randomized Variable Neighborhood Descent
#

'''experiment.py'''
#       
#