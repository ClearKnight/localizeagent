import os
import json
import shutil
from datetime import datetime

class CapCutManager:
    def __init__(self):
        # 剪映 Mac 版默认草稿路径
        self.base_path = os.path.expanduser("~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/")
        
    def get_all_drafts(self):
        """获取所有草稿并按修改时间排序"""
        if not os.path.exists(self.base_path):
            print(f"❌ 未找到剪映草稿目录: {self.base_path}")
            return []
            
        drafts = []
        for d in os.listdir(self.base_path):
            path = os.path.join(self.base_path, d)
            if os.path.isdir(path):
                mtime = os.path.getmtime(path)
                drafts.append({
                    "name": d,
                    "path": path,
                    "updated_at": datetime.fromtimestamp(mtime)
                })
        
        # 按时间降序排列
        return sorted(drafts, key=lambda x: x["updated_at"], reverse=True)

    def get_latest_draft(self):
        """获取最近编辑的草稿"""
        drafts = self.get_all_drafts()
        return drafts[0] if drafts else None

    def read_draft_content(self, draft_path):
        """读取草稿的 JSON 内容（支持新旧版本结构，并尝试处理加密情况）"""
        # 1. 尝试读取 Timelines/project.json (新版)
        project_path = os.path.join(draft_path, "Timelines", "project.json")
        if os.path.exists(project_path):
            with open(project_path, "r", encoding="utf-8") as f:
                project_data = json.load(f)
                
            # 获取所有 timeline 的 content
            all_contents = []
            for timeline in project_data.get("timelines", []):
                timeline_id = timeline.get("id")
                
                # 尝试多个可能的文件名
                possible_files = [
                    os.path.join(draft_path, "Timelines", timeline_id, "draft_content.json"),
                    os.path.join(draft_path, "Timelines", timeline_id, "template.tmp"),
                    os.path.join(draft_path, "Timelines", timeline_id, "template-2.tmp")
                ]
                
                for p in possible_files:
                    if os.path.exists(p):
                        try:
                            with open(p, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                if isinstance(data, dict) and "materials" in data:
                                    all_contents.append(data)
                                    break # 找到一个有效的就跳出
                        except:
                            continue # 加密或格式不对，尝试下一个
            
            # 如果有多个 timeline，目前只返回第一个作为主要内容
            return all_contents[0] if all_contents else None
                
        # 2. 备选查找根目录下的 draft_content.json (旧版)
        content_path = os.path.join(draft_path, "draft_content.json")
        if os.path.exists(content_path):
            try:
                with open(content_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                print("⚠️ 发现加密的 draft_content.json，当前版本暂不支持直接解密。")
                return None
            
        return None

    def extract_texts(self, content):
        """从 JSON 中提取文本素材 (支持 materials.texts 结构)"""
        if not content:
            return []
            
        texts = []
        # 剪映的文本素材存放在 materials.texts 列表中
        materials = content.get("materials", {})
        for text_item in materials.get("texts", []):
            texts.append({
                "id": text_item.get("id"),
                "content": text_item.get("content")  # 这通常是富文本格式
            })
        return texts

    def inject_subtitles(self, draft_path, srt_items):
        """
        核心注入逻辑：将 SRT 内容注入剪映草稿
        """
        print(f"🛠️ 开始注入字幕到: {draft_path}")
        
        # 1. 定位内容文件
        target_file = None
        project_path = os.path.join(draft_path, "Timelines", "project.json")
        
        if os.path.exists(project_path):
            with open(project_path, "r", encoding="utf-8") as f:
                project_data = json.load(f)
            for timeline in project_data.get("timelines", []):
                timeline_id = timeline.get("id")
                possible_paths = [
                    os.path.join(draft_path, "Timelines", timeline_id, "draft_content.json"),
                    os.path.join(draft_path, "Timelines", timeline_id, "template.tmp")
                ]
                for p in possible_paths:
                    if os.path.exists(p):
                        target_file = p
                        break
                if target_file: break
        
        if not target_file:
            # 尝试根目录
            root_content = os.path.join(draft_path, "draft_content.json")
            if os.path.exists(root_content):
                target_file = root_content

        if not target_file:
            print("❌ 错误：未找到可注入的内容文件。")
            return False

        # 2. 备份
        backup_file = target_file + ".bak"
        shutil.copy2(target_file, backup_file)
        print(f"📦 已备份原始文件到: {os.path.basename(backup_file)}")

        # 3. 读取并修改
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 获取所有文本素材
            texts = data.get("materials", {}).get("texts", [])
            if not texts:
                print("⚠️ 警告：项目中没有预设的文本轨道，请先在剪映中手动添加一段占位字幕。")
                return False

            # 4. 匹配并替换
            # 这里采用最简单的策略：按顺序替换存在的文本框
            # 进阶策略：根据时间戳匹配（待后续迭代）
            print(f"📝 正在替换 {min(len(texts), len(srt_items))} 条字幕内容...")
            
            for i in range(min(len(texts), len(srt_items))):
                # 剪映的 content 是富文本格式，包含 <size>, <color> 等标签
                # 我们采用正则保留标签，仅替换纯文字内容
                old_content = texts[i]["content"]
                new_text = srt_items[i]["text"]
                
                # 简单的替换逻辑（如果原内容是简单的文本）
                # 注意：剪映的 content 结构较复杂，这里先尝试直接替换核心文本部分
                import re
                # 匹配 [content] 标签内的内容，或者直接替换整个 content（如果不是富文本）
                if "<" in old_content and ">" in old_content:
                    # 尝试保留富文本标签，只替换文字
                    # 这是一个简化的正则，实际可能更复杂
                    texts[i]["content"] = re.sub(r'(?<=<.*?>)([^<>]+?)(?=<.*?>)', new_text, old_content)
                else:
                    texts[i]["content"] = new_text

            # 5. 保存回文件
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            
            print(f"✅ 成功！请重新打开剪映项目查看效果。")
            return True

        except Exception as e:
            print(f"❌ 注入过程中发生错误: {str(e)}")
            # 还原备份
            shutil.copy2(backup_file, target_file)
            return False

if __name__ == "__main__":
    manager = CapCutManager()
    latest = manager.get_latest_draft()
    
    if latest:
        print(f"📂 发现最近草稿: {latest['name']}")
        print(f"🕒 更新时间: {latest['updated_at']}")
        
        content = manager.read_draft_content(latest['path'])
        texts = manager.extract_texts(content)
        
        if not texts:
            print("⚠️ 警告：在该草稿中未找到任何文本素材。")
            print(f"   JSON 顶层键: {list(content.keys()) if content else 'None'}")
            if content and "materials" in content:
                print(f"   Materials 键: {list(content['materials'].keys())}")
        else:
            print(f"📝 提取到 {len(texts)} 条文本素材:")
            for t in texts[:5]:  # 只显示前 5 条
                print(f"   - ID: {t['id'][:8]}... | 内容: {t['content'][:100]}...")
    else:
        print("📭 未发现任何草稿。")
