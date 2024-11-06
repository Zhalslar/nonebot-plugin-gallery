from nonebot import on_fullmatch, logger
from nonebot.adapters.onebot.v11 import MessageSegment, Event, GROUP
from .config import accurate_keywords
from .db import randpic_path, DBConnectionManager

# 精准匹配
picture = on_fullmatch(accurate_keywords, permission=GROUP, priority=5, block=True)

@picture.handle()
async def pic(event: Event):
    connection = await DBConnectionManager.get_connection(randpic_path)
    cursor = await connection.cursor()

    command = str(event.get_message()).strip()
    await cursor.execute(f'SELECT img_url FROM Pic_of_{command} ORDER BY RANDOM() limit 1')
    data = await cursor.fetchone()

    if data is None: await picture.finish()

    file_name = data[0]
    img = randpic_path / file_name
    try:
        await picture.send(MessageSegment.image(img))
    except Exception as e:
        logger.info(e)

