# TAICA Lab 8｜活動公告檢查官（Reflection Agent）

陽明交大 113611097 百川 江晟維

**Colab：** https://colab.research.google.com/github/arvin611ch/taica-lab8-reflection-agent/blob/main/lab8_reflection_activity_agent.ipynb

## 作品內容

輸入一場活動的名稱、時間、地點、費用與補充資訊，Agent 會寫一則繁體中文公告。核心是 **Reflection**：先產生初稿，再讓 AI 以審稿者身分找缺漏和自行添加的事實，最後把審稿意見交回 AI 改稿。Gradio 同時顯示初稿、反思、修訂稿和最終公告。

程式另外逐字查核四個必填欄位。若修訂稿漏掉欄位，會把原始值補在最終公告尾端；畫面也會標示這個動作。這使 AI 審稿與可重現的程式查核各自有明確用途。

## 執行

### Colab

1. 開啟上方 Colab 連結。
2. 左側 **🔑 密鑰** 新增 `Groq`，填入自己的 Groq API 金鑰，並開啟「筆記本存取權」。
3. 執行所有程式格；最後一格開啟 Gradio 網頁。

金鑰不會寫進 Notebook。Notebook 已包含 `agent.py` 與 `app.py` 的完整內容，不需要額外下載本專案檔案。Groq 的 [Chat Completions API](https://console.groq.com/docs/api-reference) 和模型 `openai/gpt-oss-120b` 均列於 [官方文件](https://console.groq.com/docs/models)。

### 本機

需要 Python 3.10+。如已安裝 Ollama 與 `qwen2.5:14b`，不用雲端金鑰：

```bash
python -m venv .venv
.venv/bin/pip install "gradio==6.30.0"
.venv/bin/python app.py
```

也可設定 `GROQ_API_KEY` 使用 Groq。模型可用 `LAB8_MODEL` 改成同一供應商支援的其他名稱。

## 驗證與截圖

```bash
python -m unittest -v test_agent.py
```

測試涵蓋三次模型呼叫的順序、審稿意見送進改稿，以及模型漏掉必填欄位時的補齊。另以本機 Ollama `qwen2.5:14b` 實際跑過一次 Gradio：初稿把時間與地點改成不同寫法；審稿要求統一格式，修訂稿逐字保留原始值，最終稿四個必填欄位皆通過查核。結果可見 [Gradio 截圖](screenshots/gradio_chat.png)、[完整畫面](screenshots/gradio_full.png) 與 [對話文字](screenshots/gradio_result.json)。

## 檔案

| 檔案 | 用途 |
|---|---|
| `lab8_reflection_activity_agent.ipynb` | 可獨立執行的 Colab 作業本體，重點以 Markdown 標出 |
| `agent.py` | 模型呼叫與 Reflection 核心 |
| `app.py` | Gradio 展示介面 |
| `test_agent.py` | 固定回覆測試 |
| `build_notebook.py` | 從程式檔更新 Notebook，避免兩份程式不同步 |
| `capture_demo.py` | 本機操作 Gradio 並產生截圖的輔助腳本 |
| `submission.md` | 課程平台可貼的繳交文字 |

**限制：** 逐字查核只能檢查原始字串是否出現，不能證明公告完全沒有錯誤。最終稿仍需人工確認。這個限制在 Notebook 與 Gradio 畫面中都有說明。
