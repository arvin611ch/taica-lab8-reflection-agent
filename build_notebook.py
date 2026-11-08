"""由目前的 agent.py、app.py 組成可獨立執行的 Colab Notebook。"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code(source):
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": source.splitlines(True),
    }


cells = [
    md("""# Lab 8｜活動公告檢查官：Reflection Agent

**陽明交大 113611097 百川 江晟維**  
**方法：Reflection（自我檢查與修訂）**

## 1. 任務與設計

使用者輸入活動名稱、時間、地點、費用與補充資訊，Agent 產生一則可發布的繁體中文活動公告。它不是一次直接回答，而是走三次模型呼叫：

1. **撰稿**：寫初稿。
2. **反思**：另一段審稿 prompt 檢查遺漏、憑空添加與可讀性，提出具體修改。
3. **修訂**：把初稿與審稿意見交回模型改稿。

程式另逐字查核四個必填欄位。若修訂稿仍漏欄位，程式會把原始資訊補在公告尾端。**逐字查核只能確認字串出現，不能取代 AI 的語意審稿。**

這是我自己設計的活動公告主題與流程；本機沒有老師的 Demo07 原始檔，因此沒有直接複製其程式。
"""),
    md("""## 2. 安裝與模型設定

Colab 左側 **🔑 密鑰** 新增名稱 `Groq` 的金鑰，並開啟「筆記本存取權」。執行時不會印出金鑰。若在本機執行而沒有金鑰，程式會使用已啟動的 Ollama `qwen2.5:14b`。"""),
    code('%pip install -q "gradio==6.30.0" "aisuite[groq]==0.2.0" "groq==0.37.1"\n'),
    md("""## 3. Agent 核心程式

重點看 `run_reflection()`：`draft`、`critique`、`revised` 是三次不同的模型輸出；審稿意見確實送進第三次呼叫。`check_facts()` 顯示修訂前後的客觀欄位檢查。"""),
    code("%%writefile agent.py\n" + (ROOT / "agent.py").read_text(encoding="utf-8")),
    md("""## 4. 可重現的小測試

這裡用固定回覆模擬模型漏掉時間、修訂稿又漏掉費用。測試不用金鑰，能確認三個階段依序執行、審稿意見被帶入改稿、程式補齊缺漏。"""),
    code("%%writefile test_agent.py\n" + (ROOT / "test_agent.py").read_text(encoding="utf-8")),
    code("!python -m unittest -v test_agent.py\n"),
    md("""## 5. 實際模型測試

這格會真的呼叫三次模型，列出初稿、AI 反思、修訂稿及欄位查核。結果會依模型回覆略有不同。"""),
    code("""from agent import Activity, ChatModel, run_reflection, render_check_table
from IPython.display import display, Markdown

sample = Activity(
    "期中考後解壓桌遊夜",
    "11/15（週日）18:30–21:00",
    "圖書館 B1 討論室",
    "免費",
    "自備水杯；歡迎第一次接觸桌遊的同學。",
)
model = ChatModel()
result = run_reflection(sample, model.complete)
display(Markdown("### ① 初稿\\n" + result.draft))
display(Markdown("### ② AI 反思\\n" + result.critique))
display(Markdown("### ③ 最終公告\\n" + result.final))
display(Markdown("### ④ 程式查核\\n" + render_check_table(result)))
"""),
    md("""## 6. Gradio 展示與對話結果

點「產生並反思公告」可看到對話中的最終公告，以及可展開的初稿、反思、修訂稿。可改掉活動資料再執行，觀察 Agent 是否保留原始資訊。Colab 啟動時會產生 Gradio 分享網址（只在這次執行期間有效）。

以下是本機同一份 `app.py` 的實際操作截圖；可看見對話、欄位查核和三階段文字。完整文字亦保存在專案的 `screenshots/gradio_result.json`。

![Gradio 對話結果](https://raw.githubusercontent.com/arvin611ch/taica-lab8-reflection-agent/main/screenshots/gradio_chat.png)

![初稿、AI 反思與修訂稿](https://raw.githubusercontent.com/arvin611ch/taica-lab8-reflection-agent/main/screenshots/gradio_full.png)
"""),
    code("%%writefile app.py\n" + (ROOT / "app.py").read_text(encoding="utf-8")),
    code("from app import demo\ndemo.launch(share=True)\n"),
    md("""## 7. 改良與限制

- 審稿 prompt 被限定只能提出具體修改，改稿 prompt 明確接收審稿內容，避免把 Reflection 寫成三次彼此無關的生成。
- 最終公告附有程式逐字查核與缺漏補齊，能觀察模型有沒有落實修改。
- 逐字查核無法判斷活動資訊是否被錯誤解釋；例如日期換成等價寫法仍可能被標成缺漏。AI 審稿可補充語意判斷，但也可能看漏，因此畫面保留三階段供人工檢視。
- 若模型服務無法連線，介面顯示錯誤，不會把預設文案冒充 AI 執行結果。"""),
]
for index, cell in enumerate(cells):
    cell["id"] = f"lab8-{index:02d}"

notebook = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": []},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
path = ROOT / "lab8_reflection_activity_agent.ipynb"
path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(path)
