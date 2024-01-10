from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from loguru import logger

from chains.xhs.prompts import CREATOR_PROMPT, IDEA_PROMPT
from server.config import env_settings


def build_xhs_chain_by_type(chain_type: str, callbacks=None) -> LLMChain:
    # "gpt-4-1106-preview"
    # "gpt-3.5-turbo-1106"
    llm = ChatOpenAI(
        api_key=env_settings.OPENAI_API_KEY,
        model_name="gpt-4-1106-preview",
        streaming=True,
        callbacks=callbacks,
    )
    if chain_type == "xhs_ideas":
        return LLMChain(prompt=IDEA_PROMPT, llm=llm)
    elif chain_type == "xhs_note_creator":
        return LLMChain(prompt=CREATOR_PROMPT, llm=llm)


if __name__ == "__main__":
    from chains.xhs.data_source import get_general_keywords, get_xhs_note

    # idea_generator = build_xhs_chain_by_type("xhs_ideas")
    # inp = {
    #     "product_name": "Olay淡斑小白瓶",
    #     "selling_points": "美白、淡斑、抗老",
    # }
    # res = idea_generator(inp)["text"]
    # logger.info(res)
    creator = build_xhs_chain_by_type("xhs_note_creator")
    user_role = "26岁的研究生，长期熬夜导致皮肤出现痘痘和痘印"
    scence = "毕业季要拍毕业照，但是脸上的痘印让人没有自信"
    info_channel = "在学校BBS论坛上看到学长学姐推荐Olay淡斑小白瓶"
    usage_experience = "使用过程中感觉温和不刺激，痘印部位无负担"
    usage_effect = "坚持使用六周，痘印明显变淡，脸部肌肤更加平滑"
    other_requirements = "针对痘印，建议调整作息，保证充足睡眠，并且饮食清淡，避免油腻食物"
    general_keywords = "\n".join(get_general_keywords())
    note_data = get_xhs_note("抗老精华")
    case_keywords = "\n".join(note_data.get("case_keywords"))
    title = note_data.get("title")
    content = note_data.get("content")
    product_name = "Olay淡斑小白瓶"
    inp = {
        "user_role": user_role,
        "scence": scence,
        "information_channel": info_channel,
        "usage_experience": usage_experience,
        "usage_effect": usage_effect,
        "other_requirements": other_requirements,
        "general_keywords": general_keywords,
        "case_keywords": case_keywords,
        "title": title,
        "content": content,
        "product_name": product_name,
    }
    res = creator(inp)["text"]
    logger.info(res)
