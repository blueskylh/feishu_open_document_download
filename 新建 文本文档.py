import os
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://open.feishu.cn"
SAVE_ROOT = "Feishu_Docs"


def download_from_html(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # 找到所有的节点容器
    items = soup.find_all('div', class_='ud__tree__node')
    path_stack = [SAVE_ROOT]

    if not os.path.exists(SAVE_ROOT):
        os.makedirs(SAVE_ROOT)

    for item in items:
        # 1. 算深度 (找 width: XXpx)
        indent_div = item.find('div', style=lambda s: s and 'width' in s)
        depth = int(indent_div['style'].split('width:')[1].split('px')[0].strip()) // 16 if indent_div else 0

        # 2. 拿标题和链接
        label_div = item.find('div', class_='side-tree__item')
        if not label_div: continue
        title = label_div.get_text().replace('/', '_').replace('\\', '_')

        a_tag = item.find_parent('a')
        href = a_tag['href'] if a_tag else None

        # 3. 维护层级目录
        path_stack = path_stack[:depth + 1]

        if not href:
            new_dir = os.path.join(*path_stack, title)
            os.makedirs(new_dir, exist_ok=True)
            path_stack.append(title)
        else:
            current_dir = os.path.join(*path_stack)
            os.makedirs(current_dir, exist_ok=True)
            file_path = os.path.join(current_dir, f"{title}.md")

            # 下载文件
            print(f"下载: {title}")
            res = requests.get(f"{BASE_URL}{href.split('?')[0]}.md", headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code == 200:
                with open(file_path, 'w', encoding='utf-8') as mf:
                    mf.write(res.text)
            time.sleep(0.1)


if __name__ == "__main__":
    download_from_html("feishu_tree.html")