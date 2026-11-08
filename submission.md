# 繳交文字（貼到課程平台）

**繳交標題：** 陽明交大 113611097 百川 江晟維 活動公告檢查官（Reflection Agent）

**Colab 連結（公開 GitHub Notebook，任何有連結者可開啟）：**  
https://colab.research.google.com/github/arvin611ch/taica-lab8-reflection-agent/blob/0318e99c43186a7c32767a85810111263508d8c8/lab8_reflection_activity_agent.ipynb

**Agent 任務與類型：** 這是 Reflection Agent。使用者輸入活動名稱、時間、地點、費用和補充資訊，AI 協助寫出可發布的繁體中文活動公告。

**如何運作：** 程式呼叫模型三次：① 撰稿產生初稿；② 審稿 AI 依原始資料指出缺漏、憑空添加與可讀性問題；③ 改稿 AI 接收初稿和審稿意見後重新寫公告。程式再逐字查核四個必填欄位，必要時把缺漏的原始值補進最終稿。Notebook 的 §3 是 Agent 核心、§4 是固定回覆測試、§5 是實際模型結果、§6 是 Gradio 對話介面。

**重點截圖：**

- [Gradio 對話與查核表](https://raw.githubusercontent.com/arvin611ch/taica-lab8-reflection-agent/main/screenshots/gradio_chat.png)
- [完整畫面：初稿 → AI 反思 → 修訂稿](https://raw.githubusercontent.com/arvin611ch/taica-lab8-reflection-agent/main/screenshots/gradio_full.png)

**Gradio 對話結果：** 範例輸入「期中考後解壓桌遊夜／11/15（週日）18:30–21:00／圖書館 B1 討論室／免費」。實際執行後，畫面同時顯示初稿、審稿意見與完成公告；初稿把時間和地點改成不同寫法，審稿要求統一格式，修訂稿逐字保留原始值，四個必填欄位全部通過查核。完整文字另存於 [gradio_result.json](https://github.com/arvin611ch/taica-lab8-reflection-agent/blob/main/screenshots/gradio_result.json)。

**改良與測試：** 固定回覆測試刻意讓初稿漏時間、修訂稿漏費用，確認三階段流程與缺漏補齊都正常；本機實際模型與 Gradio 操作也已驗證。逐字查核無法驗證語意真偽，因此保留全部階段讓使用者人工檢視。
