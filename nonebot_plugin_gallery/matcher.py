import os
from nonebot import logger, Bot, on_command
from nonebot.adapters.onebot.v11 import Event, MessageEvent
from nonebot import on_message
from nonebot.adapters import Message
from nonebot.params import EventMessage, CommandArg
from nonebot.permission import SUPERUSER
from .config import config
from .utils import send_random_image, update_element_in_json, send_f

# 精准匹配的动态逻辑
accurate_matcher = on_message(priority=99, block=True)

@accurate_matcher.handle()
async def _(bot: Bot, event: Event, message: Message = EventMessage()):
    msg_text = str(message).strip()
    if msg_text in config.accurate_keywords:
        keyword = str(event.get_message()).strip()
        logger.info(f"精准匹配到关键词: {keyword}")
        matched_path = os.path.join(config.randpic_gallery_path, keyword)
        await send_random_image(bot, event, matched_path, config.exact_match_prob)


# 模糊匹配的动态逻辑
keyword_picture = on_message(priority=99, block=True)

@keyword_picture.handle()
async def _(bot: Bot, event: Event):
    message_text = str(event.get_message()).strip()
    for keyword in config.fuzzy_keywords:
        if keyword in message_text:
            logger.info(f"模糊匹配到关键词: {keyword}")
            matched_path = os.path.join(config.randpic_gallery_path, keyword)
            await send_random_image(bot, event, matched_path, config.fuzzy_match_prob)


accurate_list_matcher = on_command('精准匹配列表',aliases={"精准列表"}, priority=10, block=True)

@accurate_list_matcher.handle()
async def _(bot: Bot, event: MessageEvent):
    reply = f"【精准匹配列表】：\n{str(config.accurate_keywords)}"
    await send_f(bot, event, reply)


fuzzy_list_matcher = on_command('模糊匹配列表',aliases={"模糊列表"}, priority=10, block=True)

@fuzzy_list_matcher.handle()
async def _(bot: Bot, event: MessageEvent):
    reply = f"【模糊匹配列表】：\n{str(config.fuzzy_keywords)}"
    await send_f(bot, event, reply)


accurate_add = on_command('精准匹配列表+',aliases={"精准匹配+","精准列表+","精准+"},permission=SUPERUSER, priority=10, block=True)
@accurate_add.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    args_text: str = args.extract_plain_text().strip()
    parts: list = args_text.split()
    reply = "操作流程记录："
    for keyword in parts:
         if keyword not in config.accurate_keywords:
             config.accurate_keywords.append(keyword)
             update_element_in_json(config.keywords_path, "accurate_keywords", keyword)
             reply += "\n" + keyword + "成功添加到精准列表"
         else:
             reply += f"\n“{keyword}” 在精准列表中已存在"
         if keyword in config.fuzzy_keywords:
             config.fuzzy_keywords.remove(keyword)
             update_element_in_json(config.keywords_path, "fuzzy_keywords", keyword, True)
             reply += "\n" + keyword + "已从模糊列表中删除"
    await send_f(bot, event, reply)



accurate_add = on_command('模糊匹配列表+',aliases={"模糊匹配+","模糊列表+","模糊+"},permission=SUPERUSER, priority=10, block=True)
@accurate_add.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    args_text: str = args.extract_plain_text().strip()
    parts: list = args_text.split()
    reply = "操作流程记录："
    for keyword in parts:
         if keyword not in config.fuzzy_keywords:
             config.fuzzy_keywords.append(keyword)
             update_element_in_json(config.keywords_path, "fuzzy_keywords", keyword)
             reply += f"\n“{keyword}” 成功添加到模糊列表"
         else:
             reply += f"\n“{keyword}” 在模糊列表中已存在"
         if keyword in config.accurate_keywords:
             config.accurate_keywords.remove(keyword)
             update_element_in_json(config.keywords_path, "accurate_keywords", keyword, True)
             reply += f"\n“{keyword}” 已从精准列表中删除"
    await send_f(bot, event, reply)


