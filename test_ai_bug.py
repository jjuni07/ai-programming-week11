import pytest

from bug3_logic import find_max  # 받은 원문은 "from scores import find_max" — 모듈명 한 줄만 바꿈


# ---------- 정상 케이스 ----------
def test_max_in_middle():
    assert find_max([1, 5, 3]) == 5


def test_max_at_first():
    assert find_max([9, 2, 4, 1]) == 9


def test_max_at_last():
    # 마지막 원소가 최댓값인 경우 (range 상한 오류 검출)
    assert find_max([1, 2, 3, 10]) == 10


def test_ascending_order():
    assert find_max([1, 2, 3, 4, 5]) == 5


def test_descending_order():
    assert find_max([5, 4, 3, 2, 1]) == 5


def test_float_values():
    assert find_max([1.5, 2.5, 0.5]) == 2.5


def test_mixed_int_and_float():
    assert find_max([1, 2.5, 2]) == 2.5


def test_tuple_input():
    assert find_max((3, 7, 5)) == 7


# ---------- 경계값 케이스 ----------
def test_single_element():
    assert find_max([42]) == 42


def test_two_elements_first_larger():
    assert find_max([8, 3]) == 8


def test_two_elements_second_larger():
    # 길이 2: 루프가 한 번도 돌지 않는 버그 검출
    assert find_max([3, 8]) == 8


def test_three_elements_last_largest():
    assert find_max([1, 2, 3]) == 3


def test_all_equal_values():
    assert find_max([7, 7, 7, 7]) == 7


def test_duplicate_max_values():
    assert find_max([5, 9, 9, 2]) == 9


def test_all_negative_numbers():
    assert find_max([-5, -2, -9, -1]) == -1


def test_negative_and_positive():
    assert find_max([-10, 0, 10, -5]) == 10


def test_zero_values():
    assert find_max([0, 0, 0]) == 0


def test_large_numbers():
    assert find_max([10**18, 10**18 + 1, 10**17]) == 10**18 + 1


def test_does_not_modify_input():
    data = [3, 1, 4, 1, 5]
    original = data.copy()
    find_max(data)
    assert data == original


def test_matches_builtin_max():
    data = [4, 8, 15, 16, 23, 42]
    assert find_max(data) == max(data)


# ---------- 예외 케이스 ----------
def test_empty_list_raises_index_error():
    with pytest.raises(IndexError):
        find_max([])


def test_none_raises_type_error():
    with pytest.raises(TypeError):
        find_max(None)


def test_int_input_raises_type_error():
    with pytest.raises(TypeError):
        find_max(123)


def test_non_comparable_elements_raise_type_error():
    with pytest.raises(TypeError):
        find_max([1, "a", 3])


@pytest.mark.parametrize(
    "scores, expected",
    [
        ([1, 2, 3], 3),
        ([3, 2, 1], 3),
        ([2, 3, 1], 3),
        ([-1, -2, -3], -1),
        ([0], 0),
        ([1, 1, 2], 2),
    ],
)
def test_parametrized_cases(scores, expected):
    assert find_max(scores) == expected
