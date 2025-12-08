# Python 3.10.0

import random
from typing import Tuple, List, Literal, Union, Callable


"Move names and their arguments"
neighborhoodType = Union[
    Tuple[Literal["removePointIndex", "removePointValue", "error"], int],
    Tuple[Literal["insertPoint", "swapPoints", "reverseSegment"], int, int],
    Tuple[Literal["shiftSegment", "moveSegment"], int, int, int] 
]

"The solution and the move that got it -> [sol, neighborhoodType]"
moveType = Union[
    Tuple[List[int], Literal["removePointIndex", "removePointValue", "error"], int], # see if this really works
    Tuple[List[int], Literal["insertPoint", "swapPoints", "reverseSegment"], int, int],
    Tuple[List[int], Literal["shiftSegment", "moveSegment"], int, int, int]
]

"Used on moves_dict _ the solution and the moves arguments"
moveFunctionType = Union[
    Callable[[list[int], int], moveType], # removePointIndex, removePointValue, error
    Callable[[list[int], int, int], moveType], # insertPoint, swapPoints, reverseSegment
    Callable[[list[int], int, int, int], moveType] # shiftSegment, moveSegment
]


def insertPoint(sol:List[int], index:int, point:int) -> moveType:
    "Inserts a point at one specific index: sol = sol[start:index-1] + point + sol[start:index+1]"

    newSol:List[int] = sol[:]
    newSol.insert(index, point)
    
    return (newSol, "insertPoint", index, point)

def removePointIndex(sol:List[int], index:int) -> moveType:
    "Removes a point at one specific index: sol = sol[start:index-1] + sol[start:index+1]"

    newSol:List[int] = sol[:]
    newSol.pop(index)
    
    return (newSol, "removePointIndex", index)

def removePointValue(sol:List[int], value:int) -> moveType:
    "Removes the first occurrence of the value: sol = sol[start:valueIndex] + sol[start:valueIndex+1]"

    newSol:List[int] = sol[:]
    if value in newSol:
        newSol.remove(value)
    
    return (newSol, "removePointValue", value)

def swapPoints(sol:List[int], index1:int, index2:int) -> moveType:
    "Swaps points at two specific indices: sol[index1], sol[index2] = sol[index2], sol[index1]"

    newSol:List[int] = sol[:]
    newSol[index1], newSol[index2] = newSol[index2], newSol[index1]
    
    return (newSol, "swapPoints", index1, index2)

def reverseSegment(sol:List[int], start:int, end:int) -> moveType:
    "Reverses a segment of points: sol[start:end+1] = reversed(sol[start:end+1])"

    newSol:List[int] = sol[:]    
    newSol[start:end+1] = reversed(sol[start:end+1])
    
    return (newSol, "reverseSegment", start, end)

def shiftSegment(sol:List[int], start:int, end:int, positions:int) -> moveType:
    "Shifts a segment of points: sol[start:end+1] = sol[start:end+1][positions:] + sol[start:end+1][:positions]"
    
    segment = sol[start:end+1]
    newSol:List[int] = sol[:]
    positions = positions % len(segment) # in case positions > len(segment)
    if positions == 0: return (sol, "shiftSegment", start, end, positions) # no change
    newSol[start:end+1] = segment[positions:] + segment[:positions]
    
    return (newSol, "shiftSegment", start, end, positions)

def moveSegment(sol:List[int], start:int, end:int, newPosition:int) -> moveType:
    "Moves a segment of points to a new position: sol[newPosition:newPosition] = sol[start:end+1]; del sol[start:end+1]"
    
    segment = sol[start:end+1]
    newSol:List[int] = sol[:]
    del newSol[start:end+1]
    for i, val in enumerate(segment):
        newSol.insert(newPosition + i, val)
    
    return (newSol, "moveSegment", start, end, newPosition)

def moveByName(sol:List[int], move:neighborhoodType) -> moveType:
    " "

    errorOutput: moveType = (sol, "error", -1)
    match move:
        case name, arg1:
            if name == "removePointIndex":
                return removePointIndex(sol, arg1)
            elif name == "removePointValue":
                return removePointValue(sol, arg1)
            return errorOutput
        case name, arg1, arg2:
            if name == "insertPoint":
                return insertPoint(sol, arg1, arg2)
            if name == "swapPoints":
                return swapPoints(sol, arg1, arg2)
            elif name == "reverseSegment":
                return reverseSegment(sol, arg1, arg2)
            return errorOutput
        case name, arg1, arg2, arg3:
            if name == "shiftSegment":
                return shiftSegment(sol, arg1, arg2, arg3)
            elif name == "moveSegment":
                return moveSegment(sol, arg1, arg2, arg3)
            return errorOutput
        case _:
            return errorOutput

def randomMove(sol:List[int], maxValue:int, neighborhoodNames:List[str] = []) -> moveType:
    "Randomly choose and apply one of the move functions with random parameters"
    
    errorOutput: moveType = (sol, "error", -1)

    if neighborhoodNames: # if some neighborhood was submited to randomMove
        moveNames = [name for name in neighborhoodNames if name in movesDict]   # TODO create movesDict
    else: # neighborhood is all moves
        moveNames = list(movesDict.keys())

    if not moveNames: # submited neighborhood contains only illegal moves
        return errorOutput
    
    if len(sol) == 0:
        moveNames = ["insertPoint"]  # only insertPoint can be applied to an empty solution
    elif len(sol) == 1:
        moveNames.remove("swapPoints")
        moveNames.remove("reverseSegment")
        moveNames.remove("shiftSegment")
        moveNames.remove("moveSegment")

    match random.choice(moveNames):
        case "removePointIndex": # needs at least one point
            index = random.randint(0, len(sol) - 1)
            return removePointIndex(sol, index)
        
        case "removePointValue": # needs at least one point
            value = random.randint(min(sol), max(sol))
            return removePointValue(sol, value)

        case "insertPoint": # can be applied to any solution
            length = max(0, len(sol))
            index, point = random.randint(0, length), random.randint(0, maxValue)
            return insertPoint(sol, index, point)

        case "swapPoints": # needs at least two points
            index1, index2 = random.sample(range(len(sol)), 2)
            return swapPoints(sol, index1, index2)
        
        case "reverseSegment": # needs at least two points
            start = random.randint(0, len(sol) - 2)
            end = random.randint(start + 1, len(sol) - 1)
            return reverseSegment(sol, start, end)
         
        case "shiftSegment": # needs at least two points
            start = random.randint(0, len(sol) - 2)
            end = random.randint(start + 1, len(sol) - 1)
            positions = random.randint(1, end - start + 1)
            return shiftSegment(sol, start, end, positions)
        
        case "moveSegment": # needs at least two points
            start = random.randint(0, len(sol) - 2)
            end = random.randint(start + 1, len(sol) - 1)
            newPosition = random.randint(0, len(sol) - (end - start + 1))
            return moveSegment(sol, start, end, newPosition)
        case _:
            return errorOutput

def getValidRandomMove(sol:List[int], maxValue:int, neighborhoodNames:List[str] = [], maxTries:int = 100) -> moveType:
    "Tries until maxTries or newMove name != 'error'"
    
    for _ in range(maxTries):
        newMove:moveType = randomMove(sol[:], maxValue, neighborhoodNames)
        if newMove[1] != "error":
            return newMove
    return (sol, "error", -1)









''' Dictionaries for functions and generators '''

#
movesDict: dict[str, moveFunctionType] = {
    "removePointIndex": removePointIndex,
    "removePointValue": removePointValue,
    "insertPoint": insertPoint,
    "swapPoints": swapPoints,
    "reverseSegment": reverseSegment,
    "shiftSegment": shiftSegment,
    "moveSegment": moveSegment
}

'''
# 
generatorsDict:dict[str, Callable[[List[int]], neighborhoodGeneratorType]] = {
    "removePointIndex": generateRemovePointIndex,
    "removePointValue": generateRemovePointValue,
    "insertPoint", generateInsertPoint,
    "swappoints": generateSwapPoints,
    "reverseSegment": generateReverseSegment,
    "shiftSegment": generateShiftSegment,
    "moveSegment": generateMoveSegment
}
'''



