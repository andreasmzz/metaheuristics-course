# Python 3.13.4

import random
from typing import Callable, Union, Literal, Tuple, Generator

''' Special types '''

# The solution and the move that got it -> [sol, neighborhood_type] ???
move_type = Union[
    Tuple[list[bool], Literal["flip_bit", "error"], int],
    Tuple[list[bool], Literal["swap_bits", "reverse_segment"], int, int],
    Tuple[list[bool], Literal["shift_segment", "move_segment"], int, int, int]
]

# Used on moves_dict _ the solution and the moves arguments
move_function_type = Union[
    Callable[[list[bool], int], move_type], # flip_bit
    Callable[[list[bool], int, int], move_type], # swap_bits, reverse_segment
    Callable[[list[bool], int, int, int], move_type] # shift_segment, move_segment
]

# Move names and their arguments
neighborhood_type = Union[
    Tuple[Literal["flip_bit", "error"], int], # flip_bit
    Tuple[Literal["swap_bits", "reverse_segment"], int, int], # swap_bits, reverse_segment
    Tuple[Literal["shift_segment", "move_segment"], int, int, int] # shift_segment, move_segment
]

# Is this actually a variable ???
neighborhood_generator_type = Generator[neighborhood_type, None, None]

''' Functions '''

# Flip a bit at a specific index: sol[index] = not sol[index]
def flip_bit(sol: list[bool], index: int) -> move_type:
    sol[index] = not sol[index]
    return (sol, "flip_bit", index)

# Swap bits at two specific indices: sol[index1], sol[index2] = sol[index2], sol[index1]
def swap_bits(sol: list[bool], index1: int, index2: int) -> move_type:
    sol[index1], sol[index2] = sol[index2], sol[index1]
    return (sol, "swap_bits", index1, index2)

# Reverse a segment of bits: sol[start:end+1] = reversed(sol[start:end+1])
def reverse_segment(sol: list[bool], start: int, end: int) -> move_type:
    sol[start:end+1] = reversed(sol[start:end+1])
    return (sol, "reverse_segment", start, end)

# Shift a segment of bits: sol[start:end+1] = sol[start:end+1][positions:] + sol[start:end+1][:positions]
def shift_segment(sol: list[bool], start: int, end: int, positions: int) -> move_type:
    segment = sol[start:end+1]
    del sol[start:end+1]
    new_start = (start + positions) % (len(sol) + len(segment))
    for i, val in enumerate(segment):
        sol.insert(new_start + i, val)
    return (sol, "shift_segment", start, end, positions)

# Move a segment of bits to a new position: sol[new_position:new_position] = sol[start:end+1]; del sol[start:end+1]
def move_segment(sol: list[bool], start: int, end: int, new_position: int) -> move_type:
    segment = sol[start:end+1]
    del sol[start:end+1]
    for i, val in enumerate(segment):
        sol.insert(new_position + i, val)
    return (sol, "move_segment", start, end, new_position)

# 
def move_by_name(sol:list[bool], move:neighborhood_type) -> move_type:
    error_output: move_type = (sol, "error", -1)
    match move:
        case name, arg1:
            if name == "flip_bit":
                return flip_bit(sol, arg1)
            return error_output
        case name, arg1, arg2:        
            if name == "swap_bits":
                return swap_bits(sol, arg1, arg2)
            elif name == "reverse_segment":
                return reverse_segment(sol, arg1, arg2)
            return error_output
        case name, arg1, arg2, arg3:
            if name == "shift_segment":
                return shift_segment(sol, arg1, arg2, arg3)
            elif name == "move_segment":
                return move_segment(sol, arg1, arg2, arg3)
            return error_output
        case _:
            return error_output

# Randomly choose and apply one of the move functions with random parameters
def random_move(sol: list[bool], neighborhood_names:list[str] = []) -> move_type:
    error_output: move_type = (sol, "error", -1)

    if neighborhood_names: # if some neighborhood was submited to random_move
        move_names = [name for name in neighborhood_names if name in moves_dict]
    else: # neighborhood is all moves
        move_names = list(moves_dict.keys())

    if not move_names: # submited neighborhood contains only illegal moves
        return error_output
    
    match random.choice(move_names):
        case "flip_bit":
            index = random.randint(0, len(sol) - 1)
            return flip_bit(sol, index)
        
        case "swap_bits":
            index1, index2 = random.sample(range(len(sol)), 2)
            return swap_bits(sol, index1, index2)
        
        case "reverse_segment":
            start = random.randint(0, len(sol) - 2)
            end = random.randint(start + 1, len(sol) - 1)
            return reverse_segment(sol, start, end)
        
        case "shift_segment":
            start = random.randint(0, len(sol) - 2)
            end = random.randint(start + 1, len(sol) - 1)
            positions = random.randint(1, len(sol) - (end - start + 1))
            return shift_segment(sol, start, end, positions)
        
        case "move_segment":
            start = random.randint(0, len(sol) - 2)
            end = random.randint(start + 1, len(sol) - 1)
            new_position = random.randint(0, len(sol) - (end - start + 1))
            return move_segment(sol, start, end, new_position)
        case _:
            return error_output

''' Generators '''
# Generate all possible moves by type

# Returns a generator that runs through all bits to flip them one by one
def generate_flip_bit(sol: list[bool]) -> neighborhood_generator_type: # O(n)
    for index in range(len(sol)):
        yield ("flip_bit", index)

# 
def generate_swap_bits(sol:list[bool]) -> neighborhood_generator_type: # O(n^2)
    len_sol:int = len(sol)
    if len_sol < 2: return
    for index1 in range(len_sol):
        for index2 in range(index1+1, len_sol):
            yield ("swap_bits", index1, index2)

# 
def generate_reverse_segment(sol:list[bool]) -> neighborhood_generator_type: # O(n^2)
    len_sol:int = len(sol)
    if len_sol < 2: return
    for start in range(len_sol-1):
        for end in range(start+1, len_sol):
            yield ("reverse_segment", start, end)

# 
def generate_shift_segment(sol:list[bool]) -> neighborhood_generator_type: # O(n^3)
    len_sol:int = len(sol)
    if len_sol < 2: return
    for start in range(len_sol-1):
        for end in range(start+1, len_sol):
            segment_size = end - start + 1
            shift_max_size = len_sol - segment_size
            if shift_max_size > 0:
                for position in range(1, shift_max_size+1):
                    yield ("shift_segment", start, end, position)

# 
def generate_move_segment(sol:list[bool]) -> neighborhood_generator_type: # O(n^3)
    len_sol:int = len(sol)
    if len_sol < 2: return
    for start in range (len_sol - 1):
        for end in range (start+1, len_sol-1):
            segment_size:int = end + start + 1
            max_new_position:int = len_sol - segment_size
            if max_new_position >= 0:
                for new_position in range(max_new_position + 1):
                    yield ("move_segment", start, end, new_position)

# Receives a sol and a move name and returns the generator or an error
def generate_move(sol:list[bool], move_name: str) -> neighborhood_generator_type:
    
    def empty_generator_func() -> neighborhood_generator_type:
        if False:
            yield
    
    empty_generator: neighborhood_generator_type = empty_generator_func()
    
    if not move_name in moves_dict: # submited move_name is an illegal move
        return empty_generator

    match move_name:
        case "flip_bit":
            return generate_flip_bit(sol)
        case "swap_bits":
            return generate_swap_bits(sol)
        case "reverse_segment":
            return generate_reverse_segment(sol)
        case "shift_segment":
            return generate_shift_segment(sol)
        case "move_segment":
            return generate_move_segment(sol)
        case _:
            return empty_generator


''' Dictionaries for functions and generators '''

#
moves_dict: dict[str, move_function_type] = {
    "flip_bit": flip_bit,
    "swap_bits": swap_bits,
    "reverse_segment": reverse_segment,
    "shift_segment": shift_segment,
    "move_segment": move_segment
}

# 
generators_dict:dict[str, Callable[[list[bool]], neighborhood_generator_type]] = {
    "flip_bit": generate_flip_bit,
    "swap_bits": generate_swap_bits,
    "reverse_segment": generate_reverse_segment,
    "shift_segment": generate_shift_segment,
    "move_segment": generate_move_segment
}

