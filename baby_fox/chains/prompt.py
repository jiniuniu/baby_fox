QUERY_EXPANSION_TEMPL = """
基于以下输入，请提出更多相关问题，输出json格式，以query和related_queries为字段输出结果
如果输入的是一个事件名称，相关问题中需要包含描述的是什么事件
Input: {query}
Output: 
"""

CONTEXT_BASED_ANSWER_TEMPL = """
相关描述: {context}
请严格基于上面的内容回答问题，字数在200字以内。
问题: {query}


"""


PARAGRPAPH_TEMPL = """
相关材料：
{materials}
相关问题：
{outlines}

请结合上面提供的相关材料，写一篇文章，文章需要结合所罗列的相关问题，最后对文章写一个总结。
"""
