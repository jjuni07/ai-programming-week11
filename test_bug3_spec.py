from bug3_logic import count_pass, find_max


def test_generated_expectation_for_find_max_matches_specification():
    assert find_max([70, 85, 60, 95]) == 95


def test_generated_expectation_includes_cutoff_score():
    assert count_pass([60, 60, 59]) == 2