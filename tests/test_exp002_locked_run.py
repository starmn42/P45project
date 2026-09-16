from p45_experiments.exp002.locked_run import exact_baseline,summarize

def test_exact_baselines_are_valid_and_distinct():
    assert 0 < exact_baseline("MAIN") < exact_baseline("INTEGRATED") < 1

def test_primary_and_support_are_not_combined():
    outcomes=[{"main_a":3,"main_b":0,"integrated_a":3,"integrated_b":0},
              {"main_a":2,"main_b":1,"integrated_a":2,"integrated_b":1}]
    null={"main_p_upper":1.0,"integrated_p_upper":1.0}
    s=summarize([{"eligible":True}]*2,outcomes,null)
    assert s["main_primary"]==1
    assert s["main_exact2_support"]=={"A":1,"B":0}

def test_empty_is_inconclusive_without_forced_output():
    s=summarize([{"eligible":False}],[],{"main_p_upper":1.0,"integrated_p_upper":1.0})
    assert s["fallback_pick_rounds"]==0 and s["final_judgment"]=="INCONCLUSIVE"
