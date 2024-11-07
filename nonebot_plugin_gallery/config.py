
randpic_store_dir_path: str = "randpic"

accurate_keywords: list[str] = [
"？", "乐", "6","好", "好的", "我看看", "啊？",
"富哥", "服", "怎么办", "yes", "行", "早",
"嗯？", "啊这", "可以",
]
fuzzy_keywords: list[str] = [
"帮助",  "大佬", "小黑子", "原神", "OK", "羡慕", "小黑子", "稍等", "睡觉", "晚安",
"吃饭", "厉害", "笑死", "涩涩", "难绷",
]

compress: bool = False

compression_threshold: int = 512


'''
class Config(BaseModel, extra=Extra.ignore):
    
    accurate_keywords: list[str] = [
    "？", "乐", "6","好", "好的", "我看看", "啊？",
    "富哥", "服", "怎么办", "yes", "行", "早",
    "嗯？", "啊这", "可以",
]
    fuzzy_keywords: list[str] = [
    "帮助",  "大佬", "小黑子", "原神", "OK", "羡慕", "小黑子", "稍等", "睡觉", "晚安",
    "吃饭", "厉害", "笑死", "涩涩", "难绷",
]
    compress: bool = False
    compression_threshold: int = 512

'''



#config = get_driver().config
