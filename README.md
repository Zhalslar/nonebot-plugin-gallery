# nonebot-plugin-gallery

## 介绍

可以在本地创建多个图库，并且可通过QQ聊天栏对图库进行添加、删除、查询，聊天消息可随机触发发送图库中的图片（可选模式：精准匹配或模糊匹配）

## 指令说明：
- `{图库名}` - 触发图片发送（精准匹配or模糊匹配）
- `添加{图库名} 标签` - 向指定图库添加图片
- `删除{图库名}` - 删除指定图库的一张图
- `查看{图库名}` - 查看指定图库的所有图片

## 安装方法

<details open>
<summary>通过 nb-cli 安装</summary>

在 NoneBot2 项目的根目录下打开命令行，输入以下指令安装插件：

```sh
nb plugin install nonebot-plugin-gallery
```
</details>

<details>
<summary>通过包管理器安装</summary>

在 NoneBot2 项目的插件目录下，打开命令行，根据你使用的包管理器，输入相应的安装命令：

<details>
<summary>pip</summary>

```sh
pip install nonebot-plugin-gallery
```
</details>

<details>
<summary>pdm</summary>

```sh
pdm add nonebot-plugin-gallery
```
</details>

<details>
<summary>poetry</summary>

```sh
poetry add nonebot-plugin-gpt-sovits
```
</details>

<details>
<summary>conda</summary>

```sh
conda install nonebot-plugin-gallery
```
</details>

然后，打开 NoneBot2 项目根目录下的 `pyproject.toml` 文件，在 `[tool.nonebot]` 部分追加：

```toml
plugins = ["nonebot_plugin_ggallery"]
```

</details>


## 配置（示例，按需修改）

```python
# 用户自定义图片存储文件夹路径
randpic_store_dir_path: str = "D://mybot//Nonebot//bot2//randpic"

# 精准匹配关键词
accurate_keywords = [
    "new"
]

# 模糊匹配关键词
fuzzy_keywords = [
    "帮助"
]

#是否压缩图片
compress = False

#压缩阈值(单位为像素)
compression_threshold = 512
