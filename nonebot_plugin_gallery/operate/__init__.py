

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
    name="图库管理器",
    description="一个可管理并在聊天时调用图库的Nonebot2插件",
    usage="自行阅读README",
    type="application",
    homepage="https://github.com/Zhalslar/nonebot-plugin-gallery",
    config=None,
    extra={
        "author": "Zhalslar",
        "version": "1.0.0",
        "license": "MIT",
    }
)

__usage__ = "None"