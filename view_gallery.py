from nonebot import on_command
from nonebot.adapters.onebot.v11 import Event, GROUP
from .utils import  get_all_images_in_gallery

view_gallery = on_command("查看", permission=GROUP, block=True)

@view_gallery.handle()
async def handle_view_gallery(event: Event):
    gallery_name = str(event.get_message()).strip()[len("查看"):]

    image_names = await get_all_images_in_gallery(gallery_name)

    if not image_names:
        await view_gallery.finish(f"图库 {gallery_name} 中没有图片或不存在。")
    else:
        image_list = "\n".join(image_names)
        await view_gallery.finish(f"{gallery_name}图库：\n{image_list}")