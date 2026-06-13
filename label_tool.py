#!/usr/bin/env python3
"""
AI 数据标注效率工具 —— 键盘驱动，批量处理，一键导出
适用平台：阿里众包、百度众包、腾讯搜活帮 等
"""

import sys
import os

# Windows GBK 终端 UTF-8 兼容
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")

import json
import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# ============================================================
# 配置区 —— 根据实际任务类型修改
# ============================================================

# 预置标注模板（键盘快捷键 → 标签）
TEMPLATES = {
    "sentiment": {  # 情感分类
        "1": "正面",
        "2": "负面",
        "3": "中性",
    },
    "intent": {  # 意图判断
        "1": "咨询",
        "2": "投诉",
        "3": "闲聊",
        "4": "购买意向",
    },
    "quality": {  # 内容质量
        "1": "高质量",
        "2": "中等",
        "3": "低质量",
        "4": "垃圾/广告",
    },
    "custom": {},  # 自定义（运行时设置）
}

HISTORY_FILE = "label_history.json"


class LabelTool:
    """数据标注效率工具"""

    def __init__(self):
        self.template = None
        self.labels = {}
        self.data = []          # 待标注数据
        self.results = []       # 标注结果
        self.current_idx = 0
        self.start_time = None
        self.total_labeled = 0
        self.history = self._load_history()

    # ---------- 数据加载 ----------

    def load_data(self, filepath):
        """从文件加载待标注数据（支持 txt, csv, json）"""
        path = Path(filepath)
        if not path.exists():
            print(f"[X] 文件不存在: {filepath}")
            return False

        suffix = path.suffix.lower()
        if suffix == ".txt":
            with open(path, "r", encoding="utf-8") as f:
                self.data = [line.strip() for line in f if line.strip()]
        elif suffix == ".csv":
            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
        elif suffix == ".json":
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                self.data = loaded if isinstance(loaded, list) else [loaded]
        else:
            print(f"[X] 不支持的格式: {suffix}")
            return False

        print(f"[OK] 已加载 {len(self.data)} 条数据")
        return True

    # ---------- 模板管理 ----------

    def set_template(self, name):
        """设置标注模板"""
        if name in TEMPLATES:
            self.template = name
            self.labels = dict(TEMPLATES[name])
            print(f"[*] 当前模板: {name}")
            self._show_labels()
        else:
            print(f"[X] 模板不存在，可用模板: {list(TEMPLATES.keys())}")

    def set_custom_labels(self, label_dict):
        """设置自定义标签"""
        TEMPLATES["custom"] = label_dict
        self.set_template("custom")

    def _show_labels(self):
        """显示当前快捷键映射"""
        print(" " + "-" * 30)
        for key, label in self.labels.items():
            print(f"   [{key}] → {label}")
        print(" " + "-" * 30)

    # ---------- 核心标注流程 ----------

    def start_labeling(self):
        """开始交互式标注"""
        if not self.data:
            print("[X] 请先加载数据: load <文件路径>")
            return

        if not self.template:
            print("[i]  未设置模板，使用默认情感分类模板")
            self.set_template("sentiment")

        self.start_time = time.time()
        self.current_idx = 0
        self.total_labeled = 0

        print(f"\n[START] 开始标注！共 {len(self.data)} 条")
        print(f"   快捷键: 1-{len(self.labels)} 选择标签 | S 跳过 | Q 退出并保存")
        print(f"   {'='*50}\n")

        while self.current_idx < len(self.data):
            item = self.data[self.current_idx]
            self._show_item(item)

            key = self._get_key()
            if key is None:
                break  # 退出
            if key == "SKIP":
                self.current_idx += 1
                continue
            if key in self.labels:
                result = self._build_result(item, self.labels[key])
                self.results.append(result)
                self.total_labeled += 1
                self.current_idx += 1
                # 进度提示
                if self.total_labeled % 50 == 0:
                    elapsed = time.time() - self.start_time
                    speed = self.total_labeled / elapsed * 60
                    remaining = (len(self.data) - self.current_idx) / speed if speed > 0 else 0
                    print(f"   [STATS] 已标注 {self.total_labeled}/{len(self.data)} | "
                          f"速度 {speed:.0f}条/分 | 预计剩余 {remaining:.0f}分")

        self._finish()

    def _show_item(self, item):
        """显示当前待标注条目"""
        if isinstance(item, dict):
            # 尝试常见字段名
            text = item.get("text") or item.get("content") or item.get("句子") or str(item)
        else:
            text = str(item)

        # 截断过长文本
        display = text[:120] + "..." if len(text) > 120 else text
        print(f"\n[>>] [{self.current_idx + 1}/{len(self.data)}] {display}")

    def _get_key(self):
        """获取用户按键"""
        while True:
            try:
                key = input("   [TAG]  选择标签 (1-{}): ".format(len(self.labels))).strip().lower()
                if key == "q":
                    return None
                if key == "s" or key == "":
                    return "SKIP"
                if key in self.labels:
                    return key
                print(f"   [WARN]  无效按键，请按 1-{len(self.labels)}，S 跳过，Q 退出")
            except (KeyboardInterrupt, EOFError):
                return None

    def _build_result(self, item, label):
        """构建标注结果"""
        if isinstance(item, dict):
            result = dict(item)
            result["label"] = label
            result["labeled_at"] = datetime.now().isoformat()
            return result
        else:
            return {
                "id": self.current_idx + 1,
                "text": str(item),
                "label": label,
                "labeled_at": datetime.now().isoformat(),
            }

    def _finish(self):
        """完成标注，输出统计"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"\n{'='*50}")
        print(f"[OK] 标注完成！")
        print(f"   已标注: {self.total_labeled} 条")
        print(f"   耗时: {elapsed/60:.1f} 分钟")
        if elapsed > 0:
            print(f"   速度: {self.total_labeled / elapsed * 60:.0f} 条/分钟")
        self._show_distribution()
        self._auto_save()

    def _show_distribution(self):
        """显示标签分布"""
        if not self.results:
            return
        dist = {}
        for r in self.results:
            label = r["label"]
            dist[label] = dist.get(label, 0) + 1
        print(f"\n[STATS] 标签分布:")
        for label, count in sorted(dist.items(), key=lambda x: -x[1]):
            pct = count / len(self.results) * 100
            bar = "█" * int(pct / 5)
            print(f"   {label}: {count}条 ({pct:.1f}%) {bar}")

    # ---------- 导出 ----------

    def export(self, filepath=None, fmt=None):
        """导出标注结果"""
        if not self.results:
            print("[X] 没有标注结果可导出")
            return

        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"标注结果_{timestamp}.csv"

        path = Path(filepath)
        suffix = path.suffix.lower() if fmt is None else f".{fmt}"

        if suffix == ".csv":
            self._export_csv(path)
        elif suffix == ".json":
            self._export_json(path)
        elif suffix == ".jsonl":
            self._export_jsonl(path)
        else:
            # 默认CSV
            path = path.with_suffix(".csv")
            self._export_csv(path)

        print(f"[SAVED] 已导出: {path}")

    def _export_csv(self, path):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            if self.results:
                writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                writer.writeheader()
                writer.writerows(self.results)

    def _export_json(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def _export_jsonl(self, path):
        with open(path, "w", encoding="utf-8") as f:
            for r in self.results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    def _auto_save(self):
        """自动保存历史"""
        self.history.append({
            "time": datetime.now().isoformat(),
            "template": self.template,
            "total": self.total_labeled,
            "file": str(getattr(self, "current_file", "unknown")),
        })
        self._save_history()
        # 自动导出
        self.export()

    # ---------- 历史记录 ----------

    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history[-100:], f, ensure_ascii=False, indent=2)

    def show_history(self):
        """显示历史标注记录"""
        if not self.history:
            print("[--] 暂无历史记录")
            return
        print("\n[HIST] 标注历史:")
        for h in self.history[-20:]:
            print(f"   {h['time'][:16]} | {h['template']} | {h['total']}条")

    # ---------- 批量处理（进阶） ----------

    def batch_classify(self, filepath, keywords_map):
        """
        批量关键词匹配分类
        keywords_map: {"正面": ["好","棒","赞"], "负面": ["差","烂","坑"]}
        """
        if not self.data:
            self.load_data(filepath)
            if not self.data:
                return

        for item in self.data:
            text = item.get("text", str(item)) if isinstance(item, dict) else str(item)
            matched = None
            for label, keywords in keywords_map.items():
                if any(kw in text for kw in keywords):
                    matched = label
                    break
            if matched:
                self.results.append(self._build_result(item, matched))

        print(f"[OK] 批量匹配完成: {len(self.results)}/{len(self.data)} 条已分类")
        self._show_distribution()
        self.export()


# ============================================================
# 交互命令行界面
# ============================================================

def print_banner():
    print(r"""
+======================================+
|[AI] AI 数据标注效率工具 v1.0      ║
|   键盘驱动 . 批量处理 . 一键导出     |
+======================================+
    """)

def print_help():
    print("""
[*] 命令列表:
   load <文件路径>      - 加载待标注数据（txt/csv/json）
   template <模板名>    - 切换标注模板
   templates            - 查看所有可用模板
   custom <标签配置>    - 设置自定义标签（JSON格式）
   start                - 开始交互式标注
   export [文件名]      - 导出标注结果
   stats                - 查看统计
   history              - 查看历史记录
   batch <文件> <规则>  - 关键词批量分类（JSON规则文件）
   help                 - 显示帮助
   quit                 - 退出

⚡ 标注快捷键:
   1/2/3/4...  → 选择对应标签
   S           → 跳过当前条目
   Q           → 退出标注并保存

[>>] 快速开始示例:
   > load test_data.txt
   > template sentiment
   > start
   然后按 1/2/3 快速标注，按 Q 保存退出
    """)


def interactive_mode():
    """交互式命令行模式"""
    print_banner()
    print_help()

    tool = LabelTool()

    while True:
        try:
            cmd = input("\n>> > ").strip()
            if not cmd:
                continue

            parts = cmd.split(maxsplit=1)
            action = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if action == "quit" or action == "exit" or action == "q":
                if tool.results:
                    ans = input("[WARN]  还有未导出的结果，要保存吗？(y/n): ").strip().lower()
                    if ans == "y":
                        tool.export()
                print("[BYE] 再见！")
                break

            elif action == "load":
                if arg:
                    tool.current_file = arg
                    tool.load_data(arg)

            elif action == "template" or action == "t":
                if arg:
                    tool.set_template(arg)
                else:
                    print("用法: template <模板名>")

            elif action == "templates":
                print("\n[*] 可用模板:")
                for name, labels in TEMPLATES.items():
                    if labels:
                        print(f"   {name}: {list(labels.values())}")

            elif action == "custom":
                try:
                    labels = json.loads(arg)
                    tool.set_custom_labels(labels)
                except json.JSONDecodeError:
                    print("[X] JSON格式错误，例如: {\"1\":\"正面\",\"2\":\"负面\"}")

            elif action == "start" or action == "go":
                tool.start_labeling()

            elif action == "export":
                tool.export(arg if arg else None)

            elif action == "stats":
                if tool.results:
                    print(f"\n[STATS] 当前批次: {len(tool.results)} 条已标注")
                    tool._show_distribution()
                else:
                    print("[--] 当前批次无标注结果")

            elif action == "history":
                tool.show_history()

            elif action == "batch":
                batch_parts = arg.split(maxsplit=1)
                if len(batch_parts) >= 2:
                    try:
                        rules = json.loads(batch_parts[1])
                        tool.batch_classify(batch_parts[0], rules)
                    except json.JSONDecodeError:
                        print("[X] 规则JSON格式错误")

            elif action == "help" or action == "h":
                print_help()

            elif action == "demo":
                # 快速演示
                run_demo()

            else:
                print(f"[X] 未知命令: {action}，输入 help 查看帮助")

        except (KeyboardInterrupt, EOFError):
            print("\n[BYE] 再见！")
            break


def run_demo():
    """快速演示：生成示例数据并开始标注"""
    print("[DEMO] 生成演示数据...")

    demo_data = [
        "这个小区环境真的很好，绿化率高，物业负责",
        "房子漏水严重，开发商一直不处理",
        "今天天气不错",
        "请问这个户型还有吗？价格多少？",
        "你们的服务太差了，我要投诉",
        "感谢中介小哥的热心服务，很满意",
        "周边配套怎么样，有学校和医院吗",
        "垃圾广告，不要发了",
        "首付大概需要多少？能贷款吗",
        "我考虑一下，过几天回复",
        "阳台朝南，采光非常好，装修也不错",
        "地铁站离得太远了，交通不方便",
        "在吗？",
        "能不能便宜点，预算有限",
        "已经买了，谢谢",
        "这小区的隔音效果太差了，楼上一走动就听得见",
        "满五唯一吗？税费多少",
        "明天上午可以看房吗",
        "帮你推荐一下客户，我朋友也在找房",
        "不喜欢这个户型，有没有南北通透的",
    ]

    path = "demo_data.txt"
    with open(path, "w", encoding="utf-8") as f:
        for line in demo_data:
            f.write(line + "\n")

    # 设置房产相关标签
    TEMPLATES["realestate"] = {
        "1": "正面评价",
        "2": "负面评价",
        "3": "咨询需求",
        "4": "投诉",
        "5": "其他/闲聊",
    }

    tool = LabelTool()
    tool.current_file = path
    tool.load_data(path)
    tool.set_template("realestate")
    tool.start_labeling()


if __name__ == "__main__":
    # 如果有命令行参数，作为文件路径直接加载
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        template = sys.argv[2] if len(sys.argv) > 2 else "sentiment"

        tool = LabelTool()
        tool.current_file = filepath
        if tool.load_data(filepath):
            tool.set_template(template)
            tool.start_labeling()
    else:
        interactive_mode()
