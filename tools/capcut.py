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
