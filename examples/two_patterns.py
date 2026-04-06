"""두 가지 멀티에이전트 프롬프트 패턴 비교 (OpenAI SDK 기준).

Pattern A: 독립 호출 (LangGraph 방식)
  - 각 에이전트가 매번 새 메시지 리스트를 받음
  - 이전 출력을 user 메시지 텍스트에 삽입

Pattern B: 공유 대화 (MS Agent Framework 방식)
  - 하나의 messages 리스트를 이어가며 누적
  - 이전 출력이 assistant 메시지로 자연스럽게 쌓임
"""

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
MODEL = "qwen3:14b"
COMPANY = "Anthropic"


# ──────────────────────────────────────────────
# Pattern A: 독립 호출 (LangGraph 방식)
# ──────────────────────────────────────────────
def pattern_a_independent():
    """각 에이전트가 독립적으로 LLM을 호출한다."""

    # 1) Researcher: 새 대화 시작
    r1 = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": f"You are a researcher on {COMPANY}."},
            {"role": "user", "content": f"List 3 key facts about {COMPANY}."},
        ],
    )
    research = r1.choices[0].message.content

    # 2) Analyst: 새 대화 시작 (researcher 출력을 텍스트로 삽입)
    r2 = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": f"You are an analyst on {COMPANY}."},
            {"role": "user", "content": f"Analyze these facts:\n\n{research}"},
            #                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #                              이전 출력을 user 메시지에 텍스트로 삽입
        ],
    )
    analysis = r2.choices[0].message.content

    # 3) Writer: 새 대화 시작 (둘 다 텍스트로 삽입)
    r3 = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": f"You are a report writer on {COMPANY}."},
            {"role": "user", "content": (
                f"Write a short report.\n\n"
                f"## Research\n{research}\n\n"
                f"## Analysis\n{analysis}"
            )},
        ],
    )
    report = r3.choices[0].message.content

    tokens = sum(r.usage.total_tokens for r in [r1, r2, r3])
    return report, tokens


# ──────────────────────────────────────────────
# Pattern B: 공유 대화 (MS Agent Framework 방식)
# ──────────────────────────────────────────────
def pattern_b_shared():
    """하나의 messages 리스트를 누적하며 이어간다."""

    task = {"role": "user", "content": (
        f"Research and write a report about {COMPANY}. "
        f"Researcher: list 3 key facts. "
        f"Analyst: analyze them. "
        f"Writer: write the final short report."
    )}

    total_tokens = 0

    # 1) Researcher
    messages = [
        {"role": "system", "content": f"You are a researcher on {COMPANY}."},
        task,
    ]
    r1 = client.chat.completions.create(model=MODEL, temperature=0, messages=messages)
    research_msg = r1.choices[0].message
    total_tokens += r1.usage.total_tokens

    # 2) Analyst: 같은 대화에 researcher 응답을 assistant로 추가
    messages = [
        {"role": "system", "content": f"You are an analyst on {COMPANY}."},
        task,
        {"role": "assistant", "content": research_msg.content},  # ← 대화 누적
    ]
    r2 = client.chat.completions.create(model=MODEL, temperature=0, messages=messages)
    analysis_msg = r2.choices[0].message
    total_tokens += r2.usage.total_tokens

    # 3) Writer: researcher + analyst 응답이 모두 대화에 누적
    messages = [
        {"role": "system", "content": f"You are a report writer on {COMPANY}."},
        task,
        {"role": "assistant", "content": research_msg.content},   # researcher 출력
        {"role": "assistant", "content": analysis_msg.content},   # analyst 출력
    ]
    r3 = client.chat.completions.create(model=MODEL, temperature=0, messages=messages)
    total_tokens += r3.usage.total_tokens

    return r3.choices[0].message.content, total_tokens


if __name__ == "__main__":
    print("=" * 60)
    print("Pattern A: 독립 호출 (LangGraph 방식)")
    print("=" * 60)
    report_a, tokens_a = pattern_a_independent()
    print(report_a[:500])
    print(f"\n총 토큰: {tokens_a}")

    print("\n" + "=" * 60)
    print("Pattern B: 공유 대화 (MS Agent 방식)")
    print("=" * 60)
    report_b, tokens_b = pattern_b_shared()
    print(report_b[:500])
    print(f"\n총 토큰: {tokens_b}")
