import os
import re

import jieba

program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)
with open(program_dir + "/cn_stopwords.txt", encoding="utf-8") as f:
    zh_stopwords = [line.strip() for line in f]


def remove_stopwords(text):
    zh_words = jieba.cut(text, cut_all=False)
    zh_filtered_words = [
        word.strip() for word in zh_words if word not in zh_stopwords and word != " "
    ]
    filtered_words = zh_filtered_words
    return "".join(filtered_words)


def clean_string(input_str):
    # Replace multiple spaces with a single space
    res = re.sub(r"\s+", " ", input_str)
    # Remove spaces except between words
    res = re.sub(r"(?<!\w)\s+|\s+(?!\w)", "", res)
    # Replace Chinese symbols with English equivalents
    symbol_dict = {
        "，": " ",
        "。": " ",
        "！": " ",
        "？": " ",
        "；": " ",
        "：": " ",
        "“": " ",
        "”": " ",
        "‘": " ",
        "’": " ",
        "（": " ",
        "）": " ",
        "《": " ",
        "》": " ",
        "【": " ",
        "】": " ",
        "｛": " ",
        "｝": " ",
        "〔": " ",
        "〕": " ",
        "〈": " ",
        "〉": " ",
        "「": " ",
        "」": " ",
        "『": " ",
        "』": " ",
        "﹃": " ",
        "﹄": " ",
        "﹁": " ",
        "﹂": " ",
        "、": " ",
    }
    pattern = re.compile("|".join(re.escape(key) for key in symbol_dict.keys()))
    res = pattern.sub(lambda x: symbol_dict[x.group()], res)
    # Remove consecutive periods
    # res = re.sub(r'\.+', '.', res)
    pattern = re.compile(r"[,.;:!?]+$")
    res = pattern.sub("", res)
    res = re.sub(r"<.+?>", "", res)  # Remove HTML tags
    res = re.sub(r"\W{2,}", "", res)
    res = re.sub(r"(\d) +(\d)", r"\1,\2", res)
    res = res.strip()  # Remove leading/trailing spaces
    res = remove_stopwords(res)
    return res
