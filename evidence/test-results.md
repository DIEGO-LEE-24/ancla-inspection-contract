# 분리 후 독립 계약 예제 실행 결과

실행일: 2026-10-09. 분리한 Python 예제를 다시 실행했습니다. 원본 ANCLA의 모델·DB·CI·시연·운영 검증 결과가 아닙니다.

## 환경·결과

Windows, Python3.12.10 표준 라이브러리. 외부 패키지 설치·API 키·네트워크 없이 실행했습니다. Python 최소 요구 버전 전체의 호환성 시험은 하지 않았습니다.

| 테스트 | 통과 | 실패 | skip | 종료 코드 |
|---:|---:|---:|---:|---:|
| 18 | 18 | 0 | 0 | 0 |

테스트 메서드 수이며 subTest 입력을 별도로 중복 집계하지 않습니다.

## 실행 명령

저장소 루트에서 예제 폴더로 이동해 실행했습니다.

```sh
cd examples/inspection-contract
python -B -m unittest -v test_inspection
```

확인한 출력:

```text
Ran 18 tests
OK
```

README의 `python -B demo.py`도 종료 코드0으로 실행해 설명 실패 전후 동일한 판정 레코드와 대체 설명을 확인했습니다. 합성 점수·정책이며 실제 모델 추론·DB 쓰기를 실행하지 않았습니다.

## 파일 동일성과 식별

아래3개 구현·테스트·데모를 기존 통합 예제와 SHA-256으로 대조해 모두 동일함을 확인했습니다. 새 기능이나 테스트를 추가하지 않았습니다. 통합 폴더의 기존22개 파일은 변경하지 않았습니다. 분리 후 검증 당시에는 파일 해시로 실행 버전을 식별했습니다.

| 파일 | SHA-256 |
|---|---|
| [inspection.py](../examples/inspection-contract/inspection.py) | `f6320265a0ce4526480ba9b6b719291c6af8cd4b51bc640310c676a97755166b` |
| [test_inspection.py](../examples/inspection-contract/test_inspection.py) | `8d4e34c96e71a6875fbc9cb0fae1d096684d903bd42bac5e9cf0d4062613938f` |
| [demo.py](../examples/inspection-contract/demo.py) | `a2ccf09f6131cae2c927295f9dcb52c29f127d49b2dc447be67d1c7f20f91c61` |

정밀도 검증은 Decimal 문자열의 메모리·JSON 왕복 계약입니다. 실제 SQL 정밀도·DB migration·VLM 품질·비동기 복구·전체 제품 호환은 시험하지 않았습니다. 코드 변경 시 다시 실행하고 파일 식별을 갱신해야 합니다.

## 로컬 구성 검수

정적 점검은 허용 파일11개·로컬 링크29개·Mermaid2개를 확인했고 검출 문제는0건입니다. 통합 폴더22개 파일의 분리 전후 해시도 모두 같았습니다. 위 수치는 분리 후 로컬 검증 기록입니다. 공개 범위는 프로젝트명·일반 소개와 독립 예제 자료로 한정합니다.

[근거 기준](README.md) · [소개](../README.md)
