import os
from pathlib import Path
from typing import Tuple, List, Set
from nonebot import get_driver
from nonebot.log import logger
import asyncio
import hashlib
import aiosqlite
from .config import config

class DBConnectionManager:
    _instance = None
    _connection = None

    @classmethod
    async def get_connection(cls, db_path: Path) -> aiosqlite.Connection:
        if cls._connection is None:
            cls._connection = await aiosqlite.connect(db_path / "data.db")
        return cls._connection

    @classmethod
    async def close_connection(cls):
        if cls._connection:
            await cls._connection.close()
            cls._connection = None


randpic_command_list: List[str] = config.accurate_keywords + config.fuzzy_keywords  # 将命令列表转换为集合和元组
randpic_command_set: Set[str] = set(randpic_command_list)
randpic_command_tuple: Tuple[str, ...] = tuple(randpic_command_set)  # 形成指令元组
randpic_command_add_tuple = tuple("添加" + tup for tup in randpic_command_tuple)  # 形成添加指令元组
randpic_command_del_tuple = tuple("删除" + tup for tup in randpic_command_tuple)  # 用于删除图片的指令
randpic_path = Path(config.randpic_store_dir_path) # 设置图片存储路径
randpic_command_path_tuple = tuple(randpic_path / command for command in randpic_command_tuple)  # 形成指令文件夹路径元组


driver = get_driver()

# 启动时的初始化操作
@driver.on_startup
async def _():
    logger.info("正在检查文件...")
    await asyncio.create_task(create_file())
    logger.info("文件检查完成，欢迎使用插件！")

# 关闭时的操作
@driver.on_shutdown
async def close_connection():
    logger.info("正在关闭数据库")
    await DBConnectionManager.close_connection()

# 创建所需文件夹和数据库
async def create_file():
    # 创建文件夹
    for path in randpic_command_path_tuple:
        if not path.exists():
            logger.warning('未找到{path}文件夹，准备创建{path}文件夹...'.format(path=path))
            path.mkdir(parents=True, exist_ok=True)

    # 创建数据库和数据表
    connection = await DBConnectionManager.get_connection(randpic_path)
    cursor = await connection.cursor()

    # 创建每个命令对应的数据表
    for command in randpic_command_tuple:
        await cursor.execute('DROP table if exists Pic_of_{command};'.format(command=command))
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS Pic_of_{command} (
                md5 TEXT PRIMARY KEY,
                img_url TEXT
            )
            '''.format(command=command))
        await connection.commit()

    # 读取所有文件夹文件，写入数据库
    for index in range(len(randpic_command_path_tuple)):
        path: Path = randpic_command_path_tuple[index]
        randpic_file_list = os.listdir(path)
        for i in range(len(randpic_file_list)):
            filename: str = randpic_file_list[i]
            with (path / filename).open('rb') as f:
                data = f.read()
            fmd5 = hashlib.md5(data).hexdigest()

            cursor = await connection.cursor()
            command: str = randpic_command_tuple[index]
            await cursor.execute(
                'INSERT or REPLACE INTO Pic_of_{command}(md5, img_url) VALUES (?, ?)'.format(command=command),
                (fmd5, str(Path() / command / filename)))
            await connection.commit()



