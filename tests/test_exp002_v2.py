from p45_experiments.exp002_v2.locked_run import baseline
from p45_experiments.exp002.fallback import source_pool

def test_pair_baselines(): assert 0<baseline('MAIN')<baseline('INTEGRATED')<1
def test_hold_is_ranked_without_trio_engine():
 rows={n:{'number':n,'number_state':'NUMBER_HOLD','unit_state_vector':['UNIT_TEST']*5,'number_opposite_risk':'LOW','number_structure_state':'NORMAL','primary_number_context':None,'relation_state':'UNIT_NO_SUPPORT','pareto_state':'UNIT_PARETO_NONDOMINATED','overlap_profile':(0,0,0),'number_context_conflict':'NONE'} for n in range(1,8)}
 assert [x['number'] for x in source_pool(rows)][:6]==[1,2,3,4,5,6]
