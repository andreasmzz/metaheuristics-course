# Python 3.10.0

from typing import List, Tuple, Any, Dict, Union
from pathlib import Path
import random

'''

Instance format

sc st r c
coord(0)
coord(1) 
...
coord(sc+st-1)
ss(sc) ss(sc+1) ... ss(sc+st-1)

sc = numSchools
st = numStudents
r = maxRows
c = maxCols
coordX = coordinates for point X (X in [0, sc+st-1])
ss(X) = school in which student X is enrolled

Exemple:
2 4 3 6 -> 2 schools, 4 students, 3 rows, 6 columns
2 4     -> point 0 = school 0  coordinate
2 1     -> point 1 = school 1  coordinate
4 1     -> point 2 = student 0  coordinate
3 2     -> point 3 = student 1  coordinate
2 3     -> point 4 = student 2  coordinate
3 3     -> point 5 = student 3  coordinate
1 0 1 0 -> students 0 and 2 go to school 1, students 1 and 3 go to school 0

'''

OUTPUTDIR:Path = Path("input")
NUM_SCHOOLS:List[int] = [2,4,8]
NUM_STUDENTS:List[int] = [4,8,16,32]
NUM_ROWS:List[int] = [10]
NUM_COLS:List[int] = [10]
INSTANCES_PER_PARAMETERS:int = 5
PARAMETERS_VERSION:int = 1

def randomGenerateCoordinates(numSchools:int, numStudents:int, maxRows:int, maxCols:int) -> List[Tuple[int, int]]:
    "Returns a list of coordinates with numSchool first tuples being school places."
    
    coordinates:List[Tuple[int, int]] = []
    while len(coordinates) < (numSchools+numStudents):
        row,col = random.randint(0, maxRows-1), random.randint(0, maxCols-1)
        if (row, col) not in coordinates: coordinates.append((row, col))
    
    return coordinates

def pairStudentSchool(numSchools:int, numStudents:int, studentsPerSchool:list[int]) -> List[int]:
    "Receives number of students per school and returns a list of schools where student studies."
    
    if sum(studentsPerSchool) != numStudents:
        print(f"studentsPerSchool ({studentsPerSchool}) != numStudents ({numStudents})")
        return []
    if len(studentsPerSchool) != numSchools:
        print("len(studentsPerSchool) != numSchools")
        return []
    
    studentsSchool:List[int] = []
    for i, students in enumerate(studentsPerSchool):
        if students < 0: raise ValueError(f"Negative number of students for school {i}.")
        studentsSchool.extend([i]*students)
    random.shuffle(studentsSchool)

    return studentsSchool

def drawMap(numSchools:int, coordinates:List[Tuple[int, int]], maxRows:int, maxCols:int) -> None:
    "Draws on terminal # with numbers for schools, only numbers for students and dots for no relevant."
    
    currentSchool:int = 0
    currentStudent:int = 0
    numDigits:int = len(str(len(coordinates))) + 1 # could be int(math.log10(len(coordinates))) + 1 + 1
    cityMap:List[List[str]] = [["." for _ in range(maxCols)] for _ in range(maxRows)]
    for i in range(numSchools):
        row, col = coordinates[i]
        cityMap[row][col] = f"#{i}"
    for j in range(numSchools, len(coordinates)):
        row, col = coordinates[j]
        cityMap[row][col] =  f"{j-numSchools}"
    for row in cityMap:
        print(" ".join(str(cell).rjust(numDigits)for cell in row))

def generateSimpleInstance(numSchools:int, numStudents:int, maxRows:int, maxCols:int, filename:str) -> Tuple[List[Tuple[int, int]], List[int]]:
    "Returns: coordinates:List[Tuple[int, int]] with size numSchools + numStudents; studentsSchool:List[int] with size numStudents and int in [0, numSchools-1]"
    
    coordinates:List[Tuple[int, int]] = randomGenerateCoordinates(numSchools, numStudents, maxRows, maxCols)
    studentsPerSchool:List[int] = generateStudentsPerSchool(numSchools, numStudents)
    studentsSchool:List[int] = pairStudentSchool(numSchools, numStudents, studentsPerSchool)

    writeInstance(OUTPUTDIR, [[numSchools, numStudents, maxRows, maxCols], coordinates, studentsSchool], filename)
    
    return (coordinates,studentsSchool)

def generateStudentsPerSchool(numSchools:int, numStudents:int) -> List[int]:
    "Returns a list of studentsPerSchool with size numSchools."

    if numStudents < numSchools: raise ValueError(f"Too few students ({numStudents}) for schools ({numSchools}) as a school should have at least one student.")
    if numSchools <=0: return []
    if numSchools == 1: return [numStudents]
    if numSchools == numStudents: return [1] * numSchools

    bars:List[int] = sorted(random.sample(range(1, numStudents - numSchools), numSchools-1))
    bars = [0] + bars + [numStudents - numSchools]

    stars:List[int] = [bars[i+1] - bars[i]+1 for i in range(numSchools)]

    return stars

def writeInstance(folder:Path, rows:List[List[int]|List[Tuple[int, int]]], filename:str) -> None:
    "Writes every item from each inner list as a row except the first list, which is always instance parameters"
    
    #filename:str = "blablabla7"
    filepath:Path = folder/filename
    with open(filepath, "w", encoding="utf-8") as file:
        for row in rows:
            if not row:
                continue

            first = row[0] # to say if this row is a List[int] or a List[Tuple[int, int]]

            if isinstance(first, int):
                file.write(" ".join(str(i) for i in row)+ "\n")
            elif isinstance(first, tuple):
                for tup in row:
                    file.write(" ".join(str(x) for x in tup) + "\n") # type: ignore
            else:
                raise TypeError("Row contains unsupported or mixed types.")

def generateAllSimpleInstances() -> None:
    for numSchools in NUM_SCHOOLS:
        for numStudents in NUM_STUDENTS:
            for maxRows in NUM_ROWS:
                for maxCols in NUM_COLS:
                    for run in range(INSTANCES_PER_PARAMETERS):
                        intList:List[int] = [numSchools, numStudents, maxRows, maxCols, run]
                        filename:str = "school_transport_" + "_".join(map(str, intList)) + f"_v{PARAMETERS_VERSION}.txt"
                        if numStudents < numSchools: continue
                        (coords, studentsSchool) = generateSimpleInstance(numSchools, numStudents, maxRows, maxCols, filename)
                        drawMap(numSchools, coords, maxRows, maxCols)    


if __name__ == "__main__":
    print("Running createInstance.py")
    '''
    numSchools, numStudents, maxRows, maxCols = 8, 32, 10, 10
    studentsPerSchool:List[int] = [ 5, 3, 2, 2, 4, 6, 2, 8]
    filename:str = 'blablabla8'
    coords, studentsSchool = generateSimpleInstance(numSchools, numStudents, maxRows, maxCols, studentsPerSchool, filename)
    print("Coordinates: ", coords, "\nStudentsSchool: ", studentsSchool)
    drawMap(numSchools, coords, maxRows, maxCols)
    '''
    print(generateAllSimpleInstances())


'''
Traceback (most recent call last):
  File "/media/aluno/ANDY-UFF-24/25.2/Metaheuristics/SchoolTransport/createInstance.py", line 156, in <module>
    print(generateAllSimpleInstances())
          ~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/media/aluno/ANDY-UFF-24/25.2/Metaheuristics/SchoolTransport/createInstance.py", line 142, in generateAllSimpleInstances
    (coords, studentsSchool) = generateSimpleInstance(numSchools, numStudents, maxRows, maxCols, filename)
                               ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/media/aluno/ANDY-UFF-24/25.2/Metaheuristics/SchoolTransport/createInstance.py", line 93, in generateSimpleInstance
    studentsPerSchool:List[int] = generateStudentsPerSchool(numSchools, numStudents)
                                  ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/media/aluno/ANDY-UFF-24/25.2/Metaheuristics/SchoolTransport/createInstance.py", line 107, in generateStudentsPerSchool
    bars:List[int] = sorted(random.sample(range(1, numStudents - numSchools), numSchools-1))
                            ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.13/random.py", line 434, in sample
    raise ValueError("Sample larger than population or is negative")
ValueError: Sample larger than population or is negative
'''