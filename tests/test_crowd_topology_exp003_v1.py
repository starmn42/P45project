from p45_experiments import crowd_topology_exp003_v1 as m

def test_intersection_coefficients_and_rank():
    a=m.algebra_preflight()
    assert a['rank']==7
    assert all(a['coefficient_checks'].values())

def test_snapshot_range_and_fields():
    data=m.load()
    assert data['round'].tolist()==list(range(1,1238))
    assert len(data['k5'])==1237

def test_locked_boundary_and_versions():
    assert m.REPS==200_000
    assert m.SEED==2026082306
    assert m.VAL.astype(int).tolist()==[1,234,11115,182780,1233765,3454542,3262623]

def test_calculation_is_deterministic_and_exploratory_only():
    a=m.calculate(); b=m.calculate()
    assert m.canon(a)==m.canon(b)
    assert a['round_1238_plus_used'] is False
    assert a['promotion_candidate'] is False
    assert a['numeric_stability']['tolerance_pass'] is True
