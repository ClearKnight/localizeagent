import asyncio
import sys
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 将当前目录加入路径，方便导入 core 和 tools
sys.path.append(os.path.dirname(__file__))

from core.agent import VideoLocalizeAgent

async def main():
    # 加载 .env 文件中的环境变量
    load_dotenv()
    
    # 1. 输入视频 ID
    video_id = sys.argv[1] if len(sys.argv) > 1 else input("📺 请输入 YouTube 视频 ID (默认 dQw4w9WgXcQ): ") or "dQw4w9WgXcQ"
    
    agent = VideoLocalizeAgent()
    
    # 2. 选择剪映项目
    print("\n🔍 正在扫描剪映草稿...")
    drafts = agent.capcut.get_all_drafts()
    if not drafts:
        print("📭 未发现剪映草稿。")
        target_draft_path = None
    else:
        print("\n--- 请选择目标剪映项目 ---")
        for i, d in enumerate(drafts[:10]): # 只列出最近 10 个
            print(f"[{i}] {d['name']} (更新于: {d['updated_at'].strftime('%m-%d %H:%M')})")
        
        choice = input(f"\n请输入序号 (0-{min(len(drafts)-1, 9)}, 默认 0, 输入 n 跳过): ")
        if choice.lower() == 'n':
            target_draft_path = None
        else:
            try:
                idx = int(choice) if choice else 0
                target_draft_path = drafts[idx]['path']
                print(f"✅ 已选择: {drafts[idx]['name']}")
            except:
                target_draft_path = drafts[0]['path']
                print(f"⚠️ 输入无效，默认选择最近草稿: {drafts[0]['name']}")

    # 3. 运行 Agent
    await agent.run(video_id, options={
        "generate_srt": True,
        "generate_voice": True,
        "inject_capcut": True,
        "target_draft_path": target_draft_path
    })

if __name__ == "__main__":
    asyncio.run(main())
