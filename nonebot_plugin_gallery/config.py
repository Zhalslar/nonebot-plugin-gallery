
from pathlib import Path

class Config:
    """
    配置类，用于存储和管理应用的配置项。
    """
    def __init__(self):
        # 本插件工作目录的绝对路径
        self.plugin_dir = Path(__file__).resolve().parent
        # bot 的根目录的绝对路径
        self.bot_root_dir =  Path("/root/bot5")
        # 用户自定义的图片存储文件夹路径
        self.all_gallery_path = self.bot_root_dir / "all_gallery"
        # 关键词json文件的路径
        self.keywords_path = self.plugin_dir / "keywords.json"
        # 下载图片时是否压缩图片，默认开启
        self.default_compress_switch = True
        # 压缩阈值(单位为像素)，图片在512像素以下时qq以表情包大小显示
        self.compress_size = 512
        # 添加图片时是否检查并跳过重复图片
        self.duplicate_switch = True
        # 精准匹配列表
        self.accurate_keywords: list[str] = []
        # 模糊匹配列表
        self.fuzzy_keywords: list[str] = []
        # 默认匹配模式,"a"为精准匹配，“f”为模糊匹配
        self.default_mode = "a"
        # 精准匹配时发送图片的概率
        self.exact_match_prob = 0.99
        # 模糊匹配时发送图片的概率
        self.fuzzy_match_prob = 0.99


# 关键：创建一个全局的Config实例，这个实例里的精准匹配列表和模糊匹配列表能全局动态更新，从而确保图库的热重载性
config = Config()
