# Python 3.10.0

import random
import time
from math import e
from typing import List, Tuple

import move
import auxiliaryFunc as aux

INITIAL_TEMPERATURE_DEFAULT:int = 1000
TIME_LIMIT_DEFAULT:float = 60.0
INNER_MAX_TRIES_DEFAULT:int = 1000
OUTER_MAX_TRIES_DEFAULT:int = 10000
ALPHA_DEFAULT:float = 0.95 # how slow temperature decreases in SA
BETA_DEFAULT:float = 1.125 # how temperature increases in find inital temperature
GAMMA_DEFAULT:float = 0.9 # acceptance rate in find initial temperature
MAX_NO_IMPROVEMENT_DEFAULT:int = 1000

def simulatedAnnealing(sol:list[int], setting:List[int], coords:List[Tuple[int, int]], studentsSchool:List[int], going:bool, manhattan:bool, neighborhoodNames:list[str] = [],
                        initialTemperature:float = INITIAL_TEMPERATURE_DEFAULT, alpha:float = ALPHA_DEFAULT, timeLimit: float = TIME_LIMIT_DEFAULT, innerMaxTries: int = INNER_MAX_TRIES_DEFAULT, outerMaxTries:int = OUTER_MAX_TRIES_DEFAULT, maxNoImprovement:int = MAX_NO_IMPROVEMENT_DEFAULT) -> Tuple[List[int], Tuple[float, int], float, float, float, float]:
    "Returns bestSol:List[int], bestCosts:Tuple[int, int], initialTemperature:float, finalTemperature:float, alpha:float -- setting is [numSchools, numStudents, maxRows, maxCols]."

    currentSol:list[int] = sol[:]
    currentCosts:Tuple[float, int] = aux.measureSolution(currentSol, coords) # euclidean and manhattan
    bestSol:list[int] = sol[:]
    bestCosts:Tuple[float, float] = currentCosts
    costIndex:int = 1 if manhattan else 0
    tries:int = 0
    noImprovementCount:int = 0
    temperature:float = initialTemperature
    startTime:float = time.time()

    while temperature > 1/initialTemperature and time.time() - startTime < timeLimit and tries < outerMaxTries and noImprovementCount < maxNoImprovement:
        if time.time() - startTime >= timeLimit: print("Expired time - simulatedAnnealing"); break
        newMove:move.moveType = move.getValidRandomMove(currentSol, setting[0]+setting[1]-1, neighborhoodNames, innerMaxTries)
        if newMove[1] == "error": continue # couldn't find a new solution
        if not aux.validateSolution(newMove[0], setting[0], studentsSchool, going=going): continue # invalid solution
        newCosts:Tuple[float, float] = aux.measureSolution(newMove[0], coords)
        delta:float = newCosts[costIndex] - currentCosts[costIndex]
        # delta > 0 -> new solution is worse
        if delta < 0 or random.random() < min(1, e**(-delta / temperature)):
            currentSol = newMove[0]
            currentCosts = newCosts
            if currentCosts[costIndex] < bestCosts[costIndex]:
                bestSol = currentSol
                bestCosts = currentCosts
                noImprovementCount = 0
        tries += 1
        noImprovementCount += 1
        temperature *= alpha

    executionTime = time.time() - startTime
    bestSol = aux.lightClearSolution(bestSol)
    return (bestSol, bestCosts, initialTemperature, temperature, alpha, executionTime)

def findInitialTemperature(sol:list[int], setting:List[int], coords:List[Tuple[int, int]], studentsSchool:List[int], going:bool, manhattan: bool,
                            neighborhoodNames:list[str] = [], initialTemperature:float = INITIAL_TEMPERATURE_DEFAULT, beta:float = BETA_DEFAULT, gamma:float = GAMMA_DEFAULT, timeLimit: float = TIME_LIMIT_DEFAULT, innerMaxTries: int = INNER_MAX_TRIES_DEFAULT, outerMaxTries:int = OUTER_MAX_TRIES_DEFAULT) -> tuple[float, float, float, float]:
    "Returns finalTemperature[float], initalTemperature[float], beta[float], gamma[float] -- setting is [numSchools, numStudents, maxRows, maxCols]."
    
    currentTemp:float = initialTemperature
    currentSol:list[int] = sol[:]
    currentCosts:Tuple[float, float] = aux.measureSolution(currentSol, coords)
    costIndex:int = 1 if manhattan else 0
    startTime:float = time.time()

    while time.time() - startTime < timeLimit:
        print(f"Trying T = {currentTemp}")
        accepted:int = 0 # moves accepted with current T
        for tries in range (outerMaxTries):
            if time.time() - startTime >= timeLimit: print("Expired time - findInitialTemperature"); break
            newMove:move.moveType = move.getValidRandomMove(currentSol, setting[0]+setting[1]-1, neighborhoodNames)
            if newMove[1] == "error": print("new move is error"); continue # couldn't find a new solution
            if not aux.validateSolution(newMove[0], setting[0], studentsSchool, going=going): continue # invalid solution
            newCosts:Tuple[float, float] = aux.measureSolution(newMove[0], coords)
            delta:float = newCosts[costIndex] - currentCosts[costIndex]
            # delta > 0 -> new solution is worse
            #print(f"try number: {tries}, current costs:{currentCosts}, new tested costs: {newCosts}, delta: {delta}")
            if delta < 0 or random.random() < min(1, e**(-delta / currentTemp)): 
                accepted += 1
                currentSol = newMove[0]
                currentCosts = newCosts
            if delta == 0: currentSol = aux.lightClearSolution(currentSol)
        if accepted >= gamma * outerMaxTries: 
            print(f"Found T = {currentTemp} with acceptance rate {accepted / outerMaxTries}")
            break
        else: currentTemp *= beta
        
    return (currentTemp, initialTemperature, beta, gamma)



