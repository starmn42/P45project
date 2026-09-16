from .calculator import calculate_unit
from .definitions import UNIT_10

def calculate(draws, analysis_round):
    return calculate_unit(UNIT_10, draws, analysis_round)
