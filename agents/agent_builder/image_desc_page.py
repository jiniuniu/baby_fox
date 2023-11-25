import base64
import io

import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage
from PIL import Image

from server.config import env_settings


def generate_text_from_image(prompt: str, uploaded_file: io.BytesIO):
    img_base64 = base64.b64encode(uploaded_file.getbuffer()).decode("utf-8")
    chat = ChatOpenAI(
        model="gpt-4-vision-preview",
        max_tokens=1024,
        api_key=env_settings.OPENAI_API_KEY,
    )
    msg = chat.invoke(
        [
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": f"{prompt}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                    },
                ]
            )
        ]
    )
    return msg.content


def image_description_page():
    prompt = st.text_area("提示", value="帮我描述这张图片")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button(
        "图生文",
        use_container_width=True,
        disabled=(uploaded_file is None),
    ):
        content = generate_text_from_image(prompt, uploaded_file)
        st.write(content)


if __name__ == "__main__":
    image_description_page()
