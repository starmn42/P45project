from pathlib import Path
import json
from .pairs.final_aggregation import aggregate

ROOT=Path(__file__).resolve().parents[2]
def main():
    result=aggregate(ROOT/'v27_storage/backtests/p45_v274_pair_walkforward_v12.sqlite3',
      ROOT/'v27_storage/backtests/p45_v274_pair_v12_final_aggregation.sqlite3',
      ROOT/'v27_storage/reports/p45_v274_pair_v12_final_aggregation.json',
      ROOT/'downloads/official-1-1235/official.csv',ROOT/'v27_storage/backtests/p45_v273_trio_walkforward.sqlite3')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
