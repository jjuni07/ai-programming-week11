# 성적 관리 프로그램

## 무엇을 하나요 (What)
성적 CSV 파일을 읽어 유효한 `(이름, 점수)` 목록(점수는 0~100 정수)을 돌려주고, 건너뛴 줄과 그 이유를 함께 기록한다.

## 왜 만들었나요 (Why)
실제 성적 파일에는 빈 칸, 범위 밖 점수, 열 개수가 틀린 줄, 이름이 같은 사람이 섞여 있다. 그냥 읽으면 프로그램이 죽거나 잘못된 점수가 조용히 섞여 들어간다. 그래서 잘못된 줄은 버리되 어느 줄을 왜 버렸는지 남기고, 동명이인일 수 있는 중복 이름은 지우지 않고 모두 보존하도록 만들었다. 이 프로그램의 목적은 이 약속이 지켜지는지를 테스트로 확인하는 것이다.

## 어떻게 쓰나요 (How)
Python 3.10 이상이 필요하다. 프로젝트 폴더에서 실행한다.

```
python load_scores.py scores.csv
```

경로를 생략하면 `scores.csv`를 읽는다. 파일이 없으면 `FileNotFoundError`가 그대로 발생한다.

## 어떻게 테스트하나요 (Tests)
```
python -m pip install pytest pytest-cov
python -m pytest test_load_scores.py
python -m pytest --cov=load_scores --cov-report=term-missing test_load_scores.py
```

기대하는 화면:

```
test_load_scores.py .....................                                [100%]
21 passed
```

나머지 묶음의 기대 결과:

| 명령 | 기대 결과 |
|---|---|
| `python -m pytest test_ai_A.py` | 38 passed |
| `python -m pytest test_ai_B.py` | 33 passed, 1 failed (AI가 만든 기대값이 틀림, 수정하지 않고 보존) |
| `python -m pytest test_ai_bug.py` | 22 passed, 8 failed (고장난 `bug3_logic.py`의 버그를 잡아냄) |
| `python -m pytest test_fixed.py` | 6 passed (수정본 `bug3_fixed.py`) |
| `python -m pytest test_bug3_spec.py` | 2 failed (명세 기준 기대값이 고장난 원본을 잡아냄) |

## 파일 구성 (Files)
| 파일 | 역할 |
|---|---|
| `load_scores.py` | 성적 CSV 로더 |
| `scores.csv` · `empty.csv` · `weird.csv` | 정상 · 헤더만 있는 · 이상한 입력 자료 |
| `test_load_scores.py` | 명세만 보고 직접 설계해 작성한 테스트 |
| `test_ai_A.py` · `test_ai_B.py` | AI에게 코드를 줬을 때 · 명세를 줬을 때 받은 테스트(수정 없음) |
| `bug3_logic.py` · `test_ai_bug.py` | 의도적으로 고장낸 코드와 그 코드로 받은 AI 테스트 |
| `bug3_fixed.py` · `test_fixed.py` | 고친 코드와 회귀 테스트 |
| `test_bug3_spec.py` | 명세 기준 기대값으로 고장난 원본의 버그를 확인 |
| `prompts.txt` | 실험 프롬프트 원문 |
| `WORKSHEET.md` | 제출 워크시트 |
| `LICENSE` | MIT 라이선스 |

## 만든 사람 · AI 사용 (Author & AI)
- 만든 사람: 윤승준 (자율전공, 2026100463)
- AI 사용: 테스트 설계와 코드 이해는 직접 했고, README·워크시트 문장 다듬기와 A/B/함정 비교용 테스트 생성에 Claude를 사용했다. `test_ai_A.py`, `test_ai_B.py`, `test_ai_bug.py`는 `prompts.txt` 프롬프트로 받은 결과를 수정하지 않고 저장했다(`test_ai_bug.py`는 import 모듈명 한 줄만 변경).
