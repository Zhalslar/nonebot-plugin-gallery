from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.params import CommandArg
from .utils import(
    send_random_image,
    list_files_in_directory,
    extract_folder_names,
    get_user_label,
    get_at_label,
    send_f,
)
from .config import config


view_gallery = on_command("查看", priority=10, block=True)

@view_gallery.handle()
async def handle_view_gallery(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    """指令管理器"""
    parts: list = args.extract_plain_text().strip().split()
    at_label = await get_at_label(bot,event)
    user_label = await get_user_label(bot,event)
    # 查看自己的图库
    if not parts and not at_label:
        await view_one_gallery(bot, event, user_label)
    # 查看被@者的图库
    elif not parts and at_label:
        await view_one_gallery(bot, event, at_label)
    #查看被@者的图库里某编号图片
    elif len(parts) == 1 and at_label:
        await view_picture(bot,event,at_label,int(parts[0]))
    # 查看自己图库下的某编号的图
    elif len(parts) == 1 and parts[0].isdigit():
        await view_picture(bot, event, user_label, parts[0])
    # 查看所有图库
    elif len(parts) == 1 and parts[0] == "all":
        await view_all_gallery(bot, event)
    # 查看指定图库
    elif len(parts) == 1:
        await view_one_gallery(bot, event, parts[0])
    #查看某编号的图片
    elif len(parts) == 2 and parts[1].isdigit():
        await view_picture(bot,event,parts[0],int(parts[1]))
    else:
        await view_gallery.finish(f"图库【{parts[0]}】未创建或指令错误")


async def view_all_gallery(bot: Bot, event: MessageEvent):
    """查看所有图库"""
    all_gallery = await extract_folder_names(config.all_gallery_path)
    if not all_gallery:
        await bot.send(event, "当前没有任何图库")
    else:
        gallery_list = "\n".join(all_gallery)
        await send_f(bot, event, f"所有图库：\n{gallery_list}")
    return


async def view_one_gallery(bot:Bot,event:MessageEvent,gallery_name):
    """查看名为gallery_name的图库"""
    g_path = config.all_gallery_path / gallery_name
    image_name_list = await list_files_in_directory(g_path)
    if not image_name_list:
        await bot.send(event, f"图库【{gallery_name}】中没有图片")
    else:
        sorted_list = sorted(image_name_list, key=lambda x: (int(x.split('_')[1]), x.split('_')[0]))
        image_str = "\n".join(sorted_list)
        reply = f"【{gallery_name}】图库：\n{image_str}"
        await send_f(bot, event, reply)


async def view_picture(bot: Bot, event: MessageEvent, gallery_name:str, index:int):
    """查看gallery_name图库下编号为index的图片"""
    g_path = config.all_gallery_path / gallery_name
    image_names = await list_files_in_directory(g_path)
    if not image_names:
        await bot.send(event, f"图库【{gallery_name}】中没有图片")
        return
    formatted_name = f"{gallery_name}_{index}_"
    selected_image = next((img for img in image_names if img.startswith(formatted_name)), None)
    if selected_image:
        image_path = g_path / selected_image
        await send_random_image(bot, event, image_path, 1)
    else:
        await send_f(bot, event, f"图库【{gallery_name}】中没有序号为 {index} 的图片")
    return




