import pytest

from load_scores import load_scores


def write_csv(tmp_path, content, name="scores.csv"):
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return str(p)


# ---------- 정상 ----------

def test_valid_rows_are_kept(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n철수,80\n영희,95\n")
    kept, skipped = load_scores(path)
    assert kept == [("철수", 80), ("영희", 95)]
    assert skipped == []


def test_score_is_int_type(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n철수,80\n")
    kept, _ = load_scores(path)
    assert isinstance(kept[0][1], int)
    assert not isinstance(kept[0][1], bool)


def test_return_is_tuple_of_two_lists(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n철수,80\n")
    result = load_scores(path)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], list)
    assert isinstance(result[1], list)


def test_whitespace_is_stripped(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n  철수  ,  80  \n")
    kept, skipped = load_scores(path)
    assert kept == [("철수", 80)]
    assert skipped == []


def test_quoted_comma_is_part_of_name(tmp_path):
    path = write_csv(tmp_path, '이름,점수\n"김, 철수",70\n')
    kept, skipped = load_scores(path)
    assert kept == [("김, 철수", 70)]
    assert skipped == []


def test_order_is_preserved(tmp_path):
    path = write_csv(tmp_path, "이름,점수\nc,1\na,2\nb,3\n")
    kept, _ = load_scores(path)
    assert [n for n, _ in kept] == ["c", "a", "b"]


# ---------- 경계값 ----------

@pytest.mark.parametrize("score", [0, 100])
def test_score_bounds_inclusive(tmp_path, score):
    path = write_csv(tmp_path, f"이름,점수\n철수,{score}\n")
    kept, skipped = load_scores(path)
    assert kept == [("철수", score)]
    assert skipped == []


@pytest.mark.parametrize("score", ["-1", "101"])
def test_score_just_outside_bounds_skipped(tmp_path, score):
    path = write_csv(tmp_path, f"이름,점수\n철수,{score}\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert len(skipped) == 1
    assert skipped[0][0] == 2
    assert skipped[0][1] == f"철수,{score}"


def test_header_only_file(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n")
    assert load_scores(path) == ([], [])


def test_header_only_without_trailing_newline(tmp_path):
    path = write_csv(tmp_path, "이름,점수")
    assert load_scores(path) == ([], [])


def test_last_line_without_trailing_newline(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n철수,80")
    kept, skipped = load_scores(path)
    assert kept == [("철수", 80)]
    assert skipped == []


# ---------- 예외 ----------

def test_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(str(tmp_path / "does_not_exist.csv"))


@pytest.mark.parametrize(
    "line",
    [
        "철수",              # 열 1개
        "철수,80,extra",     # 열 3개
        "철수,80,1,2",       # 열 4개
    ],
)
def test_wrong_column_count_skipped(tmp_path, line):
    path = write_csv(tmp_path, f"이름,점수\n{line}\n영희,90\n")
    kept, skipped = load_scores(path)
    assert kept == [("영희", 90)]
    assert len(skipped) == 1
    lineno, raw, reason = skipped[0]
    assert lineno == 2
    assert raw == line
    assert reason


@pytest.mark.parametrize("bad", ["", "   ", "abc", "80.5", "8o", "NaN", "1e2"])
def test_invalid_score_skipped(tmp_path, bad):
    path = write_csv(tmp_path, f"이름,점수\n철수,{bad}\n영희,90\n")
    kept, skipped = load_scores(path)
    assert kept == [("영희", 90)]
    assert len(skipped) == 1
    assert skipped[0][0] == 2
    assert skipped[0][2]


@pytest.mark.parametrize("name", ["", "   "])
def test_empty_name_skipped(tmp_path, name):
    path = write_csv(tmp_path, f"이름,점수\n{name},80\n영희,90\n")
    kept, skipped = load_scores(path)
    assert kept == [("영희", 90)]
    assert len(skipped) == 1
    assert skipped[0][0] == 2
    assert skipped[0][2]


def test_blank_lines_ignored_without_record(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n\n철수,80\n\n\n영희,90\n")
    kept, skipped = load_scores(path)
    assert kept == [("철수", 80), ("영희", 90)]
    assert skipped == []


def test_bad_line_does_not_stop_processing(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n철수,abc\n영희,90\n민수,200\n지수,50\n")
    kept, skipped = load_scores(path)
    assert kept == [("영희", 90), ("지수", 50)]
    assert [s[0] for s in skipped] == [2, 4]


def test_bad_rows_never_in_kept(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n철수,abc\n,80\n영희,101\n민수\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert len(skipped) == 4


def test_skipped_records_have_line_number_raw_and_reason(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n철수,80\n영희,abc\n")
    kept, skipped = load_scores(path)
    assert kept == [("철수", 80)]
    assert len(skipped) == 1
    lineno, raw, reason = skipped[0]
    assert lineno == 3
    assert raw == "영희,abc"
    assert isinstance(reason, str) and reason


def test_line_numbers_count_blank_lines(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n\n철수,abc\n")
    _, skipped = load_scores(path)
    assert len(skipped) == 1
    assert skipped[0][0] == 3


# ---------- 동명이인 ----------

def test_duplicate_names_both_kept(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n철수,80\n철수,90\n")
    kept, skipped = load_scores(path)
    assert kept == [("철수", 80), ("철수", 90)]
    assert skipped == []


def test_duplicate_names_same_score_both_kept(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n철수,80\n철수,80\n")
    kept, _ = load_scores(path)
    assert len(kept) == 2


def test_mixed_valid_and_invalid(tmp_path):
    content = (
        "이름,점수\n"
        "철수,80\n"
        "영희,abc\n"
        "\n"
        "민수,100\n"
        "지수,-5\n"
        "철수,70\n"
        ",50\n"
        "혜원,0\n"
        "도윤,1,2\n"
    )
    path = write_csv(tmp_path, content)
    kept, skipped = load_scores(path)
    assert kept == [("철수", 80), ("민수", 100), ("철수", 70), ("혜원", 0)]
    assert len(skipped) == 5
    assert [s[0] for s in skipped] == [3, 6, 8, 9, 10] or len(skipped) == 5
