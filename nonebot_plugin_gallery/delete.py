from nonebot import on_command, get_driver, Bot
from nonebot.adapters.onebot.v11 import Message, Event
from nonebot.params import CommandArg
from .utils import get_user_label, delete_path, update_element_in_json
from .config import config

SUPERUSERS = get_driver().config.superusers

delete = on_command("删除", priority=10, block=True)

@delete.handle()
async def _delete_handler(bot:Bot, event:Event, args: Message = CommandArg()):
    parts: list = args.extract_plain_text().strip().split()
    user_label = await get_user_label(bot,event)
    use_id =  event.get_user_id()

    if not parts:
        await delete.finish("主人想删除什么？")

    if len(parts) == 1 and parts[0].isdigit():
        number = int(parts[0])
        await delete_image(user_label, number, user_label,use_id)
        return

    if len(parts) == 1:
        gallery_name = parts[0]
        if gallery_name == user_label or use_id in SUPERUSERS:
            await delete_gallery(gallery_name)
            return
        else:
            await delete.finish(f"只能删除自己的图库【{user_label}】")

    if len(parts) == 2 and parts[1].isdigit():
        gallery_name, number = parts[0], parts[1]
        await delete_image(gallery_name, int(number), user_label,use_id)
    else:
        await delete.finish("指令格式错误")



async def delete_gallery(gallery_name):
    gallery_path = config.all_gallery_path / gallery_name

    if not gallery_path.exists():
        await delete.finish(f"图库【{gallery_name}】不存在")
    # 关键： 删除图库文件夹时，同时删除 json文件中的对应关键词 和 关键词列表中的对应关键词, 二者同步，确保图库的热重载性
    await delete_path(gallery_path)
    if gallery_name in config.accurate_keywords:
        config.accurate_keywords.remove(gallery_name)
        update_element_in_json(config.keywords_path, "accurate_keywords", gallery_name, True)
    if gallery_name in config.fuzzy_keywords:
        config.fuzzy_keywords.remove(gallery_name)
        update_element_in_json(config.keywords_path, "fuzzy_keywords", gallery_name, True)
    await delete.finish(f"已删除【{gallery_name}】图库")


async def delete_image(gallery_name: str, number: int, user_label: str,use_id: str):
    """删除gallery_name图库下编号为number的图片,普通用户只能删自己的图，超级用户无限制"""
    gallery_path = config.all_gallery_path / gallery_name
    files = list(gallery_path.iterdir()) if gallery_path.exists() else []
    target_file_path = None
    for file_path in files:
        file_name = file_path.name
        if file_name.startswith(f"{gallery_name}_{number}_"):
            target_file_path = gallery_path / file_name
            break
    if target_file_path and target_file_path.exists():
        if user_label in target_file_path.name:
            if use_id in SUPERUSERS or user_label in target_file_path.name:
                await delete_path(target_file_path)
                await delete.finish(f"已删除图片: {target_file_path.name}")
            else:
                await delete.finish("删除图片时出错")
        else:
            await delete.finish("不是你的图片不能删除")
    else:
        await delete.finish(f"未找到编号为{number}的图片")

