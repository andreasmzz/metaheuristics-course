# Python 3.13.4

from dataclasses import dataclass, field
import datetime
import time
from typing import Callable, Tuple

solution_data: list[bool]

@dataclass
class ExperimentResult:
    experiment_id: str
    input_name: str
    run_timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    initial_solution: list[bool]
    refined_solution: list[bool]
    initial_solution_function: str
    refinement_heuristic_techniques: list[str] = field(default_factory=list)
    
    
    
    
    
    
    
    method_name: str
    move_name: str
    initial_value: int
    refined_value: int
    improvement: int
    num_evaluations: int
    time_taken: float





