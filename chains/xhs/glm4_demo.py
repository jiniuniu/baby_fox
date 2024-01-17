from langchain.output_parsers.json import parse_json_markdown
from loguru import logger
from zhipuai import ZhipuAI

from chains.xhs.data_source import get_general_keywords, get_xhs_note
from chains.xhs.prompts import CREATOR_TMPL, IDEA_TMPL
from server.config import env_settings


class XhsGLM4:
    def __init__(self):
        self.client = ZhipuAI(api_key=env_settings.GLM4_API_KEY)

    def generate_ideas(self, product_name: str, selling_points: str):
        user_query = IDEA_TMPL.format(
            product_name=product_name,
            selling_points=selling_points,
        )
        response = self.client.chat.completions.create(
            model="glm-4",
            messages=[
                {
                    "role": "user",
                    "content": user_query,
                },
            ],
            stream=True,
        )
        for chunk in response:
            yield chunk.choices[0].delta.content

    def create_note(
        self,
        topic_name,
        user_role,
        scence,
        information_channel,
        usage_experience,
        usage_effect,
        other_requirements,
        product_name,
    ):
        general_keywords = "\n".join(get_general_keywords())
        logger.info(f"general keywords: {general_keywords}")
        xhs_note = get_xhs_note(topic_name)
        title = xhs_note.get("title") or ""
        logger.info(f"title: {title}")
        content = xhs_note.get("content") or ""
        logger.info(f"content: {content}")
        case_keywords = "\n".join(xhs_note.get("case_keywords") or "")
        logger.info(f"case keywords: {case_keywords}")
        user_query = CREATOR_TMPL.format(
            user_role=user_role,
            scence=scence,
            information_channel=information_channel,
            usage_experience=usage_experience,
            usage_effect=usage_effect,
            other_requirements=other_requirements,
            general_keywords=general_keywords,
            case_keywords=case_keywords,
            title=title,
            content=content,
            product_name=product_name,
        )
        response = self.client.chat.completions.create(
            model="glm-4",
            messages=[
                {
                    "role": "user",
                    "content": user_query,
                },
            ],
            stream=True,
        )
        for chunk in response:
            yield chunk.choices[0].delta.content
