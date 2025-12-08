# Python 3.10.0

from typing import List, Tuple
import random

"Data format: List"
"List[int]          numSchools numStudents maxRows maxCols"
"List[Tuple[int]]   coordinates"
"List[int]          studentsSchool"

def generateRandomSolution(totalPoints:int) -> List[int]:
    "Returns the order in which the points should be visited"

    route:List[int] = [num for num in range(totalPoints)]
    random.shuffle(route)
    return route
    

if __name__ == "__main__":
    print("Running main.py")
    route = generateRandomSolution(6)
    print(route)