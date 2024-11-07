
from . import(
    config,
    db,
    utils,
    match,
    operate
)

from nonebot.plugin import PluginMetadata


__plugin_meta__ = PluginMetadata(
    name="图库管理器",
    description="一个可管理并在聊天时调用图库的Nonebot2插件",
    usage="自行阅读README",
    type="application",
    homepage="https://github.com/Zhalslar/nonebot-plugin-gallery",
    config=None,
    supported_adapters={"~onebot.v11"}
)
