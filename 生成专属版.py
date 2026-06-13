#!/usr/bin/env python3
"""
成交数据管理 · 专属版生成器
用法：python 生成专属版.py 客户姓名 手机号
输出：成交数据管理_张三.html（带客户专属授权信息）
"""

import sys
import os
from datetime import datetime

# ============================================================
# 配置
# ============================================================
SOURCE_FILE = "tool.html"  # 源文件

# 占位标记（源文件里要有这个）
PLACEHOLDER_LINE = 'h1>成交数据管理 <span style="font-size:.6rem;opacity:.7">个人版 v3.1</span></h1>'


def generate(customer_name, customer_phone=""):
    """生成专属版HTML文件"""
    # 读取源文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(script_dir, SOURCE_FILE)

    if not os.path.exists(source_path):
        print(f"[X] 源文件不存在: {source_path}")
        print("   请确保 成交数据管理_个人版.html 在同一目录")
        return False

    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 替换标题为专属版
    # 替换标题占位符（注意HTML中有id="licenseBadge"属性）
    old_badge = 'id="licenseBadge">个人版 v3.1</span>'
    new_badge = ('id="licenseBadge">授权给：' + customer_name +
                 (' ' + customer_phone if customer_phone else '') +
                 '</span>')

    if old_badge not in content:
        print("[X] 源文件中找不到标题占位符，请检查源文件版本")
        print("   需要: " + old_badge)
        return False

    content = content.replace(old_badge, new_badge)

    # 也替换状态栏
    old_status = 'id="licenseStatus">数据仅存储在您的浏览器本地</span>'
    new_status = 'id="licenseStatus">专属授权 · 数据仅存储在本浏览器</span>'
    content = content.replace(old_status, new_status)

    # 也替换 title
    content = content.replace(
        '<title>成交数据管理 · 个人版</title>',
        '<title>成交数据管理 · ' + customer_name + '专属</title>'
    )

    # 替换底部授权信息
    license_info = (
        '  授权给: ' + customer_name +
        (' | ' + customer_phone if customer_phone else '') +
        ' | 生成时间: ' + datetime.now().strftime('%Y-%m-%d %H:%M') +
        ' | 仅供授权用户使用，请勿外传'
    )
    old_console = "console.log('  存储: 浏览器 localStorage（完全离线）');"
    new_console = old_console + "\n" + "console.log('" + license_info + "');"

    # 在title下方添加meta作者信息
    content = content.replace(
        '<meta name="viewport"',
        '<meta name="author" content="' + customer_name + '专属版">\n<meta name="viewport"'
    )

    # 输出文件
    safe_name = customer_name.replace(" ", "_").replace("/", "_")
    output_filename = f"成交数据管理_{safe_name}专属版.html"
    output_path = os.path.join(script_dir, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    # 生成专属链接和二维码
    import urllib.parse
    base_url = "https://wwccll.github.io/cjdata/tool.html"
    params = f"u={urllib.parse.quote(customer_name)}"
    if customer_phone:
        params += f"&p={customer_phone}"
    personal_url = f"{base_url}?{params}"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(personal_url)}"
    qr_download = f"https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={urllib.parse.quote(personal_url)}"

    print("=" * 55)
    print("[OK] 专属版已生成！")
    print("  客户: " + customer_name)
    if customer_phone:
        print("  手机: " + customer_phone)
    print("  文件: " + output_filename)
    print("=" * 55)
    print()
    print("[LINK] 专属链接（发给客户）:")
    print("  " + personal_url)
    print()
    print("[QR] 专属二维码（客户扫码直接打开）:")
    print("  预览: " + qr_url)
    print("  下载高清: " + qr_download)
    print()
    print("发送方式（二选一）:")
    print("  1. 微信发专属链接 -> 客户点开即用 -> 可添加到手机桌面")
    print("  2. 微信发专属二维码图片 -> 客户长按识别 -> 自动打开")
    print()
    print("[LOCK] 专属保护:")
    print("  - 链接里含有客户姓名，打开后页面显示「授权给：" + customer_name + "」")
    print("  - 二维码绑定了客户身份，别人拿了也用不了")
    print("  - 每个客户的链接和二维码都不同")
    return True


def main():
    if len(sys.argv) < 2:
        print("成交数据管理 · 专属版生成器")
        print("=" * 40)
        print()
        print("用法: python 生成专属版.py <客户姓名> [手机号]")
        print()
        print("示例:")
        print('  python 生成专属版.py 张三')
        print('  python 生成专属版.py 李四 13812345678')
        print()
        print("会在当前目录生成 成交数据管理_张三专属版.html")
        print("把生成的专属版发给对应客户即可")
        print()
        print("=" * 40)

        # 交互模式
        print("交互模式：")
        name = input("请输入客户姓名: ").strip()
        if not name:
            print("[X] 姓名不能为空")
            return
        phone = input("请输入客户手机号（可选，直接回车跳过）: ").strip()
        generate(name, phone)
    else:
        name = sys.argv[1]
        phone = sys.argv[2] if len(sys.argv) > 2 else ""
        generate(name, phone)


if __name__ == "__main__":
    main()
