# Python 3.10.0

from typing import List, Tuple, Any, Set
from pathlib import Path
import random
import math

def loadInstance(filepath:Path) -> List:
    "Each row is read into List[int], every sequential row with same len will be made into tuples inside a list. Each inner list is a type of data."
    
    def groupBlock(block:List[List[int]]) -> List[Any]: # List[int]|List[Tuple]:
        if len(block) == 1: # block with only one row
            return block[0]
        return [tuple(row) for row in block] # block with 2 or more rows
    
    with open(filepath, "r", encoding="utf-8") as file:
        output:List[List[Any]] = []
        currentBlock:List[List[int]] =[]
        currentWidth:int = 0
        for row in file:
            parts:list[int] = [int(x) for x in row.split()] 
            width:int = len(row)

            if currentWidth is None: # starting new block
                currentWidth = width
                currentBlock.append(parts)
                continue

            if width != currentWidth: # row with different width -> new block
                output.append(groupBlock(currentBlock)) # finalize last block
                currentBlock = [parts] # start new block as a List[List[int]]
                currentWidth = width
                continue

            currentBlock.append(parts) # appends a List[int] into our List[List[int]]
        
        if currentBlock: 
            output.append(groupBlock(currentBlock))

        output = [item for item in output if item] # remove empty blocks if any
        return output

def generateValidRandomSolution(numSchools:int, numStudents:int, going:bool) -> List[int]:
    students:List[int] = [num+numSchools for num in range(numStudents)]
    random.shuffle(students)
    schools:List[int] = [num for num in range(numSchools)]
    random.shuffle(schools)
    #print("students: ", students)
    #print("schools: ",schools)
    if going:
        students.extend(schools)
        return students
    schools.extend(students)
    return schools

def validateSolution(sol:List[int], numSchools:int, studentsSchool:List[int], going:bool) -> bool:
    #print("validanting sol: ", sol)
    schools:Set[int] = set(range(numSchools))
    students:Set[int] = set(range(numSchools, numSchools + len(studentsSchool)))
    if not schools.issubset(set(sol)):
        #print("not all schools visited")
        return False # not all schools visited
    if not students.issubset(set(sol)):
        #print("not all students visited")
        return False # not all students visited
    for point in sol:
        #print("point: ", point)
        if point >= numSchools: # if the point is a student house
            if studentsSchool[point-numSchools-1] not in sol[point:] and going: return False # if their school wasn't visited after getting the kid
            if studentsSchool[point-numSchools-1] not in sol[:point] and not going: return False # if their school wasn't visited before delivering the kid

    #print("sol is valid")
    return True

def measureDistance(coord1:tuple[int, int], coord2:tuple[int, int]) -> Tuple[float, int]:
    "Returns a pair of float values for euclidean and manhattan distance"

    euclidean:float = math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)
    manhattan:int = abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])
    
    return (euclidean, manhattan)

def measureSolution(sol:list[int], coords:List[Tuple[int, int]]) -> Tuple[float, int]:
    "Returns a pair of float values for euclidean and manhattan distance"

    euclidean:float = 0
    manhattan:int = 0
    for i in range(len(sol) - 2):
        point1:Tuple[int,int] = coords[sol[i]]
        point2:Tuple[int,int] = coords[sol[i+1]]
        eucl, manh = measureDistance(point1, point2)
        euclidean += eucl
        manhattan += manh

    return (euclidean, manhattan)

def lightClearSolution(sol:List[int]) -> List[int]:
    "Removes only successive repetitions."
    clearSol:List[int] = [sol[0]]
    for i in range(1, len(sol)):
        if sol[i] != clearSol[-1]:
            clearSol.append(sol[i])

    return clearSol

if __name__ == "__main__":
    print("Running auxiliaryFunc.py")
    instance = loadInstance(Path("old_input/blablabla"))
    print(instance)
    #numSchools, numStudents, maxRows, maxCols = instance[0]
    sol:List[int] = generateValidRandomSolution(2, 4, True)
    print(sol)
    validSol:bool = validateSolution(sol, instance[0][0], instance[2], going=True)
    print(validSol)


'''
Running auxiliaryFunc.py
[[2, 4, 3, 6], [(2, 4), (2, 1), (4, 1), (3, 2), (2, 3), (3, 3)], [1, 0, 1, 0]]
students:  [4, 2, 5, 3]
schools:  [0, 1]
[4, 2, 5, 3, 0, 1]
point:  4
point:  2
point:  5
False
'''