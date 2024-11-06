# noneBot-plugin-gallery

## 介绍

可以在本地创建多个图库，并且可通过QQ聊天栏对图库进行添加、删除、查询，聊天消息可随机触发发送图库中的图片（可选模式：精准匹配或模糊匹配）

## 功能

图库管理，随机发图

## 使用方法

### 指令说明：
- `{图库名}` - 触发图片发送
- `添加{图库名} 标签` - 向指定图库添加图片
- `删除{图库名}` - 删除指定图库的一张图
- `查看{图库名}` - 查看指定图库的所有图片
- 
### 示例：
![Uploading cbcc3d90ad707ab256d754dbffb0dbc7.jpg…]()
![07cbc7ebcbb206d6552241e90ff6a926](https://github.com/user-attachments/assets/f701e0ea-1450-4632-9242-fbc688667e91)
![58424caa1355e1f9fcf9fe7f4e359c36](https://github.com/user-attachments/assets/20b81f34-1a41-43d8-a2fa-8057e0ebb4c9)


## 安装方法

<details open>
<summary>通过 nb-cli 安装</summary>

在 NoneBot2 项目的根目录下打开命令行，输入以下指令安装插件：

```sh
nb plugin install nonebot-plugin-gpt-sovits
```
</details>

<details>
<summary>通过包管理器安装</summary>

在 NoneBot2 项目的插件目录下，打开命令行，根据你使用的包管理器，输入相应的安装命令：

<details>
<summary>pip</summary>

```sh
pip install nonebot-plugin-gpt-sovits
```
</details>

<details>
<summary>pdm</summary>

```sh
pdm add nonebot-plugin-gpt-sovits
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
conda install nonebot-plugin-gpt-sovits
```
</details>

然后，打开 NoneBot2 项目根目录下的 `pyproject.toml` 文件，在 `[tool.nonebot]` 部分追加：

```toml
plugins = ["nonebot_plugin_gpt_sovits"]
```

</details>

## 配置

在 `.env` 文件中添加以下配置：

| 配置项                   | 默认值                     | 说明 |
| ------------------------ | -------------------------- | --- |
| GPT_SOVITS_API_BASE_URL   | http://127.0.0.1:9880       | 可选。GPT-SoVITS API 的 URL |
| GPT_SOVITS_API_V2         | True                        | 可选。是否使用 GPT-SoVITS API v2。注意：API 是否为 v2 不取决于你使用的 GPT-SoVITS 模型版本，而是由你运行的 API 脚本决定。`api_v2.py` 为 API v2，`api.py` 为 API v1 |
| GPT_SOVITS_COMMAND        | tts                         | 可选。触发 TTS 的命令，可自定义为 GPT-SoVITS 角色名 |
| GPT_SOVITS_CONVERT_TO_SILK| False                       | 可选。是否将生成音频转换为 SILK 格式发送 |
| GPT_SOVITS_EMOTION_MAP    | 无默认值                     | 必填。配置情感映射 |
| GPT_SOVITS_ARGS           | 无默认值                     | 可选。传递给 GPT-SoVITS 的额外参数，如 `{"temperature": 0.9}` |

### GPT_SOVITS_EMOTION_MAP 示例配置：

```json
[
  {
    "name": "平静",
    "sentences": [
      {"text": "示例文本1", "language": "zh", "path": "路径1"},
      {"text": "示例文本2", "language": "zh", "path": "路径2"}
    ]
  },
  {
    "name": "激动",
    "sentences": [
      {"text": "示例文本3", "language": "zh", "path": "路径3"}
    ]
  }
]
```

### GPT_SOVITS_ARGS 配置说明

一般不需要配置此项，但如果你需要传递额外参数给 GPT-SoVITS，可以展开阅读如何配置。

<details>
<summary>点击展开</summary>

- 对于使用 `api.py`（将 `GPT_SOVITS_API_V2` 设置为 `False`）的用户，可配置以下参数：
    - `cut_punc`（`str` 类型）：用于切分句子的标点符号，默认值为 "，。"
    - `top_k`（`int` 类型）：生成文本的 Top-K，默认值为 10
    - `top_p`（`float` 类型）：生成文本的 Top-P，默认值为 1.0
    - `temperature`（`float` 类型）：生成文本的温度，默认值为 1.0
    - `speed`（`float` 类型）：生成音频的播放速度，默认值为 1.0

- 对于使用 `api_v2.api`（将 `GPT_SOVITS_API_V2` 设置为 `True`）的用户，可配置以下参数：
    - `aux_ref_audio_paths`（`list` 类型）：用于生成文本的参考音频路径，默认值为 []
    - `top_k`（`int` 类型）：生成文本的 Top-K，默认值为 5
    - `top_p`（`float` 类型）：生成文本的 Top-P，默认值为 1.0
    - `temperature`（`float` 类型）：生成文本的温度，默认值为 1.0
    - `text_split_method`（`str` 类型）：切分文本的方法，默认值为 `cut3`（按中文句号切），可选值：
        - `cut0`：不切分
        - `cut1`：四句一切
        - `cut2`：50字一切
        - `cut3`：按中文句号切
        - `cut4`：按英文句号切
        - `cut5`：按标点符号切
    - `batch_size`（`int` 类型）：生成文本的 Batch 大小，默认值为 1
    - `batch_threshold`（`float` 类型）：生成文本的 Batch 阈值，默认值为 0.75
    - `split_bucket`（`bool` 类型）：是否分割 Batch，默认值为 True
    - `speed_factor`（`float` 类型）：生成音频的速度因子，默认值为 1.0
    - `fragment_interval`（`float` 类型）：片段间隔，默认值为 0.3
    - `streaming_mode`（`bool` 类型）：是否流式返回，默认值为 False
    - `seed`（`int` 类型）：随机种子，-1 为随机，默认值为 -1
    - `parallel_infer`（`bool` 类型）：是否使用并行推理，默认值为 True
    - `repetition_penalty`（`float` 类型）：重复惩罚，默认值为 1.35

</details>


## 额外配置

若启用 `GPT_SOVITS_CONVERT_TO_SILK`，请进行以下额外配置：

1. 将 `ffmpeg` 添加到环境变量
2. 下载 [silk_cli](https://github.com/idranme/silk-cli/releases) 并放置于 Bot 根目录，重命名为 `cli.exe`（Windows）或 `cli`（Linux）
3. 完成配置
