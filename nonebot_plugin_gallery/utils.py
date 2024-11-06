import os
from datetime import datetime
from hashlib import md5
from typing import List
from PIL import Image
import io
from pathlib import Path
from nonebot import logger
from .db import randpic_command_tuple, randpic_path, DBConnectionManager


def resize_image(image: Image.Image, max_size: int = 512) -> bytes:
    """
    缩放图像至指定的最大宽高尺寸，并返回字节数据。
    参数:
        image (Image.Image): 要处理的图像对象。
        max_size (int): 图像的最大宽度或高度，默认为 512 像素。
    返回:
        bytes: 缩放后的图像数据。
        @rtype: object
    """
    if image.width > max_size or image.height > max_size:
        image.thumbnail((max_size, max_size))
    output = io.BytesIO()
    image.save(output, format=image.format)
    return output.getvalue()





async def get_all_images_in_gallery(gallery_name: str) -> List[str]:
    """
    查询数据库，获取指定图库下所有图片的名称。

    参数:
    - gallery_name: 图库的名称。

    返回:
    - 一个包含所有图片名称的列表。
    """
    if gallery_name not in randpic_command_tuple:  # 假设randpic_command_tuple是一个包含所有图库名称的元组
        logger.error(f"图库 {gallery_name} 不存在")
        return []

    try:
        connection = await DBConnectionManager.get_connection(randpic_path)  # 假设randpic_path是数据库文件的路径
        table_name = f"Pic_of_{gallery_name}"
        async with connection.execute(f"SELECT img_url FROM {table_name}") as cursor:
            image_names = [Path(row[0]).name for row in await cursor.fetchall()]
        return image_names
    except Exception as e:
        logger.error(f"获取图库 {gallery_name} 图片列表时出错: {e}")
        return []





def rename_files(randpic_file_list, path):
    """
    重命名文件的函数。

    参数:
    - randpic_file_list: 原始文件列表。
    - path: 文件所在的路径。
    """
    # 生成hash_str，这里使用当前时间戳作为哈希的基础
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_str = md5(current_time.encode()).hexdigest()[:8]  # 取前8位作为hash_str

    # 重命名文件
    for i, filename in enumerate(randpic_file_list):
        filename_without_extension, filename_extension = os.path.splitext(filename)
        current_time = datetime.now().strftime("%m%d%H%M")
        hash_new_filename = (
            hash_str +
            f"{randpic_command_tuple[i]}_{i + 1}_{current_time}" +
            (filename_extension if filename_extension != '' else '.jpg')
        )
        os.rename(path / filename, path / hash_new_filename)

    # 更新文件列表以包含新命名的文件
    randpic_file_list = os.listdir(path)

    # 将哈希化的文件名恢复为规范名
    for i, hash_filename in enumerate(randpic_file_list):
        new_filename = hash_filename.replace(hash_str, '', 1)  # 只替换第一次出现的hash_str
        os.rename(path / hash_filename, path / new_filename)