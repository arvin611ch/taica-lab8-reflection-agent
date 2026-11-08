"""本機 Gradio 已啟動後，操作一次畫面並保存真實截圖與文字。"""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1050}, device_scale_factor=1)
    page.goto("http://127.0.0.1:7860", wait_until="networkidle")
    page.get_by_role("button", name="產生並反思公告").click()
    page.get_by_text("完成公告", exact=False).wait_for(timeout=180_000)
    page.wait_for_timeout(1000)
    page.screenshot(path=str(OUT / "gradio_chat.png"))
    page.screenshot(path=str(OUT / "gradio_full.png"), full_page=True)

    # 從瀏覽器 DOM 讀取實際的對話與各階段文字，供繳交內容核對。
    labels = ["① 初稿", "② AI 反思／審稿意見", "③ AI 修訂稿（程式補齊前）"]
    stage_text = {}
    for label in labels:
        stage_text[label] = page.get_by_label(label).input_value()
    data = {"page_text": page.locator("body").inner_text(), "stages": stage_text}
    (OUT / "gradio_result.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("已保存 Gradio 實際操作截圖與對話文字：", OUT)
    browser.close()
