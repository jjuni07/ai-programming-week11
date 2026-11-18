import runpy
import sys
from pathlib import Path

import pytest

from load_scores import load_scores

DATA_DIR = Path(__file__).parent


def write_csv(tmp_path, contents):
    path = tmp_path / "scores.csv"
    path.write_text(contents, encoding="utf-8")
    return path


def test_normal_file_loads_valid_scores():
    kept, skipped = load_scores(DATA_DIR / "scores.csv")

    assert kept == [
        ("김하나", 88),
        ("최,네번", 77),
        ("김하나", 91),
        ("윤보람", 64),
        ("서한별", 95),
    ]
    assert len(skipped) == 5


def test_blank_lines_are_ignored(tmp_path):
    path = write_csv(tmp_path, "name,score\n가나다,80\n\n라마바,90\n")

    kept, skipped = load_scores(path)

    assert kept == [("가나다", 80), ("라마바", 90)]
    assert skipped == []


def test_quoted_comma_in_name_is_preserved():
    kept, skipped = load_scores(DATA_DIR / "scores.csv")

    assert ("최,네번", 77) in kept
    assert all("최,네번" not in original for _, original, _ in skipped)


def test_duplicate_names_are_both_kept():
    kept, _ = load_scores(DATA_DIR / "scores.csv")

    assert [score for name, score in kept if name == "김하나"] == [88, 91]


def test_weird_fixture_keeps_trimmed_scores_and_skips_invalid_rows():
    kept, skipped = load_scores(DATA_DIR / "weird.csv")

    assert kept == [("한겨울", 77), ("윤보람", 88)]
    assert len(skipped) == 7


def test_missing_file_raises_file_not_found_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "missing.csv")


def test_header_only_file_returns_empty_results():
    assert load_scores(DATA_DIR / "empty.csv") == ([], [])


def test_empty_file_returns_empty_results(tmp_path):
    path = write_csv(tmp_path, "")

    assert load_scores(path) == ([], [])


@pytest.mark.parametrize(
    ("score", "is_valid"),
    [(-1, False), (0, True), (1, True), (99, True), (100, True), (101, False)],
)
def test_score_boundaries(tmp_path, score, is_valid):
    path = write_csv(tmp_path, f"name,score\n가나다,{score}\n")

    kept, skipped = load_scores(path)

    assert (len(kept) == 1) is is_valid
    assert len(skipped) == (0 if is_valid else 1)


@pytest.mark.parametrize(
    ("row", "reason"),
    [
        ("이름만있음", "열 개수가 2가 아님"),
        ("가나다,80,추가", "열 개수가 2가 아님"),
        (",80", "이름이 비어 있음"),
        ("가나다,", "점수가 비어 있음"),
        ("가나다,결석", "점수가 정수가 아님"),
        ("가나다,101", "점수가 0~100 밖"),
    ],
)
def test_invalid_rows_are_recorded(tmp_path, row, reason):
    path = write_csv(tmp_path, f"name,score\n{row}\n")

    kept, skipped = load_scores(path)

    assert kept == []
    assert len(skipped) == 1
    assert skipped[0][1:] == (row, reason)

def test_command_line_prints_kept_and_skipped_counts(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["load_scores.py", str(DATA_DIR / "scores.csv")])

    runpy.run_path(str(DATA_DIR / "load_scores.py"), run_name="__main__")

    out = capsys.readouterr().out
    assert "읽은 줄 : 5개" in out
    assert "건너뛴 줄 : 5개" in out
    assert "점수가 0~100 밖" in out
