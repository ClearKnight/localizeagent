import asyncio
import sys
import os

# 将当前目录加入路径，方便导入 core 和 tools
sys.path.append(os.path.dirname(__file__))

from core.agent import VideoLocalizeAgent

async def main():
    # ---------------------------------------------------------
    # API 配置 (建议使用 DeepSeek 或 GPT-4o-mini)
    # 你也可以在终端运行: export LLM_API_KEY="your_key"
    # ---------------------------------------------------------
    # os.environ["LLM_API_KEY"] = "sk-xxxxxxxxxxxx" 
    # os.environ["LLM_BASE_URL"] = "https://api.deepseek.com" # 或 https://api.openai.com/v1
    # os.environ["LLM_MODEL"] = "deepseek-chat" # 或 gpt-4o-mini
    # ---------------------------------------------------------

    # 使用示例
    video_id = sys.argv[1] if len(sys.argv) > 1 else "dQw4w9WgXcQ"
    
    agent = VideoLocalizeAgent()
    await agent.run(video_id)

if __name__ == "__main__":
    asyncio.run(main())
