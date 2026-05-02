---
name: python-conventions
description: 이 프로젝트에서 파이썬 코드를 작성하거나 수정할 때 사용. 특히 컴프리헨션, 제너레이터, join, 메서드 체이닝 등 한 줄에 두 개 이상의 변환을 쓰려고 할 때 반드시 확인.
---

# 파이썬 컨벤션

## 빽빽한 한 줄보다 풀어 쓴 표현식

**복잡한 표현식은 중간 변수로 끊어서 작성한다.** 각 변수 이름이 그 자체로 "무엇을 계산하는가"를 설명하는 인라인 문서 역할을 한다. 읽는 사람에게 한 박자 쉴 자리를 준다.

## 하지 말 것

```python
conditions_text = "\n".join(f"{i}. {c}" for i, c in enumerate(complete_conditions))
```

```python
result = [(k, v) for k, v in d.items() if v > 0 and k.startswith("_")]
```

```python
return sorted([x for x in items if x.active], key=lambda x: x.created_at, reverse=True)
```

## 권장

```python
numbered_conditions = (f"{i}. {c}" for i, c in enumerate(complete_conditions))
conditions_text = "\n".join(numbered_conditions)
```

```python
private_items = ((k, v) for k, v in d.items() if k.startswith("_"))
positive_private = [(k, v) for k, v in private_items if v > 0]
result = positive_private
```

```python
active_items = [x for x in items if x.active]
return sorted(active_items, key=lambda x: x.created_at, reverse=True)
```

## 이유

- 변수 이름이 곧 인라인 문서 역할을 한다 — 주석이 따로 필요 없다
- 디버거에서 중간 값마다 멈춰서 확인할 수 있다
- 인지 부하가 줄어든다 — 빽빽한 한 줄을 해독하는 것보다 의도가 명시된 세 줄을 읽는 게 쉽다
- 예외나 스택 트레이스가 어느 변환 단계에서 터졌는지 정확히 가리킨다

## 한 줄로 둬도 되는 경우

- **단일 변환**: `upper = s.upper()`, `total = sum(xs)`, `pairs = list(zip(a, b))`
- **관용 패턴**: `", ".join(names)`, `[x.id for x in items]`
- **사소한 필터**: `[x for x in xs if x]`

## 판단 기준

표현식 안에 **두 개 이상의 변환**(filter+map, 제너레이터+join, sort+filter 등)이 쌓여 있다면 → 끊어서 작성한다.

## 빨간불 체크리스트

| 작성한 코드 | 끊어 써야 한다는 신호 |
|---|---|
| `"".join(f"..." for ... in ...)` | join 안에 제너레이터 → 제너레이터에 이름을 붙여라 |
| `[... for ... in ... if ...]`에 map과 filter가 모두 있음 | 필터된 컬렉션에 이름을 붙이고 그 다음에 map |
| `sorted([x for x in ...], key=...)` | 리스트에 이름을 붙이고 그 다음에 sort |
| `map`/`filter`/`sorted` 안에 본문이 자명하지 않은 lambda | 이름 붙은 함수로 추출 |
| `.filter().map().reduce()` 식의 체이닝 | 각 단계마다 변수 이름 부여 |
