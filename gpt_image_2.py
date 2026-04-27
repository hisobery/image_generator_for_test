# -*- coding: utf-8 -*-
import requests
import json
import base64
import os
from datetime import datetime

#此处为API地址和API Key
url = "https://XXXXX/v1/images/generations"#BaseURL
api_key = "sk-XXXXX"#API Key
#此处为提示词和画面比例
prompt = r'''#提示词
一个金属苹果雕塑
''' 
aspect_ratio="1:1" #画面比例

# 读取图片(这个列表里放需要转换的图片链接，如果不需要转换图片，可以保持为空列表)
image = []

# 组装请求体，指定模型、提示词、画面比例、质量等参数
payload = json.dumps({
   "model": "gpt-image-2",
   "prompt":prompt,
   "aspect_ratio": aspect_ratio,
   "quality": "high",
   "image":image
})
headers = {
   'Authorization': f'Bearer {api_key}',
   'Content-Type': 'application/json'
}
#发送请求
response = requests.request("POST", url, headers=headers, data=payload)

# 保存图片（ds写的）

# 1. 检查 HTTP 状态码
# 如果API返回的不是200（成功），则打印状态码和响应正文（可能包含错误描述），然后通过 exit() 终止程序运行。
if response.status_code != 200:
    print(f"请求失败，状态码：{response.status_code}")
    print("错误详情：", response.text)
    exit()

# 2. 解析 JSON
# 尝试将响应内容解析为Python字典。如果响应体不是合法的JSON格式（如服务器返回了HTML报错页），抛出 json.JSONDecodeError 异常，打印原始内容并退出。
try:
    result = response.json()
except json.JSONDecodeError:
    print("响应不是有效的 JSON 格式：", response.text)
    exit()

# 3. 提取 data 列表中的 url
# 根据类似OpenAI的返回格式，生成结果通常放在 data 字段中，且是一个列表，每个元素包含一张生成图片的信息（至少含 url 字段）。
# 如果 data 为空或不存在，打印完整响应（格式化JSON）并退出。
images_data = result.get("data", [])
if not images_data:
    print("响应中未包含任何图片数据。")
    print("完整响应：", json.dumps(result, indent=2, ensure_ascii=False))
    exit()

# 4. 创建保存目录
# 获取当前 .py 文件所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 定义保存图片的文件夹名称（与脚本同目录）
save_dir = os.path.join(script_dir, "generated_images")

# 创建目录（如果不存在）
os.makedirs(save_dir, exist_ok=True)

# 5. 下载并保存图片

'''
取出第一张图片的 url 字段（假设生成了至少一张图）。若 url 缺失则报错退出。

向提取到的图片URL发送GET请求，下载图片的二进制数据。
若下载成功（状态码200）：
确定文件扩展名：使用 os.path.splitext(img_url)[-1] 获取URL最后一个点后面的部分（如 .png），然后通过 .split("?")[0] 去除可能的查询参数（例如 ?token=...）。如果提取结果为空，则默认使用 .png。
生成带时间戳的文件名：image_20260426_143021.png 这样的格式，避免重名。
拼接完整的保存路径，以二进制写入模式（"wb"）打开文件，将 img_response.content（图片字节数据）写入磁盘。
若下载失败（URL可能已失效），打印失败状态码。
'''

img_url = images_data[0].get("url")
if not img_url:
    print("图片URL不存在。")
    exit()

print(f"正在下载图片：{img_url}")

img_response = requests.get(img_url)
if img_response.status_code == 200:
    # 从URL中提取文件扩展名
    ext = os.path.splitext(img_url)[-1].split("?")[0]
    if not ext:
        ext = ".png"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"image_{timestamp}{ext}"
    filepath = os.path.join(save_dir, filename)

    with open(filepath, "wb") as f:
        f.write(img_response.content)
    print(f"已保存至：{filepath}")
else:
    print(f"下载失败，状态码：{img_response.status_code}")
