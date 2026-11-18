import pytest

from bug3_fixed import count_pass, find_max


def test_find_max_includes_the_last_score():
    assert find_max([70, 85, 60, 95]) == 95


def test_find_max_handles_a_single_score():
    assert find_max([42]) == 42


@pytest.mark.parametrize(
    ("scores", "expected"),
    [([70, 85, 95], 3), ([60, 60, 59], 2), ([], 0)],
)
def test_count_pass_includes_cutoff(scores, expected):
    assert count_pass(scores) == expected


def test_count_pass_uses_custom_cutoff():
    assert count_pass([69, 70, 71], cutoff=70) == 2