import re

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, Event

message_handler = on_command("你是？")

@message_handler.handle()

async def get_reply_label(bot: Bot, event: Event) ->str:
    """获取事件中被引用消息者的标签"""
    reply = event.dict().get("reply")
    if reply:
        quoted_user_qq = reply.get("sender", {}).get("user_id")
        return await id_to_label(bot, event, quoted_user_qq)


async def get_user_label(bot:Bot, event: Event):
    """获取事件中发送消息者的标签"""
    return id_to_label(bot, event, event.user_id)


async def get_at_label(bot: Bot, event: Event)->list:
    """获取事件中所有被@者的标签"""
    at_members = [seg.data['qq'] for seg in event.message if seg.type == 'at']
    label_list = []
    for user_id in at_members:
        label_list.append(await id_to_label(bot, event, user_id))
    return label_list

async def id_to_label(bot:Bot, event:Event, user_id:str) ->str:
    """获取用户标签（优先群昵称, 其次用户昵称，最后用户ID）"""
    member_info = await bot.get_group_member_info(group_id=event.group_id,user_id=int(user_id))
    label = member_info.get("card") or member_info.get("nickname") or str(event.user_id)
    pattern = r'[\u4e00-\u9fa5a-zA-Z0-9]'
    label = ''.join(re.findall(pattern, label))
    return label