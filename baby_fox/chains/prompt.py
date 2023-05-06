QUERY_EXPANSION_TEMPL = """
基于以下输入，请提出更多相关问题，输出json格式，以query和related_queries为字段输出结果

Input: {query}
Output: 
"""

CONTEXT_BASED_ANSWER_TEMPL = """
相关描述: {context}
请结合以上提供的内容，准确地回答用户的问题，
问题: {query}


"""
