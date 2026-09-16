from pathlib import Path
import sqlite3
from p45_experiments.exp003.calculator import build_feature_state,evaluate_locked_feature,DISTANCES
from p45_experiments.exp003.storage import create_empty

def test_distance_zero_and_boundaries():
 f=build_feature_state([1,10,20,30,40,45],2)
 assert f['number_distance'][1]==0 and f['number_distance'][2]==1 and f['number_distance'][45]==0
 assert set(f['distance_exposure'])==set(DISTANCES) and sum(f['distance_exposure'].values())==45
def test_determinism_ten_times():assert len({build_feature_state([1,10,20,30,40,45],2)['feature_hash'] for _ in range(10)})==1
def test_outcome_is_separate():
 f=build_feature_state([1,10,20,30,40,45],2);o=evaluate_locked_feature(f,[2,11,21,31,41,44],3)
 assert o['feature_hash']==f['feature_hash'] and sum(o['main_hits'].values())==6 and sum(o['integrated_hits'].values())==7
def test_storage(tmp_path:Path):
 p=tmp_path/'e.sqlite3';create_empty(p);c=sqlite3.connect(p);assert c.execute('pragma integrity_check').fetchone()[0]=='ok' and c.execute('pragma foreign_key_check').fetchall()==[];c.close()
