
import os
from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import Fullmatch
from nonebot.log import logger
from .db import randpic_command_del_tuple, randpic_path, DBConnectionManager

delete = on_fullmatch(randpic_command_del_tuple, priority=2, block=True)

@delete.got("pic", prompt="发一下要删除的图片编号喵~")
async def delete_pic_by_name(args: str = Fullmatch()):
    connection = await DBConnectionManager.get_connection(randpic_path)

    # 提取图片编号和图库名称
    command = args.strip()
    try:
        gallery_name, pic_num = command.split('_')
        pic_num = int(pic_num)
    except ValueError:
        await delete.send(Message("\n图片编号格式不正确哦~"))
        return

    # 检查图片是否存在于数据库中
    async with connection.cursor() as cursor:
        await cursor.execute(f'SELECT img_path FROM Pic_of_{gallery_name} WHERE pic_num=?', (pic_num,))
        row = await cursor.fetchone()
        if not row:
            await delete.send(Message(f"\n{gallery_name}图库没这张图哎~"), at_sender=True)
            return

        # 获取图片路径
        file_path_str = row[0]
        file_path = (randpic_path / file_path_str).resolve()

        # 尝试删除文件
        if file_path.exists():
            try:
                os.remove(file_path)
                logger.info(f"文件 {file_path} 已被删除")
            except OSError as e:
                logger.warning(f"删除文件失败: {e}")
                await delete.send(Message("\n删不了"), at_sender=True)
                return
        else:
            logger.warning(f"文件路径不存在: {file_path}")
            await delete.send(Message("\n文件路径不存在"), at_sender=True)
            return

        # 从数据库中删除记录
        await cursor.execute(f'DELETE FROM Pic_of_{gallery_name} WHERE pic_num=?', (pic_num,))
        await connection.commit()

        # 提示删除成功
        await delete.send(Message("\n好嘟，删除了"), at_sender=True)