# 멀티에이전트 벤치마크 분석

## 요약

MS Agent Framework가 LangGraph보다 빠르고 토큰이 적게 나온 원인 분석
결론: **프레임워크 자체의 차이가 아니라 built-in으로 구현된 multi-agent 패턴과 기본 Agent간 context 전달 패턴의 차이**

LangGraph 구현을 MS Agent과 동일한 패턴으로 수정하고, GPT-4.1에서 수동 토큰 측정으로 검증한 결과
**두 프레임워크의 토큰 사용량과 레이턴시는 사실상 동일**했음.

---

## 1. 기존 벤치마크의 문제

### 1.1 기존 결과 (Qwen3:14b, Ollama)

| Framework | Quality | Latency | Total Tokens |
|-----------|---------|---------|-------------|
| **MS Agent** | **9.87** | **93s** | **7,006** |
| LangGraph | 9.42 | 506s | 8,823 |
| AutoGen | 9.63 | 572s | 10,793 |

MS Agent이 압도적으로 좋아 보이지만, 두가지 문제 존재

### 문제 1: 프롬프트 패턴이 다르다

기존 벤치마크에서 **LangGraph은 "Independent" 패턴**, **MS Agent은 "Shared context" 패턴**으로 구현되어 있었음.

**패턴 A — Independent 호출 방식 (기존 LangGraph)**

이전 에이전트의 출력을 `user` 메시지 텍스트에 삽입:

```python
messages = [
    {"role": "system", "content": "You are an analyst..."},
    {"role": "user", "content": f"Analyze these facts:\n\n{research}"},
]
```

모델은 이전 출력을 "사용자가 준 참고 자료"로 인식하여
**독립적이고 포괄적인 답변**을 작성한다. → output 증가

**패턴 B — Shared Context (기존 MS Agent)**

이전 에이전트의 출력을 `assistant` 메시지로 대화 이력에 추가:

```python
messages = [
    {"role": "system", "content": "You are an analyst..."},
    {"role": "user", "content": "사용자 요청..."},
    {"role": "assistant", "content": research_msg.content},
]
```

모델은 이전 출력을 "이전 대화에서 나온 내용"으로 인식하여
**중복 없이 자기 역할만 수행**한다. → output이 간결해짐

### 문제 2: 토큰 측정이 부정확

모든 프레임워크의 토큰값에 누락이 있었음:

| Framework | 보고값 | 실제 (수동 측정) | 누락률 |
|-----------|-------|----------------|-------|
| MS Agent (Qwen3) | 7,006 | ~10,500 추정 | ~33% |
| LangGraph (GPT-4.1) | 5,337 | 8,628 | 38% |

- MS Agent: `WorkflowRunResult` 이벤트 순회에서 일부 에이전트 usage 누락
- LangGraph: `UsageMetadataCallbackHandler`가 일부 호출 누락

---

## 2. 공정한 비교: 동일 패턴 + 수동 측정

### 2.1 수정 내용

LangGraph 구현을 MS Agent과 동일한 패턴으로 수정:

1. **Team Task**: 모든 에이전트가 같은 user message(검색 데이터 포함)를 받음
2. **Shared Context**: 이전 에이전트 출력을 `AIMessage`로 누적
3. **Manual Token Measurement**: 에이전트별 `UsageMetadataCallbackHandler`로 개별 측정 후 합산

```python
# 수정 후 LangGraph analyst Node
def analyst(state, llm):
    messages = [
        SystemMessage(content=ANALYST_SYSTEM.format(company=company)),
        HumanMessage(content=state["task"]),     # Team Task (MS Agent과 동일)
        *state["history"],                        # AIMessage 리스트 (공유 대화)
    ]
    response = llm.invoke(messages)
    return {"history": [AIMessage(content=response.content)]}
```

### 2.2 GPT-4.1 기준 결과 

| | LangGraph | MS Agent | 차이 |
|---|---------|---------|------|
| **Input Tokens** | 5,355 | 5,441 | +86 (+1.6%) |
| **Output Tokens** | 3,167 | 3,206 | +39 (+1.2%) |
| **Total Tokens** | **8,522** | **8,647** | **+125 (+1.5%)** |
| **Latency** | **33.8s** | **34.3s** | **+0.5s (+1.5%)** |

**토큰: 1.5% 차이. 레이턴시: 0.5초 차이. 사실상 동일**

---

## 3. 핵심 발견

### 3.1 프레임워크 차이가 아니라 패턴 차이였음

기존 벤치마크에서 보인 "MS Agent 4배 효율적" 결과는:
- **Independent (패턴 A) vs Shared Context (패턴 B)** 비교였음
- 커스텀하게 개발을 추가하여 동일 패턴으로 맞추면 **1.5% 차이** — 프레임워크 간 본질적 차이 미비함

### 3.2 패턴 B의 실질적 효과

패턴 A(독립)에서 패턴 B(공유 대화)로 전환하면:

| 지표 | 패턴 A (독립) | 패턴 B (공유) | 변화 |
|-----|-------------|-------------|------|
| Total Tokens | ~8,800 | ~8,500 | -3% |
| Output Tokens | ~5,300 | ~3,200 | **-40%** |
| Input Tokens | ~3,500 | ~5,400 | +54% |

- **Output이 40% 감소**: 모델이 대화를 이어가므로 중복 없이 간결하게 응답
- **Input이 54% 증가**: 이전 에이전트 출력이 대화 이력으로 누적
- **Total은 큰 차이 없음**: output 감소와 input 증가가 상쇄

로컬 모델(Ollama)에서는 output 토큰 생성이 병목(~15-20 tok/s)이므로,
output 40% 감소가 **레이턴시에 직접적인 영향**을 미친다. → 기존 Qwen3에서 93초 vs 506초 차이의 핵심 원인.

### 3.3 프레임워크별 기본 동작의 차이

| 프레임워크 | 기본 패턴 | 설명 |
|-----------|---------|------|
| MS Agent | **B (자동)** | `SequentialBuilder`가 대화 이력 누적을 자동 처리 |
| AutoGen | **B (자동)** | `RoundRobinGroupChat`이 대화 이력을 자동 누적 |
| LangGraph | **선택 (수동)** | 구현자가 state 설계로 패턴을 직접 선택 |
| Agents SDK | **선택 (수동)** | 구현자가 메시지 조립 방식을 직접 선택 |

MS Agent/AutoGen은 기본 동작이 공유 대화이므로 별도 코드 없이 패턴 B를 사용.
LangGraph은 범용 그래프이므로 구현자가 state 설계로 패턴을 직접 구현해야 함. 기본 구현 샘플은 Independent 패턴이라 MS Agent과 비교 시 불리하게 보일 수 밖에 없음. (이또한 차이는 차이)

### 3.4 토큰 측정은 프레임워크 빌트인을 신뢰하면 안 됨

| Framework | 측정 방식 | 누락 여부 |
|-----------|---------|---------|
| LangGraph | `UsageMetadataCallbackHandler` | ⚠️ 일부 호출 누락 발생 |
| MS Agent | `WorkflowRunResult` 이벤트 순회 | ⚠️ 일부 에이전트 누락 발생 |
| AutoGen | `msg.models_usage` 직접 접근 | ✅ 정확 |
| Agents SDK | `raw_responses.usage` 직접 접근 | ✅ 정확 |

**권장**: API 레벨에서 각 호출의 `usage`를 직접 집계하는 것이 가장 정확하다.

---

## 4. 결론

| 항목 | 기존 벤치마크 결론 | 수정 후 실제 결론 |
|-----|-----------------|----------------|
| 토큰 효율성 | MS Agent 4배 효율 | **동일** (1.5% 차이) |
| 레이턴시 | MS Agent 5배 빠름 | **동일** (GPT-4.1), 로컬 모델에서는 패턴 차이로 다름 |
| 품질 | MS Agent 최고 | **동등** (9.4–9.6 범위) |
| 핵심 변인 | 프레임워크 | **프롬프트 패턴** (독립 vs 공유 대화) |

**멀티에이전트 파이프라인의 성능은 "어떤 프레임워크를 쓰느냐"보다
"어떤 메시지 전달 패턴으로 구현"하느냐가 더 크게 좌우된다.**
