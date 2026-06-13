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
SOURCE_FILE = "成交数据管理_个人版.html"  # 源文件

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
    old_header = 'h1>成交数据管理 <span style="font-size:.6rem;opacity:.7">个人版 v3.1</span></h1>'
    new_header = (
        'h1>成交数据管理 '
        '<span style="font-size:.6rem;opacity:.7">'
        '授权给：' + customer_name +
        (' ' + customer_phone if customer_phone else '') +
        '</span></h1>'
    )

    if old_header not in content:
        print("[X] 源文件中找不到标题占位符，请检查源文件版本")
        return False

    content = content.replace(old_header, new_header)

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

    print("=" * 50)
    print("[OK] 专属版已生成！")
    print("  客户: " + customer_name)
    if customer_phone:
        print("  手机: " + customer_phone)
    print("  文件: " + output_filename)
    print("  路径: " + output_path)
    print("=" * 50)
    print()
    print("发送方式:")
    print("  1. 微信电脑版 → 拖拽文件到聊天框 → 发送")
    print("  2. 右键文件 → 压缩为zip → 发zip（防止被微信改后缀）")
    print()
    print("提醒客户: 收到后用浏览器打开，不要微信内直接点开")
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
