import textwrap

def split_sentences(text):
    """
    根据中文标点符号断句。
    """
    sentences = []
    sentence = ""
    for char in text:
        sentence += char
        if char in "，。？！；、":
            sentences.append(sentence)
            sentence = ""
    if sentence:  # 添加最后一个句子（如果有）
        sentences.append(sentence)
    return sentences

def format_poem_for_display(poem, max_width):
    """
    格式化诗歌文本以适应显示宽度，先断句再检查宽度。
    
    :param poem: 原始诗歌文本。
    :param max_width: 墨水屏的最大字符宽度（以像素为单位）。
    :return: 格式化后的诗歌文本。
    """
    formatted_poem = []
    sentences = split_sentences(poem)
    
    for sentence in sentences:
        # 计算当前字体大小下，句子的大致宽度（这里需要根据实际使用的字体调整宽度计算方式）
        # 假设每个中文字符的宽度约为font_width
        font_width = 20  # 假定每个字符的平均宽度（需要根据实际字体调整）
        sentence_width = len(sentence) * font_width
        
        if sentence_width > max_width:
            # 如果句子宽度超过最大宽度，进行换行处理
            wrapped = textwrap.wrap(sentence, width=max_width // font_width)
            formatted_poem.extend(wrapped)
        else:
            formatted_poem.append(sentence)
    
    return "\n".join(formatted_poem)

# 示例诗歌文本
#poem_text = "黄菊枝头生晓寒。人生莫放酒杯干。风前横笛斜吹雨，醉里簪花倒著冠。身健在，且加餐。舞裙歌板尽清欢。黄花白发相牵挽，付与时人冷眼看。"

# # 格式化文本
# formatted_poem = format_poem_for_display(poem['title'], 360)  # 假设墨水屏最大宽度为360像素
# print(formatted_poem)
# formatted_poem = format_poem_for_display(poem['dynasty'], 360)  # 假设墨水屏最大宽度为360像素
# print(formatted_poem)
# formatted_poem = format_poem_for_display(poem['author'], 360)  # 假设墨水屏最大宽度为360像素
# print(formatted_poem)
# formatted_poem = format_poem_for_display(poem['full_content'], 360)  # 假设墨水屏最大宽度为360像素
# print(formatted_poem)
