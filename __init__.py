

from . import(
    add_picture,
    exact_match,
    fuzzy_match,
    config,
    db,
    utils,
    del_picture,
    view_gallery
)

from nonebot.plugin import PluginMetadata
from .config import randpic_store_dir_path


__plugin_meta__ = PluginMetadata(
    name="图库系统",
    description="Nonebot2 图库系统 图片",
    usage="使用 /help 查看帮助信息。",
    type="application",
    homepage="https://github.com/yourusername/my-plugin",
    config=None,
    extra={
        "author": "Zhalslar",
        "version": "1.0.0",
        "license": "MIT",
    }
)

__usage__ = "None"