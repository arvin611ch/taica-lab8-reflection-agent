"""Gradio 介面；可本機執行，也可在 Colab 最後一格啟動。"""

import gradio as gr

from agent import Activity, ChatModel, render_check_table, run_reflection


def respond(title, when, where, fee, notes, history):
    history = list(history or [])
    try:
        activity = Activity(title, when, where, fee, notes)
        model = ChatModel()
        result = run_reflection(activity, model.complete)
    except (ValueError, RuntimeError) as exc:
        return history, "", "", "", f"⚠️ {exc}"

    summary = f"{title}｜{when}｜{where}｜{fee}"
    history.append({"role": "user", "content": summary})
    history.append(
        {
            "role": "assistant",
            "content": f"### 完成公告\n{result.final}\n\n"
            f"_已執行：初稿 → AI 反思 → 修訂；模型：{model.backend}／{model.model}_",
        }
    )
    return history, result.draft, result.critique, result.revised, render_check_table(result)


with gr.Blocks(title="活動公告檢查官｜Reflection Agent") as demo:
    gr.Markdown(
        "# 活動公告檢查官 ✍️\n"
        "**Reflection Agent**：撰稿 AI → 審稿 AI → 改稿 AI。"
        "下方會公開三個階段與欄位查核，方便觀察修訂是否真的有幫助。"
    )
    with gr.Row():
        with gr.Column(scale=1):
            title = gr.Textbox(label="活動名稱（必填）", value="期中考後解壓桌遊夜")
            when = gr.Textbox(label="時間（必填）", value="11/15（週日）18:30–21:00")
            where = gr.Textbox(label="地點（必填）", value="圖書館 B1 討論室")
            fee = gr.Textbox(label="費用（必填）", value="免費")
            notes = gr.Textbox(
                label="補充資訊（選填）",
                value="自備水杯；歡迎第一次接觸桌遊的同學。",
                lines=3,
            )
            run_button = gr.Button("產生並反思公告", variant="primary")
            gr.Markdown("Colab：左側 🔑 新增 `Groq` 金鑰並開啟筆記本存取權。")
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Gradio 對話結果", height=400)
            checks = gr.Markdown(label="必填資訊查核")
    with gr.Accordion("查看 Agent 的三個階段", open=True):
        draft_box = gr.Textbox(label="① 初稿", lines=6, interactive=False)
        critique_box = gr.Textbox(label="② AI 反思／審稿意見", lines=8, interactive=False)
        revised_box = gr.Textbox(label="③ AI 修訂稿（程式補齊前）", lines=6, interactive=False)
    run_button.click(
        respond,
        inputs=[title, when, where, fee, notes, chatbot],
        outputs=[chatbot, draft_box, critique_box, revised_box, checks],
    )
    gr.ClearButton([chatbot, draft_box, critique_box, revised_box, checks])


if __name__ == "__main__":
    demo.launch(share=False)
