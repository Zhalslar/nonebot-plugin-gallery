from pydantic import BaseModel, Extra
from nonebot import get_driver, get_plugin_config

class Config(BaseModel, extra=Extra.ignore):
    randpic_store_dir_path: str
    accurate_keywords: list[str]
    fuzzy_keywords: list[str]
    compress: bool = False
    compression_threshold: int = 512


config = get_driver().config
