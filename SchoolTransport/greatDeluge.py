# Python 3.10.0

import time
from typing import List, Tuple

import auxiliaryFunc as aux
import move


RAIN_SPEED_FACTOR_DEFAULT:float = 1.0
TIME_LIMIT_DEFAULT:float = 60.0
INNER_MAX_TRIES_DEFAULT:int = 1000
OUTER_MAX_TRIES_DEFAULT:int = 10000
MAX_NO_IMPROVEMENT_DEFAULT:int = 1000

def greatDeluge(sol:list[int], setting:List[int], coords:List[Tuple[int, int]], studentsSchool:List[int], going:bool, manhattan:bool, neighborhoodNames:list[str] = [],
                        rainSpeedFactor:float = RAIN_SPEED_FACTOR_DEFAULT, timeLimit: float = TIME_LIMIT_DEFAULT, innerMaxTries: int = INNER_MAX_TRIES_DEFAULT, outerMaxTries:int = OUTER_MAX_TRIES_DEFAULT, maxNoImprovement:int = MAX_NO_IMPROVEMENT_DEFAULT) -> Tuple[List[int], Tuple[float, int], float, float, float]:
    "Returns finalSol:List[int], finalCosts:Tuple[int, int], alpha:float, tol:float -- setting is [numSchools, numStudents, maxRows, maxCols]."

    currentSol:list[int] = sol[:]
    currentCosts:Tuple[float, int] = aux.measureSolution(currentSol, coords) # euclidean and manhattan
    bestSol:List[int] = sol[:]
    bestCosts:Tuple[float, float] = currentCosts
    costIndex:int = 1 if manhattan else 0
    waterLevel:float = currentCosts[costIndex]
    rainSpeed:float = rainSpeedFactor * (currentCosts[costIndex] / outerMaxTries)
    tries:int = 0
    noImprovementCount:int = 0
    startTime:float = time.time()
    
    while time.time() - startTime < timeLimit and tries < outerMaxTries and noImprovementCount < maxNoImprovement:
        if time.time() - startTime >= timeLimit: print("Expired time - greatDeluge"); break
        newMove:move.moveType = move.getValidRandomMove(currentSol, setting[0]+setting[1]-1, neighborhoodNames, innerMaxTries)
        if newMove[1] == "error": continue # couldn't find a new solution
        if not aux.validateSolution(newMove[0], setting[0], studentsSchool, going=going): continue # invalid solution
        newCosts:Tuple[float, float] = aux.measureSolution(newMove[0], coords)
        cost:float = newCosts[costIndex]
        # delta > 0 -> new solution is worse
        if cost <= waterLevel:
            currentSol = newMove[0]
            currentCosts = newCosts
            if currentCosts[costIndex] < bestCosts[costIndex]:
                bestSol = currentSol
                bestCosts = currentCosts
                noImprovementCount = 0
        tries += 1
        noImprovementCount += 1
        waterLevel -= rainSpeed

    executionTime = time.time() - startTime
    bestSol = aux.lightClearSolution(bestSol)
    return (bestSol, bestCosts, rainSpeed, waterLevel, executionTime)