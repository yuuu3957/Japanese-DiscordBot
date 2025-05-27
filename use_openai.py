#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
import openai
import gradio as gr

openai.api_key = "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"

def jp_to_zh(word):
    prompt = f"""pi
    請用繁體中文解釋日文單字「{word}」的意思，並提供兩個常見例句（包含中文翻譯）。
    格式：
    解釋：
    例句1：日文句子
    中文翻譯1：
    例句2：日文句子
    中文翻譯2：
    """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

iface = gr.Interface(
    fn=jp_to_zh,
    inputs=gr.Textbox(label="請輸入日文單字"),
    outputs=gr.Textbox(label="中文解釋與例句"),
    title="日文單字翻譯小助手",
    description="輸入日文單字，即時獲得中文解釋與例句。"
)

iface.launch()