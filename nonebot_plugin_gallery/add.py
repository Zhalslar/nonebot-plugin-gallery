import os
from pathlib import Path
from nonebot import on_command, Bot
from nonebot.params import CommandArg
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Event, Message, MessageEvent
from .config import config
from .utils import (
    download_image,
    update_element_in_json,
    get_user_label,
    compress_image,
    check_duplicate_image,
    get_at_label, fix_image_extension, get_reply_label
)

add = on_command("添加", priority=10, block=True)


@add.handle()
async def handle_add_command(state: T_State, bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    """指令管理器"""
    parts: list = args.extract_plain_text().strip().split()
    at_label = await get_at_label(bot,event)
    user_label = await get_user_label(bot,event)
    # 添加到自己的图库
    if not parts and not at_label:
        gallery_name = user_label
        mode = config.default_mode
        compress_switch = config.default_compress_switch
    # 添加到被@者的图库
    elif not parts and at_label:
        gallery_name = at_label
        mode = config.default_mode
        compress_switch = config.default_compress_switch
    else:
        gallery_name = parts[0]
        # 模糊匹配添加
        if len(parts) > 1 and 'f' in parts:
            mode = 'f'
        else:
            mode = config.default_mode
        # 添加时不压缩
        if len(parts) > 1 and 'n' in parts:
            compress_switch = False
        else:
            compress_switch = config.default_compress_switch
    state["gallery_name"] = gallery_name
    state["label"] = user_label
    state["mode"] = mode
    state["compress_switch"] = compress_switch
    logger.info(f"图库名：{gallery_name},标签：{user_label}，模式：{mode},压缩开关:{compress_switch}")


@add.got('image', prompt='请发送图片~')
async def _(state: T_State, event: Event):
    gallery_name = state["gallery_name"]
    label = state["label"]
    mode = state["mode"]
    compress_switch = state["compress_switch"]

    for segment in event.get_message():
        if segment.type != 'image':
            await add.finish("你别添加了")
        else:
            pic_url = segment.data['url']
            await picture_main_handle(pic_url, gallery_name, label, compress_switch,mode)


steal = on_command("偷图", aliases={"这图我要了", "偷你图"}, priority=5, block=True)

@steal.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    parts: list = args.extract_plain_text().strip().split()
    user_label = await get_user_label(bot,event)
    reply_label = await get_reply_label(bot, event)
    if event.reply:
        original_message = event.reply.message
        pic_urls = [seg.data["url"] for seg in original_message if seg.type == "image"]
        if pic_urls:
            pic_url = pic_urls[0]
            compress_switch = config.default_compress_switch
            mode = config.default_mode
            if "n" in parts: compress_switch = False
            if "f" in parts: mode = "f"
            await picture_main_handle(pic_url, user_label, reply_label, compress_switch, mode)
        else:
            await bot.send(event, "哪有图嘛？")


async def picture_main_handle(pic_url, gallery_name: str = "垃圾桶", label: str = "无名",
                              compress_switch: bool = config.default_compress_switch,
                              mode:str = config.default_mode,
                              ):
    """处理图片下载事件的主函数"""

    gallery_path = config.all_gallery_path / gallery_name
    gallery_path.mkdir(parents=True, exist_ok=True)

    # 初步获取拓展名
    extension = Path(pic_url).suffix
    if not extension or not extension.startswith('.'):
        extension = ".jpg"

    # 根据编号生成不重复的图片名
    picture_name = generate_unique_filename(gallery_path, gallery_name, label, extension)

    # 下载图片
    await download_image(pic_url, gallery_path, picture_name)

    # 更正拓展名
    picture_path = gallery_path / picture_name
    picture_name = fix_image_extension(picture_path)
    picture_path = gallery_path / picture_name

    # 是否压缩
    if compress_switch:
        try:
            compress_image(picture_path, config.compress_size)
        except Exception as e:
            logger.error(f"压缩图片失败：{str(e)}")

    # 是否排除重复图片
    if config.duplicate_switch:
        if check_duplicate_image(gallery_path, picture_path):
            os.remove(picture_path)
            await add.finish(f"【{gallery_name}】图库已经有这图了")

    # 关键： 如果是新图库：根据匹配模式将 新增图库名 保存到json文件中，同时更新关键词列表 ，二者同步，确保图库的热重载性
    if gallery_name not in config.fuzzy_keywords and gallery_name not in config.accurate_keywords:
        if mode == 'f':
            config.fuzzy_keywords.append(gallery_name)
            update_element_in_json(config.keywords_path, "fuzzy_keywords", gallery_name)
            logger.info(f"新增模糊匹配关键词：{gallery_name}")

        elif mode == 'a':
            config.accurate_keywords.append(gallery_name)
            update_element_in_json(config.keywords_path, "accurate_keywords", gallery_name)
            logger.info(f"新增精准匹配关键词：{gallery_name}")

    await add.send(f"【{gallery_name}】新增图片：\n{picture_name}")


def generate_unique_filename(gallery_path, gallery_name: str, label: str, extension: str = ".jpg") -> str:
    """
    生成唯一的图片文件名，格式为 {gallery_name}_{pic_num}_{label}{extension}。
    编号唯一性由 {pic_num} 保证, 并且取用最小的可用编号
    """
    existing_numbers = set()
    for file in gallery_path.iterdir():
        if file.is_file():
            parts = file.stem.split('_')
            if len(parts) >= 2 and parts[0] == gallery_name and parts[1].isdigit():
                existing_numbers.add(int(parts[1]))
    pic_num = 1
    while pic_num in existing_numbers:
        pic_num += 1
    return f"{gallery_name}_{pic_num}_{label}{extension}"




