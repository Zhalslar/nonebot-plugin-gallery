from nonebot import on_keyword, logger
from nonebot.adapters.onebot.v11 import MessageSegment, Event, GROUP
from .db import randpic_path, DBConnectionManager
from .config import fuzzy_keywords

# 模糊匹配
keyword_picture = on_keyword(fuzzy_keywords, permission=GROUP, priority=5, block=True)

@keyword_picture.handle()
async def fuzzy_pic(event: Event):
    connection = await DBConnectionManager.get_connection(randpic_path)
    cursor = await connection.cursor()
    message_text = str(event.get_message()).strip()

    # 遍历模糊关键词列表 fuzzy_keywords，判断消息内容是否包含任何关键词
    for keyword in fuzzy_keywords:
        if keyword in message_text:
            logger.info(f"模糊匹配到关键词: {keyword}")

            await cursor.execute(f'SELECT img_url FROM Pic_of_{keyword} ORDER BY RANDOM() LIMIT 1')
            data = await cursor.fetchone()
            if data is None: await keyword_picture.finish()

            file_name = data[0]
            img = randpic_path / file_name
            try:
                await keyword_picture.send(MessageSegment.image(img))
            except Exception as e:
                logger.info(e)
            return
