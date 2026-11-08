"""活動公告檢查官：初稿 → AI 反思 → 修訂，外加可重現的欄位查核。"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
DEFAULT_OLLAMA_MODEL = "qwen2.5:14b"


def _colab_secret(name: str) -> str | None:
    try:
        from google.colab import userdata  # type: ignore[import-not-found]

        return userdata.get(name)
    except Exception:
        return None


class ChatModel:
    """優先用 Colab 的 Groq 金鑰；本機無金鑰時使用 Ollama。"""

    def __init__(self) -> None:
        self.api_key = (os.getenv("GROQ_API_KEY") or _colab_secret("Groq") or "").strip()
        self.backend = "Groq" if self.api_key else "Ollama"
        self.model = os.getenv("LAB8_MODEL") or (
            DEFAULT_GROQ_MODEL if self.api_key else DEFAULT_OLLAMA_MODEL
        )
        if not self.api_key:
            if "google.colab" in sys.modules:
                raise RuntimeError(
                    "Colab 讀不到 Groq API 金鑰。請在左側 🔑 密鑰新增 Name=Groq，"
                    "Value=Groq 官方網站建立的 API 金鑰，並打開這份筆記本的 Notebook access；"
                    "之後重新執行本格。不要把金鑰貼在程式碼或聊天室。"
                )
            try:
                urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2).close()
            except (urllib.error.URLError, TimeoutError) as exc:
                raise RuntimeError(
                    "找不到模型：請在 Colab 左側 🔑 設定 Groq 金鑰並開啟筆記本存取權；"
                    "或在本機啟動 Ollama 並下載 qwen2.5:14b。"
                ) from exc

    def complete(self, system: str, user: str, temperature: float = 0.3) -> str:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        if self.api_key:
            url = GROQ_URL
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 900,
            }
            # Groq 前端會擋掉 urllib 預設的 Python-urllib User-Agent（403/1010）。
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "taica-lab8-reflection-agent/1.0",
            }
        else:
            url = OLLAMA_URL
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": 900},
            }
            headers = {}
        request = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", **headers},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.load(response)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"{self.backend} 呼叫失敗（HTTP {exc.code}）：{detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"{self.backend} 連線失敗：{exc}") from exc
        answer = (
            data["choices"][0]["message"]["content"]
            if self.api_key
            else data["message"]["content"]
        )
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("模型沒有回傳文字。")
        return answer.strip()


@dataclass(frozen=True)
class Activity:
    title: str
    when: str
    where: str
    fee: str
    notes: str = ""

    def __post_init__(self) -> None:
        for label, value in self.required_facts().items():
            if not value or not value.strip():
                raise ValueError(f"請填寫「{label}」。")
            if len(value) > 120:
                raise ValueError(f"「{label}」請勿超過 120 字。")
        if len(self.notes) > 500:
            raise ValueError("補充資訊請勿超過 500 字。")

    def required_facts(self) -> dict[str, str]:
        return {
            "活動名稱": self.title.strip(),
            "時間": self.when.strip(),
            "地點": self.where.strip(),
            "費用": self.fee.strip(),
        }

    def as_json(self) -> str:
        return json.dumps(
            {**self.required_facts(), "補充資訊": self.notes.strip()},
            ensure_ascii=False,
            indent=2,
        )


def check_facts(text: str, activity: Activity) -> dict[str, bool]:
    """只檢查四個必填值是否逐字出現；不宣稱能判斷語意真偽。"""
    return {label: value in text for label, value in activity.required_facts().items()}


@dataclass(frozen=True)
class ReflectionResult:
    draft: str
    critique: str
    revised: str
    final: str
    before: dict[str, bool]
    after: dict[str, bool]
    repaired: tuple[str, ...]


def run_reflection(
    activity: Activity,
    complete: Callable[[str, str, float], str],
) -> ReflectionResult:
    """三次模型呼叫分別扮演撰稿、審稿、改稿；最後用程式補齊必填資訊。"""
    facts = activity.as_json()
    draft = complete(
        "你是大學活動文案編輯。只寫可直接發布的繁體中文公告，不要說明過程。"
        "只可使用提供的事實，不可編造報名連結、主辦單位、名額或截止日。"
        "請保留活動名稱、時間、地點、費用的原始字串。",
        f"請根據以下資料寫一則 100～220 字、語氣親切而清楚的活動公告：\n{facts}",
        0.6,
    )
    before = check_facts(draft, activity)
    missing_before = [label for label, present in before.items() if not present]
    critique = complete(
        "你是嚴格但具建設性的文案審稿人。請檢查初稿是否漏掉必填資訊、"
        "是否自行加入未提供的事實，以及讀者能否一眼看懂。"
        "請用繁體中文列出『保留』與『修改』兩段；每個修改點要具體。"
        "你只審稿，不要直接重寫公告。",
        f"原始資料：\n{facts}\n\n初稿：\n{draft}\n\n"
        f"程式逐字查核發現缺少的欄位：{missing_before or '無'}。"
        "逐字查核僅供參考；也請檢查語意與憑空添加的內容。",
        0.2,
    )
    revised = complete(
        "你是同一位文案編輯。根據審稿意見重寫公告，只輸出可直接發布的繁體中文修訂稿。"
        "必須逐字保留活動名稱、時間、地點、費用；不可捏造任何資料。",
        f"原始資料：\n{facts}\n\n初稿：\n{draft}\n\n審稿意見：\n{critique}\n\n"
        f"初稿逐字查核缺漏：{missing_before or '無'}。",
        0.3,
    )
    after = check_facts(revised, activity)
    missing_after = [label for label, present in after.items() if not present]
    final = revised
    if missing_after:
        # 模型可能改寫日期或省略費用；程式確保繳出的公告仍含原始必填資訊。
        footer = "\n\n活動資訊：\n" + "\n".join(
            f"- {label}：{activity.required_facts()[label]}" for label in missing_after
        )
        final += footer
    return ReflectionResult(
        draft=draft,
        critique=critique,
        revised=revised,
        final=final,
        before=before,
        after=check_facts(final, activity),
        repaired=tuple(missing_after),
    )


def render_check_table(result: ReflectionResult) -> str:
    rows = ["| 必填資訊 | 初稿 | 最終稿 |", "|---|:---:|:---:|"]
    for label in result.before:
        rows.append(
            f"| {label} | {'✓' if result.before[label] else '✗'} | "
            f"{'✓' if result.after[label] else '✗'} |"
        )
    note = (
        "程式補齊：" + "、".join(result.repaired) + "。"
        if result.repaired
        else "修訂稿已包含所有必填欄位。"
    )
    return "\n".join(rows) + "\n\n" + note + "\n\n逐字查核只驗證欄位字串；AI 審稿另檢查語意與多餘資訊。"
