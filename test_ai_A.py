# test_load_scores.py
import pytest

from load_scores import load_scores, MIN_SCORE, MAX_SCORE


def write_csv(tmp_path, text, encoding="utf-8", name="scores.csv"):
    """테스트용 CSV 파일을 만들고 경로를 돌려준다."""
    p = tmp_path / name
    p.write_bytes(text.encode(encoding))
    return str(p)


# ---------------------------------------------------------------
# 정상 케이스
# ---------------------------------------------------------------
def test_normal_rows_are_loaded(tmp_path):
    path = write_csv(tmp_path, "name,score\n홍길동,90\n김철수,75\n이영희,60\n")
    kept, skipped = load_scores(path)
    assert kept == [("홍길동", 90), ("김철수", 75), ("이영희", 60)]
    assert skipped == []


def test_header_is_not_included(tmp_path):
    path = write_csv(tmp_path, "name,score\n홍길동,90\n")
    kept, skipped = load_scores(path)
    assert ("name", "score") not in kept
    assert len(kept) == 1
    assert skipped == []


def test_header_only_returns_empty(tmp_path):
    path = write_csv(tmp_path, "name,score\n")
    assert load_scores(path) == ([], [])


def test_whitespace_is_stripped(tmp_path):
    path = write_csv(tmp_path, "name,score\n  홍길동  ,  85  \n")
    kept, skipped = load_scores(path)
    assert kept == [("홍길동", 85)]
    assert skipped == []


def test_order_is_preserved(tmp_path):
    path = write_csv(tmp_path, "name,score\nC,1\nA,2\nB,3\n")
    kept, _ = load_scores(path)
    assert [n for n, _ in kept] == ["C", "A", "B"]


def test_duplicate_names_are_both_kept(tmp_path):
    path = write_csv(tmp_path, "name,score\n홍길동,90\n홍길동,80\n")
    kept, skipped = load_scores(path)
    assert kept == [("홍길동", 90), ("홍길동", 80)]
    assert skipped == []


def test_utf8_bom_is_handled(tmp_path):
    path = write_csv(tmp_path, "name,score\n홍길동,90\n", encoding="utf-8-sig")
    kept, skipped = load_scores(path)
    assert kept == [("홍길동", 90)]
    assert skipped == []


def test_score_is_int_type(tmp_path):
    path = write_csv(tmp_path, "name,score\n홍길동,90\n")
    kept, _ = load_scores(path)
    assert isinstance(kept[0][1], int)


def test_constants():
    assert MIN_SCORE == 0
    assert MAX_SCORE == 100


# ---------------------------------------------------------------
# 경계값
# ---------------------------------------------------------------
@pytest.mark.parametrize("score", [0, 1, 99, 100])
def test_boundary_scores_are_accepted(tmp_path, score):
    path = write_csv(tmp_path, f"name,score\n홍길동,{score}\n")
    kept, skipped = load_scores(path)
    assert kept == [("홍길동", score)]
    assert skipped == []


@pytest.mark.parametrize("score", [-1, 101, -100, 1000])
def test_out_of_range_scores_are_skipped(tmp_path, score):
    path = write_csv(tmp_path, f"name,score\n홍길동,{score}\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert skipped == [(2, f"홍길동,{score}", "점수가 0~100 밖")]


def test_line_number_counts_header_as_line_1(tmp_path):
    path = write_csv(tmp_path, "name,score\n홍길동,90\n김철수,abc\n")
    _, skipped = load_scores(path)
    assert skipped[0][0] == 3


def test_empty_file(tmp_path):
    path = write_csv(tmp_path, "")
    assert load_scores(path) == ([], [])


def test_no_trailing_newline(tmp_path):
    path = write_csv(tmp_path, "name,score\n홍길동,90")
    kept, skipped = load_scores(path)
    assert kept == [("홍길동", 90)]
    assert skipped == []


# ---------------------------------------------------------------
# 예외(잘못된 입력) 케이스
# ---------------------------------------------------------------
def test_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(str(tmp_path / "no_such_file.csv"))


def test_too_few_columns(tmp_path):
    path = write_csv(tmp_path, "name,score\n홍길동\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert skipped == [(2, "홍길동", "열 개수가 2가 아님")]


def test_too_many_columns(tmp_path):
    path = write_csv(tmp_path, "name,score\n홍길동,90,extra\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert skipped == [(2, "홍길동,90,extra", "열 개수가 2가 아님")]


def test_empty_name(tmp_path):
    path = write_csv(tmp_path, "name,score\n,90\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert skipped == [(2, ",90", "이름이 비어 있음")]


def test_whitespace_only_name(tmp_path):
    path = write_csv(tmp_path, "name,score\n   ,90\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert skipped[0][0] == 2
    assert skipped[0][2] == "이름이 비어 있음"


def test_empty_score(tmp_path):
    path = write_csv(tmp_path, "name,score\n홍길동,\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert skipped == [(2, "홍길동,", "점수가 비어 있음")]


def test_whitespace_only_score(tmp_path):
    path = write_csv(tmp_path, "name,score\n홍길동,   \n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert skipped[0][2] == "점수가 비어 있음"


@pytest.mark.parametrize("raw", ["abc", "9.5", "90점", "1e2", "--5", "NaN"])
def test_non_integer_score(tmp_path, raw):
    path = write_csv(tmp_path, f"name,score\n홍길동,{raw}\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert skipped == [(2, f"홍길동,{raw}", "점수가 정수가 아님")]


def test_empty_name_checked_before_empty_score(tmp_path):
    path = write_csv(tmp_path, "name,score\n,\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert skipped == [(2, ",", "이름이 비어 있음")]


def test_blank_lines_are_ignored_and_not_recorded(tmp_path):
    path = write_csv(tmp_path, "name,score\n\n홍길동,90\n\n\n김철수,80\n")
    kept, skipped = load_scores(path)
    assert kept == [("홍길동", 90), ("김철수", 80)]
    assert skipped == []


def test_blank_lines_still_count_toward_line_numbers(tmp_path):
    path = write_csv(tmp_path, "name,score\n\n홍길동,abc\n")
    _, skipped = load_scores(path)
    assert skipped == [(3, "홍길동,abc", "점수가 정수가 아님")]


def test_mixed_valid_and_invalid_rows(tmp_path):
    text = (
        "name,score\n"
        "홍길동,90\n"          # 2 정상
        "김철수,abc\n"         # 3 정수 아님
        "이영희,101\n"         # 4 범위 밖
        ",50\n"                # 5 이름 없음
        "박민수,\n"            # 6 점수 없음
        "최지우,70,x\n"        # 7 열 개수
        "\n"                   # 8 빈 줄
        "정하늘,100\n"         # 9 정상
    )
    path = write_csv(tmp_path, text)
    kept, skipped = load_scores(path)
    assert kept == [("홍길동", 90), ("정하늘", 100)]
    assert skipped == [
        (3, "김철수,abc", "점수가 정수가 아님"),
        (4, "이영희,101", "점수가 0~100 밖"),
        (5, ",50", "이름이 비어 있음"),
        (6, "박민수,", "점수가 비어 있음"),
        (7, "최지우,70,x", "열 개수가 2가 아님"),
    ]


def test_quoted_field_with_comma_counts_as_one_column(tmp_path):
    path = write_csv(tmp_path, 'name,score\n"홍,길동",90\n')
    kept, skipped = load_scores(path)
    assert kept == [("홍,길동", 90)]
    assert skipped == []
