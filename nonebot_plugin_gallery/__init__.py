from pathlib import Path
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot import get_driver, logger, on_command
from .config import config
from . import add, matcher, view, delete
from .utils import send_f, init_json_file, read_json, write_json, create_subfolders

__plugin_meta__ = PluginMetadata(
    name="图库管理器",
    description="给bot提供强大的图库管理功能",
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


driver = get_driver()
@driver.on_startup
async def _():
    logger.info("图库插件正在初始化...")
    initialize(config.all_gallery_path, config.keywords_path)
    logger.info("初始化完成，欢迎使用插件！")



def initialize(root_folder, json_file, key_a ="accurate_keywords", key_f="fuzzy_keywords"):
    """
    同步：文件夹、json文件、精准匹配列表、模糊匹配列表
    ps：初始化的核心算法，关键在于集合运算
    """
    # 确保总文件夹存在
    Path(root_folder).mkdir(parents=True, exist_ok=True)

    # 初始化JSON文件，确保键存在
    init_json_file(json_file, [key_a, key_f])

    # 读取JSON文件
    data = read_json(json_file)

    # 获取总文件夹下所有子文件夹的名称
    total_subfolders = {d.name for d in Path(root_folder).iterdir() if d.is_dir()}

    # 获取m,j并转换为集合
    a_set = set(data.get(key_a, []))
    f_set = set(data.get(key_f, []))

    # 进行集合运算
    new_f_set = f_set - a_set
    new_d_set = total_subfolders.union(new_f_set).union(a_set)
    new_a_set = new_d_set - new_f_set

    # 将集合转换回列表
    new_a = sorted(list(new_a_set))
    new_d = sorted(list(new_d_set))
    new_f = sorted(list(new_f_set))

    # 更新JSON文件
    data[key_a] = new_a
    data[key_f] = new_f
    write_json(json_file, data)

    # 更新子文件夹名称
    create_subfolders(root_folder, new_d)

    #更新精确匹配列表、模糊匹配列表
    config.accurate_keywords = new_a
    config.fuzzy_keywords = new_f



overloads = on_command('重载图库',permission=SUPERUSER, priority=1, block=True)
@overloads.handle()
async def overloads_gallery():
    try:
        initialize(config.all_gallery_path, config.keywords_path)
        await overloads.send("图库重载完成")
        logger.info("图库重载完成")
    except Exception as e:
        await overloads.send(f"图库重载失败")
        logger.error(f"图库重载失败：{str(e)}")



gallery_help = on_command('图库帮助', priority=5, block=True)

@gallery_help.handle()
async def _(bot,event):
    """图库帮助"""
    r = "图库帮助(指令示例:)：\n" \
        "【cat】从cat图库随机抽图\n" \
        "【添加】添图到自己的图库\n" \
        "【添加@Ta】添图到Ta的图库\n" \
        "【添加cat】添图到图库里\n" \
        "【添加cat f】模糊匹配添加\n" \
        "【添加cat n】添图时不压缩\n" \
        "\n" \
        "【查看】查看自己的图库\n" \
        "【查看3】查看你的3号图\n" \
        "【查看@Ta】查看Ta的图库\n" \
        "【查看all】查看所有图库\n" \
        "【查看cat】查看cat图库\n" \
        "【查看cat 3】查看cat的3号图\n" \
        "\n" \
        "【删除4】删除你的4号图\n" \
        "【删除cat】删除cat图库\n" \
        "【删除cat 5】删除cat的5号图\n" \
        "\n" \
        "【偷图】引用图片，发送偷图"
    await send_f(bot,event,r,1)





