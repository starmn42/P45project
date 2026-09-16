from .calculator import calculate_unit
from .definitions import END_DIGIT

def calculate(draws, analysis_round):
    return calculate_unit(END_DIGIT, draws, analysis_round)
