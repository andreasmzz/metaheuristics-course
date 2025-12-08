# Python 3.10.0

from fileinput import filename
import os
import random
from typing import List, Tuple, Dict, Any
from pathlib import Path
import csv

import simulatedAnnealing as sa
import recordRecordTravel as rrt
import greatDeluge as gda
import auxiliaryFunc as aux


TIME_LIMIT_DEFAULT:float = 60.0
INNER_MAX_TRIES_DEFAULT:int = 1000
OUTER_MAX_TRIES_DEFAULT:int = 10000
MAX_NO_IMPROVEMENT_DEFAULT:int = 1000


''' Dicts '''
SA_ARGS:Dict[str, Any] = {
    'neighborhoods': [],
    'initialTemperature': sa.INITIAL_TEMPERATURE_DEFAULT,
    'alpha': sa.ALPHA_DEFAULT,
    'timeLimit': TIME_LIMIT_DEFAULT,
    'innerMaxTries': INNER_MAX_TRIES_DEFAULT,
    'outerMaxTries': OUTER_MAX_TRIES_DEFAULT,
    'maxNoImprovement': MAX_NO_IMPROVEMENT_DEFAULT
}
RRT_ARGS:Dict[str, Any] = {
    'neighborhoods': [],
    'alpha': rrt.ALPHA_DEFAULT,
    'timeLimit': TIME_LIMIT_DEFAULT,
    'innerMaxTries': INNER_MAX_TRIES_DEFAULT,
    'outerMaxTries': OUTER_MAX_TRIES_DEFAULT,
    'maxNoImprovement': MAX_NO_IMPROVEMENT_DEFAULT
}
GDA_ARGS:Dict[str, Any] = {
    'neighborhoods': [],
    'rainSpeedfactor': gda.RAIN_SPEED_FACTOR_DEFAULT,
    'timeLimit': TIME_LIMIT_DEFAULT,
    'innerMaxTries': INNER_MAX_TRIES_DEFAULT,
    'outerMaxTries': OUTER_MAX_TRIES_DEFAULT,
    'maxNoImprovement': MAX_NO_IMPROVEMENT_DEFAULT
}


''' Run Functions '''

def runExperiment(folderName:str, version:int, methodsNames:List[str], args:Dict[str, Any], runsPerFile:int = 5, going:bool=True, manhattan:bool=False) -> None:
    """
    Calls every method submitted runsPerFile times on every file in the submitted folder.
    """

    folder:Path = Path(folderName+f"_v{version}")

    try:
        files = os.listdir(folder)
    except FileNotFoundError:
        print(f"The folder '{folder}' does not exist.")
        return

    for fileName in files:
        filePath = Path(folder) / fileName
        
        bestSolFound:List[int] = []
        bestCostFound:Tuple[float, int] = (float('inf'), 10**10000)
        bestMethod:str = ""

        if os.path.isfile(filePath):
            setting, coords, studentsSchool = aux.loadInstance(filePath)
            initialSol = aux.generateValidRandomSolution(setting[0], setting[1], going=True)

            for run in range(runsPerFile):
                print(f"\nRunning experiments for file: {fileName}, Run: {run + 1}/{runsPerFile}")
                
                results:List[Dict[str, Dict[str, Any]]] = []

                for methodName in methodsNames:
                    if methodName == "Simulated Annealing" or methodName == "SA":
                        random.seed(run)  # Set seed for reproducibility
                        resSA:Tuple[List[int], Tuple[float, int], float, float, float, float] = runSimulatedAnnealing(Path(filePath), initialSol, setting, coords, studentsSchool, going, manhattan, args=args['SA'])
                        results.append({'SA': {'run': run, 'bestSol': resSA[0], 'bestCost': resSA[1], 'initialTemp': resSA[2], 'finalTemp': resSA[3], 'alpha': resSA[4], 'executionTime': resSA[5]}})
                        if resSA[1] < bestCostFound:
                            bestSolFound = resSA[0]
                            bestCostFound = resSA[1]
                            bestMethod = "SA"
                        
                    elif methodName == "Record-to-Record Travel" or methodName == "RRT":
                        random.seed(run)  # Set seed for reproducibility
                        resRRT:Tuple[List[int], Tuple[float, int], float, float, float] = runRecordRecordTravel(Path(filePath), initialSol, setting, coords, studentsSchool, going, manhattan, args=args['RRT'])
                        results.append({'RRT': {'run': run, 'bestSol': resRRT[0], 'bestCost': resRRT[1], 'alpha': resRRT[2], 'tolerance': resRRT[3], 'executionTime': resRRT[4]}})
                        if resRRT[1] < bestCostFound:
                            bestSolFound = resRRT[0]
                            bestCostFound = resRRT[1]
                            bestMethod = "RRT"

                    elif methodName == "Great Deluge" or methodName == "GDA":
                        random.seed(run)  # Set seed for reproducibility
                        resGDA:Tuple[List[int], Tuple[float, int], float, float, float] = runGreatDeluge(Path(filePath), initialSol, setting, coords, studentsSchool, going, manhattan, args=args['GDA'])
                        results.append({'GDA': {'run': run, 'bestSol': resGDA[0], 'bestCost': resGDA[1], 'rainSpeed': resGDA[2], 'waterFinalLevel': resGDA[3], 'executionTime': resGDA[4]}})
                        if resGDA[1] < bestCostFound:
                            bestSolFound = resGDA[0]
                            bestCostFound = resGDA[1]
                            bestMethod = "GDA"

                    else:
                        print(f"Method '{methodName}' is not recognized.")

                writeExperimentResults("output", filePath, results)
              
        writeBestPerInstance("output", filePath, version, bestSolFound, bestCostFound, bestMethod)

def runSimulatedAnnealing(filePath:Path, initialSol:List[int], setting:List[int], coords:List[Tuple[int, int]], studentsSchool:List[int], going:bool, manhattan:bool, args) -> Tuple[List[int], Tuple[float, int], float, float, float, float]:
    """
    Runs the Simulated Annealing algorithm on the given file.
    """

    # The **args unpacks the dictionary into keyword arguments (kwargs) 
    # and overrides any defaults defined in sa.simulatedAnnealing
    result = sa.simulatedAnnealing(
        sol=initialSol,
        setting=setting,
        coords=coords,
        studentsSchool=studentsSchool,
        going=going,
        manhattan=manhattan,
        
        **args
    )
    '''
        neighborhoodNames=args.neighborhoods,
        initialTemperature=args.initialTemperature,
        alpha=args.alpha,
        timeLimit=args.timeLimit,
        innerMaxTries=args.innerMaxTries,
        outerMaxTries=args.outerMaxTries
        '''
    
    bestSol, bestCosts, initialTemp, finalTemp, alpha, executionTime = result
    print(f"Simulated Annealing Result for {filePath.name}:")
    print(f"Best Costs: {bestCosts}, Initial Temp: {initialTemp}, Final Temp: {finalTemp}, Alpha: {alpha}, Execution Time: {executionTime}")

    return result

def runRecordRecordTravel(filePath:Path, initialSol:List[int], setting:List[int], coords:List[Tuple[int, int]], studentsSchool:List[int], going:bool, manhattan:bool, args) -> Tuple[List[int], Tuple[float, int], float, float, float]:
    """
    Runs the Record-to-Record Travel algorithm on the given file.
    """
    result = rrt.recordRecordTravel(
        sol=initialSol,
        setting=setting,
        coords=coords,
        studentsSchool=studentsSchool,
        going=going,
        manhattan=manhattan,
        
        **args
    )
    '''
        neighborhoodNames=args.neighborhoods,
        alpha=args.alpha,
        timeLimit=args.timeLimit,
        innerMaxTries=args.innerMaxTries,
        outerMaxTries=args.outerMaxTries'''

    bestSol, bestCosts, alpha, tolerance, executionTime = result
    print(f"Record-to-Record Travel Result for {filePath.name}:")
    print(f"Best Costs: {bestCosts}, Alpha: {alpha}, Tolerance: {tolerance}, Execution Time: {executionTime}")    

    return result

def runGreatDeluge(filePath:Path, initialSol:List[int], setting:List[int], coords:List[Tuple[int, int]], studentsSchool:List[int], going:bool, manhattan:bool, args) -> Tuple[List[int], Tuple[float, int], float, float, float]:
    """
    Runs the Great Deluge algorithm on the given file.
    """
    result = gda.greatDeluge(
        sol=initialSol,
        setting=setting,
        coords=coords,
        studentsSchool=studentsSchool,
        going=going,
        manhattan=manhattan,
        
        **args
    )
    '''
        neighborhoodNames=args.neighborhoods,
        rainSpeedFactor=args.rainSpeedFactor,
        timeLimit=args.timeLimit,
        innerMaxTries=args.innerMaxTries,
        outerMaxTries=args.outerMaxTries'''

    bestSol, bestCosts, rainSpeed, finalWaterLevel, executionTime = result
    print(f"Great Deluge Result for {filePath.name}:")
    print(f"Best Costs: {bestCosts}, Rain Speed: {rainSpeed}, Final Water Level: {finalWaterLevel}, Execution Time: {executionTime}")    

    return result

def writeExperimentResults(folderName:str, instance:Path, results:List[Dict[str, Dict[str, Any]]]) -> None:
    """
    Writes the experiment results to a file. Results is a list of dicts with key 'method', dict result with keys bestSol, bestCost and other args for each method.
    \nbestCost is a tuple (euclideanCost:float, manhattanCost:int).
    \nExample:
    \nresults = 
    \n\t[
    \n\t{'SA':{'bestSol': [...], 'bestCost': (123.45, 678), 'initialTemp': 1000.0, 'finalTemp': 10.0, 'alpha': 0.95}},
    \n\t{'RRT':{'bestSol': [...], 'bestCost': (234.56, 789), 'alpha': 0.98, 'tolerance': 50.0}},
    \n\t{'GDA':{'bestSol': [...], 'bestCost': (345.67, 890), 'rainSpeed': 0.5, 'finalWaterLevel': 100.0}}]
    """
    folder:Path = Path(folderName)
    # parents=True allows creating intermediate directories
    # exist_ok=True prevents an error if the directory already exists
    folder.mkdir(parents=True, exist_ok=True)

    csvFile:str = f"results_{instance.stem}.csv"
    filepath:Path = folder/csvFile

    fileExists:bool = filepath.exists()

    additionalHeaders = set()

    # Write header
    headers = ['Method', 'Run', 'BestSol', 'EuclideanCost', 'ManhattanCost', 'ExecutionTime']
    for result in results:
        for method, res in result.items():
            additionalHeaders.update(res.keys())
    additionalHeaders.discard('bestSol')
    additionalHeaders.discard('bestCost')
    additionalHeaders.discard('run')
    additionalHeaders.discard('executionTime')
    headers.extend(sorted(additionalHeaders))

    with open(filepath, 'a', newline='') as file:
        writer = csv.writer(file)

        if not fileExists:
            writer.writerow(headers)

        for result in results:
            for method, res in result.items():
                # Prepare a dictionary for easy field retrieval
                row_dict = {
                    'Method': method, 
                    'Run': str(res.get('run', '')), 
                    # Correct solution formatting
                    'BestSol': ' '.join(map(str, res['bestSol'])).strip('[]'), 
                    'EuclideanCost': str(res['bestCost'][0]), 
                    'ManhattanCost': str(res['bestCost'][1]),
                    'ExecutionTime': str(res.get('executionTime', ''))
                }
                for header in additionalHeaders:
                    row_dict[header] = str(res.get(header, ''))
                aligned_row = [row_dict.get(h, '') for h in headers]
                writer.writerow(aligned_row)

'''
# Append new results to existing .csv or create new file
def append_to_csv(experiment_type: str, new_results: list[dict[str, Any]], output_dir) -> None:
    csv_file: Path = output_dir / f"{experiment_type}.csv"
    fieldnames: list[str] = list(new_results[0].keys())
    
    file_exists: bool = csv_file.exists()
    
    with open(csv_file, "a", newline='') as f: # "a" is for append
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(new_results)
'''

def writeBestPerInstance(folderName:str, instance:Path, version:int, bestSol:List[int], bestCost:Tuple[float, int], bestMethod:str) -> None:
    """
    Writes the best solution found per instance to a file.
    """

    txtFile:str = f"bestSolutionVersion{version}.txt"
    folder:Path = Path(folderName)
    folder.mkdir(parents=True, exist_ok=True)
    filepath:Path = folder/txtFile

    row: str = f"Instance: {instance.name}, Best Method: {bestMethod}, Best Cost: {bestCost}, Best Sol: {' '.join(map(str, bestSol))}\n"
    with open(filepath, 'a') as file:
        file.write(row)









if __name__ == "__main__":
    print("Running experiment.py")
    runExperiment('input', 1, ['SA', 'RRT', 'GDA'], {'SA': {}, 'RRT': {}, 'GDA': {}}, runsPerFile=3, going=True, manhattan=False)
   