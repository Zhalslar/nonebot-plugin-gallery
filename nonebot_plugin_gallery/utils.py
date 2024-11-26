
import hashlib
import random
import re
import json
import aiofiles
from PIL import Image
from nonebot import Bot,logger
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, GroupMessageEvent, Event
from aiofiles import os
from httpx import AsyncClient
from typing import List
import os
from pathlib import Path



# -----------------json工具-------------------

def init_json_file(file_path, keys) -> None:
    """初始化JSON文件，确保指定的键存在"""
    data = read_json(file_path)
    for key in keys:
        if key not in data:
            data[key] = []
    write_json(file_path, data)


def read_json(file_path) -> dict:
    """读取JSON文件并返回一个字典"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_json(file_path, dict_data) -> None:
    """将字典写入JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(dict_data, file, indent=4)


def get_list_from_json(json_path, key) -> list:
    """从json文件中取出列表"""
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
        if key in data and isinstance(data[key], list):
            return data[key]
        else:
            return []
    except FileNotFoundError:
        print(f"The file {json_path} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"The file {json_path} is not a valid JSON file.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def update_element_in_json(json_path, key, element, remover:bool=False) -> None:
    """更新json文件里对应键下的指定元素：remover关闭时，添加指定元素； remover打开时，删除指定元素"""
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
        if key in data and isinstance(data[key], list):
            if remover and element in data[key]:
                data[key].remove(element)
            elif not remover and element not in data[key]:
                data[key].append(element)
        else:
            data[key] = [element] if not remover else []

        with open(json_path, 'w') as file:
            json.dump(data, file, indent=4)
    except FileNotFoundError:
        print(f"The file {json_path} was not found.")
    except json.JSONDecodeError:
        print(f"The file {json_path} is not a valid JSON file.")
    except Exception as e:
        print(f"An error occurred: {e}")




# -----------------------label工具--------------------------

async def get_reply_label(bot: Bot, event: Event) ->str:
    """获取事件中被引用消息者的标签"""
    reply = event.dict().get("reply")
    if reply:
        quoted_user_qq = reply.get("sender", {}).get("user_id")
        return await id_to_label(bot, event, quoted_user_qq)


async def get_user_label(bot:Bot, event: Event):
    """获取事件中发送消息者的标签"""
    return await id_to_label(bot, event, event.user_id)


async def get_at_label(bot: Bot, event: Event, select_num:int = 0)->str:
    """获取事件中所有被@者的标签"""
    at_members = [seg.data['qq'] for seg in event.message if seg.type == 'at']
    if at_members:
        label_list = []
        for user_id in at_members:
            label_list.append(await id_to_label(bot, event, user_id))
        return label_list[select_num]
    else: return ""

async def id_to_label(bot:Bot, event:Event, user_id:str) ->str:
    """获取用户标签（优先群昵称, 其次用户昵称，最后用户ID）"""
    member_info = await bot.get_group_member_info(group_id=event.group_id,user_id=int(user_id))
    label = member_info.get("card") or member_info.get("nickname") or str(event.user_id)
    pattern = r'[\u4e00-\u9fa5a-zA-Z0-9]'
    label = ''.join(re.findall(pattern, label))
    return label




# -----------------------files工具--------------------------


def create_subfolders(root_folder, subfolder_names):
    """根据子文件夹名创建子文件夹，如果已存在则跳过"""
    for name in subfolder_names:
        subfolder_path = Path(root_folder) / name
        if not subfolder_path.exists():
            subfolder_path.mkdir()

async def extract_folder_names(directory_path) -> List[str]:
    """获取directory_path目录下所有文件名，返回列表"""
    folder_names = []
    try:
        entries = await aiofiles.os.scandir(directory_path)
        for entry in entries:
            if entry.is_dir():
                folder_names.append(entry.name)
    except Exception as e:
        print(f"错误: {e}")
    return folder_names


async def list_files_in_directory(path: Path) -> List[str]:
    """获取path路径下的所有文件名称列表"""
    if not path.exists() or not path.is_dir():
        return []
    all_items = [item for item in path.iterdir() if item.is_file()]
    files = [item.name for item in all_items]
    return files


async def delete_path(path: Path) -> None:
    """删除path路径下所有的文件或文件夹"""
    try:
        if not path.exists():
            raise FileNotFoundError(f"路径不存在: {path}")
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            for child in path.iterdir():
                await delete_path(child)
            path.rmdir()
        else:
            raise ValueError(f"未知的路径类型: {path}")
    except Exception as e:
        raise e




# -----------------------image工具--------------------------


async def download_image(pic_url: str, path, picture_name: str) -> None:
    """下载图片，并以指定图片名命名，保存到path路径"""
    async with AsyncClient() as client:
        try:
            resp = await client.get(pic_url, timeout=5.0)
            resp.raise_for_status()  # 如果响应状态码不是200，将抛出异常
            save_path = path / picture_name
            async with aiofiles.open(save_path, mode='wb') as f:
                await f.write(await resp.aread())
        except Exception as e:
            logger.warning(f"下载图片失败: {e}")
            return


def compress_image(path, max_size: int = 512) -> None:
    """压缩path路径的图片到max_size大小，GIF不处理"""
    try:
        with open(path, 'r+b') as file:
            image = Image.open(file)
            if image.format == "GIF":
                return
            if image.width > max_size or image.height > max_size:
                image.thumbnail((max_size, max_size))
            image.save(path, format=image.format)
    except Exception as e:
        raise ValueError(f"图片压缩失败: {e}")


def fix_image_extension(image_path: Path) -> str:
    """检查并修正image_path路径下的图片的扩展名，使其与实际格式一致"""
    if not image_path.is_file():
        raise ValueError(f"The path {image_path} is not a valid file.")
    try:
        with Image.open(image_path) as img:
            actual_extension = f".{img.format.lower()}"
    except Exception as e:
        raise ValueError(f"无法打开 {image_path}路径下的图片: {e}")

    current_extension = image_path.suffix.lower()
    if current_extension != actual_extension:
        new_name = image_path.with_suffix(actual_extension)
        image_path.rename(new_name)
        return new_name.name
    return image_path.name


def check_duplicate_image(folder_path, new_image_path) -> bool:
    """检查文件夹内是否有重复的图片"""
    new_image_hash = get_image_hash(new_image_path)
    for filename in folder_path.iterdir():
        if filename.is_file() and filename != new_image_path:
            existing_image_hash = get_image_hash(filename)
            if new_image_hash == existing_image_hash:
                return True
    return False


def get_image_hash(image_path) -> str:
    """计算图片的哈希值"""
    hash_sha256 = hashlib.sha256()
    with open(image_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()





# -----------------------send工具--------------------------


async def send_random_image(bot, event, folder_path, probability: float = 1.0):
    """随机发送folder_path路径下的一张图片，或者指定图片，probability概率默认为1，即百分百发送"""
    # 检查路径是否存在
    if not os.path.exists(folder_path):
        logger.info(f"文件或文件夹路径不存在: {folder_path}")
        return

    if os.path.isfile(folder_path):
        if random.random() < probability:
            try:
                await bot.send(event, MessageSegment.image(f"file://{folder_path}"))
            except Exception as e:
                logger.info(f"图片发送失败: {e}")
                logger.info(f"尝试发送的图片路径: {folder_path}")
        else:
            logger.info("匹配到关键词，但概率不满足，不发送图片")
        return

    files = os.listdir(folder_path)
    if not files:
        logger.info(f"文件夹为空: {folder_path}")
        return

    selected_image = random.choice(files)
    selected_image_path = os.path.join(folder_path, selected_image)

    if random.random() < probability:
        try:
            await bot.send(event, MessageSegment.image(f"file://{selected_image_path}"))
        except Exception as e:
            logger.info(f"图片发送失败: {e}")
            logger.info(f"尝试发送的图片路径: {selected_image_path}")
    else:
        logger.info("匹配到关键词，但概率不满足，不发送图片")



async def send_f(bot: Bot, event: MessageEvent, arg: str, max_length:int=100):
    """消息长度超过max_length则自动转发"""
    arg = re.sub(r'\n*$', '', arg)
    if len(arg) < max_length:
        await bot.send(event, arg)
    else:
        messages = {
            "type": "node",
            "data": {
                "name": "return",
                "uin": bot.self_id,
                "content": MessageSegment.text(arg)
            }
        }
        if isinstance(event, GroupMessageEvent):
            return await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=messages)
        else:
            return await bot.call_api("send_private_forward_msg", user_id=event.user_id, messages=messages)





