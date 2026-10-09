# AI Inspection Contract — Python 최소 재현

판정과 설명을 다른 반환 계약으로 분리하는 독립 예제입니다. 합성 점수와 메모리 레코드만 사용하며 모델 추론·DB·원본 제조 데이터는 없습니다.

## 설계

[`inspection.py`](inspection.py)의 `judge()`는 고정된 `PolicySnapshot`으로 판정합니다. `Inspection`에는 판정·점수·snapshot이 있고 `explain()`은 별도 `Explanation`만 반환합니다. 설명 실패는 대체 설명과 검토 필요 상태로 남기며 판정 필드를 갱신하지 않습니다.

snapshot과 판정은 frozen dataclass입니다. 임계값·점수는 float를 거치지 않는 `Decimal`이며 JSON에는 문자열로 저장합니다. 과거 레코드의 snapshot 부재는 `None`으로 유지하고 새 설정으로 추정하지 않습니다.

## 실행

Python 3.10+의 표준 라이브러리만 사용합니다. 저장소 루트에서 예제 폴더로 이동해 실행하세요.

```sh
cd examples/inspection-contract
python -B -m unittest -v test_inspection
python -B demo.py
```

데모는 합성 점수를 판정하고 설명 실패 전후 판정 레코드가 같음을 출력합니다. 임계값·버전 문자열은 이 예제를 위해 만든 값입니다.

## 테스트

[`test_inspection.py`](test_inspection.py)의 18개 테스트가 다음을 검사합니다.

- 임계값 미만·동일값·점수 없음의 정상·결함·미분류 판정.
- 설명 성공·실패·빈 응답 전후 판정 유지, 프로그래밍 오류 전파.
- immutable 판정·snapshot, JSON 정밀도와 버전 보존.
- 정책 변경 후 과거 결과 유지, 반환 레코드 변경의 영향 분리.
- snapshot 없음·null·점수 없음의 과거 기록 호환, 과거 설명의 계보 미생성.
- float·비유한값·범위 밖 입력·알 수 없는 판정 거절.

## 범위

Decimal 문자열 저장의 계약만 검증합니다. 실제 SQL 컬럼·migration·트랜잭션·비동기 큐·VLM 게이트·사람 검토 UI는 구현하지 않습니다. frozen dataclass는 협력적인 프로그램 계약이며 악의적인 코드에 대한 보안 격리는 아닙니다.

과거 데이터 호환은 `decision`과 문자열 또는 누락된 `score`, 부재 또는 null인 `policy` 형식에 한정합니다. 모든 기존 제품 스키마의 호환을 주장하지 않습니다.

[설계](../../cases/b-ancla-inspection.md) · [실행 결과](../../evidence/test-results.md) · [소개](../../README.md)
