import hashlib
import io
import os
import aiofiles
import re

from PIL import Image
from httpx import AsyncClient
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, Event, Message,MessageSegment

from .config import compression_threshold, compress
from .db import randpic_path, DBConnectionManager
from .utils import resize_image

add = on_command("添加", priority=1, block=True)


@add.handle()
async def handle_add_command(state: T_State, event: Event, args: Message = CommandArg()):
    # 提取图库名和标签
    args_text = args.extract_plain_text().strip()
    match = re.match(r'^(\S+)\s+(\S+)$', args_text)
    if not match:
        await add.finish("添加图库名 标签")

    # 图库名和标签
    gallery_name, label = match.groups()

    # 将图库名和标签存入状态，以便后续使用
    state["gallery_name"] = gallery_name
    state["label"] = label




@add.got('image', prompt='请发送图片~')
async def _(state: T_State, bot: Bot, event: Event):
    await handle_image_message(state, bot, event)

async def handle_image_message(state: T_State, bot: Bot, event: Event):
    message = event.get_message()
    # 检查消息中的每个段，如果有一个是图片则处理
    for segment in message:
        if segment.type == 'image':
            await add_pic(state, segment)
            return
    # 如果没有找到图片，可以给用户提示
    await bot.send(event, "请发送一张图片。")

async def add_pic(state: T_State, pic_segment: MessageSegment):
    # 从状态中读取图库名和标签
    gallery_name = state["gallery_name"]
    label = state["label"]
    print(gallery_name,label)

    # 设置图库路径并确保存在
    command_path = randpic_path / gallery_name
    command_path.mkdir(parents=True, exist_ok=True)

    connection = await DBConnectionManager.get_connection(randpic_path)
    # 获取当前图片数量以便命名
    randpic_cur_picnum = len(os.listdir(command_path))

    # 确认消息包含图片
    pic_name = pic_segment
    if pic_name.type != 'image':
        await add.send(MessageSegment.face(289))
        return

    # 获取图片 URL
    pic_url = pic_name.data['url']

    # 下载图片
    async with AsyncClient() as client:
        try:
            resp = await client.get(pic_url, timeout=5.0)
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f"下载图片失败: {e}")
            await add.send(MessageSegment.text('\n这张保存不了喵~'))
            return

    # 计算图片哈希值
    data = resp.content
    fmd5 = hashlib.md5(data).hexdigest()

    # 检查图片是否已存在
    async with connection.cursor() as cursor:
        await cursor.execute(f'SELECT img_url FROM Pic_of_{gallery_name} WHERE md5=?', (fmd5,))
        if await cursor.fetchone():
            await add.send(Message("\n这张图库里已经有啦！"), at_sender=True)
            return

    # 图片过大时是否压缩
    if compress:
        data = resize_image(Image.open(io.BytesIO(data)), compression_threshold)

    # 构建文件路径和文件名
    _, extension = os.path.splitext(pic_url)
    file_name = f"{gallery_name}_{randpic_cur_picnum + 1}_{label}{extension or '.jpg'}"
    file_path = command_path / file_name

    # 保存图片文件并更新数据库
    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)

        async with connection.cursor() as cursor:
            await cursor.execute(
                f'INSERT INTO Pic_of_{gallery_name}(md5, img_url) VALUES (?, ?)',
                (fmd5, str(file_path))
            )
        await connection.commit()

        # 提示添加成功
        await add.send(pic_name + Message(f"添加好啦~"), at_sender=True)
    except Exception as e:
        logger.warning(f"添加图片失败: {e}")
        await add.send(Message("\n添加失败！"), at_sender=True)
