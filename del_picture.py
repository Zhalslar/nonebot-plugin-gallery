import hashlib
import os

from httpx import AsyncClient

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.params import Arg, Fullmatch
from nonebot.log import logger
from .db import randpic_command_del_tuple, randpic_path, DBConnectionManager

delete = on_fullmatch(randpic_command_del_tuple, priority=2, block=True)

@delete.got("pic", prompt="发一下要删除的图片喵~")
async def delete_pic(args: str = Fullmatch(), pic_list: Message = Arg('pic')):

    connection = await DBConnectionManager.get_connection(randpic_path)

    gallery_name = args.replace('删除', '').strip()

    # 检查是否为图片类型
    pic_name = pic_list[0]
    if pic_name.type != 'image':
        await delete.send(MessageSegment.face(289))
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
            await delete.send(pic_name + MessageSegment.text('\n下载不了这张图喵~'))
            return

    # 计算图片哈希值
    fmd5 = hashlib.md5(resp.content).hexdigest()

    # 检查图片是否存在于数据库中
    async with connection.cursor() as cursor:
        await cursor.execute(f'SELECT img_url FROM Pic_of_{gallery_name} WHERE md5=?', (fmd5,))
        row = await cursor.fetchone()
        if not row:
            await delete.send(pic_name + Message(f"\n{gallery_name}图库没这张图哎~"), at_sender=True)
            return

        # 获取图片路径并尝试删除文件
        file_path = (randpic_path / row[0]).resolve()

        if file_path.exists():
            try:
                os.remove(str(file_path))
            except OSError as e:
                logger.warning(f"删除文件失败: {e}")
                await delete.send(pic_name + Message("\n删不了"), at_sender=True)
        else:
            logger.warning(f"文件路径不存在: {file_path}")
            await delete.send(pic_name + Message("\n文件路径不存在"), at_sender=True)

        # 从数据库中删除记录
        await cursor.execute(f'DELETE FROM Pic_of_{gallery_name} WHERE md5=?', (fmd5,))
        await connection.commit()

        # 提示删除成功
        await delete.send(pic_name + Message("\n好嘟，删除了"), at_sender=True)
