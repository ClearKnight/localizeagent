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
    # 使用示例
    video_id = sys.argv[1] if len(sys.argv) > 1 else "dQw4w9WgXcQ"
    
    agent = VideoLocalizeAgent()
    await agent.run(video_id)

if __name__ == "__main__":
    asyncio.run(main())
