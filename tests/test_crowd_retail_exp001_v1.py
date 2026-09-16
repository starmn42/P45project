from p45_experiments import crowd_retail_exp001_v1 as m

def test_hypergeometric_cell_probability():
    assert abs(m.p_ge2(5,2,2)-.1)<1e-12

def test_round_pmf_normalized():
    p=m.round_pmf([2,1,1],2)
    assert abs(p.sum()-1)<1e-12
    assert abs(p[1]-1/6)<1e-12

def test_locked_source_and_determinism():
    a=m.calculate();b=m.calculate()
    assert m.canon(a)==m.canon(b)
    assert a['round_1238_plus_used'] is False
    assert a['mode_store_count_mismatch']==0
    assert a['promotion_candidate'] is False
