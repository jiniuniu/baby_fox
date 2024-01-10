from langchain.prompts import PromptTemplate

IDEA_TMPL = """
你好，请生成5个能通过{product_name}结合其卖点{selling_points}能解决的不同的痛点。
基于痛点分别拓展出不同的人设和具体的场景，这个人设在该场景下能用{product_name}解决痛点并有具体的效果。

回复内容口语化。
人设需给明年龄和身份，不需要给明姓名。

用JSON格式输出结果，每行的第一个词作为主键，需要包含下面的信息
problem_to_solve，（产品的卖点功效，所解决的痛点）
user_role，（人设，提及年龄，职业身份，和产品卖点相关的自身痛点，如：35岁的摄影师，肤质偏干），
scence，（场景，需要暴露用户痛点），
information_channel，（信息渠道，一个详细路径即可，如何得知产品），
usage_experienece，（使用感受，有细节的表达，且表达注重普通人感受），
usage_effect，（使用效果，周期可长可短），
other_requirements，(其他要求，解决这些痛点的其他方向的干货1个，比如肤色的问题除了使用美白精华也可以通过“内服食谱”来解决该痛点)


输出样例
```json
[
    {{
        "problem_to_solve": "解决色斑问题",
        "user_role": "25岁的办公室白领，肤质偏干",
        "scence": "夏天到了，穿上短袖裙子，发现手臂和脸上的色斑特别明显",
        "information_channel": "在社交媒体上看到网红推荐",
        "usage_experienece": "产品质地清爽，不油腻，使用后肌肤有明显的滋润感，同时不会引起过敏或刺痛感",
        "usage_effect": "连续使用1个月后，色斑明显淡化，肤色也变得更加均匀",
        "other_requirements": "除了使用淡斑产品外，可以多做美白面膜来加速美白效果；如果通过内服食谱来解决色斑问题，可以起名为“美白果汁”，比如以柠檬、蜂蜜和白木耳为主要原料制作美白果汁"
    }},
    {{
        "problem_to_solve": "解决雀斑问题",
        "user_role": "28岁的全职妈妈，肤质较油",
        "scence": "带孩子出门玩耍时，发现阳光下自己脸上的雀斑非常明显",
        "information_channel": "在电视购物节目中看到该产品推荐",
        "usage_experienece": "产品质地清爽，不会造成肌肤油腻感，使用后肌肤有一定的紧致感，同时没有刺激性气味",
        "usage_effect": "连续使用2个月后，雀斑明显减淡，肤色也变得更加均匀",
        "other_requirements": "除了使用淡斑产品外，可以多做防晒工作来避免雀斑加深；如果通过内服食谱来解决雀斑问题，可以起名为“美白果昔”，比如以西红柿、胡萝卜和蜂蜜为主要原料制作美白果昔"
    }}
]
```
"""


IDEA_PROMPT = PromptTemplate(
    input_variables=[
        "product_name",
        "selling_points",
    ],
    template=IDEA_TMPL,
)


CREATOR_TMPL = """
# Goal

你是一个{user_role}。{scence}。撰写一篇小红书笔记。

大致框架
1. {information_channel}{usage_experience}{usage_effect}
2. {other_requirements}

## Constraints
- 全文前后始终表达一个话题，前后逻辑畅通，通篇口语化表达；
- 身份信息不需要特地用“我是***”来表达，可以从场景描述中了解即可；
- 需要展开描述其他的解决方案；
- 从【Goal】的人设和使用场景出发，口语化表达，分享真实感受；
- 以真实分享干货为主，不要任何纰漏成分的表达；
- 不要使用“刷酸”、“刷酸治疗”等明示或暗示医疗作用和效果的词语；
- 结尾不需要任何的【总结】【呼吁】【推荐安利】；

## Tone 
-【口语化】【用词简单直接】；
-【细节化】【生活化场景】的描绘和叙述；
- 禁止使用任何【比喻】、【拟人】；
- 在符合逻辑的情况下，尽量使用【Recommended Words】的表达；

## Recommended Expression
{general_keywords}

## Recommended Word
{case_keywords}

## 仅参考文章结构，里面提到的产品不可参考

标题：{title}
正文：{content}

## OUTPUT(说人话)（在文章的中间部分提{product_name}）

"""


CREATOR_PROMPT = PromptTemplate(
    input_variables=[
        "user_role",
        "scence",
        "information_channel",
        "usage_experience",
        "usage_effect",
        "other_requirements",
        "general_keywords",
        "case_keywords",
        "title",
        "content",
        "product_name",
    ],
    template=CREATOR_TMPL,
)
