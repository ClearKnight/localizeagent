import os
from typing import Dict, List
from langchain_core.messages import HumanMessage
from core.workflow import app as translation_app, format_time
from tools.voiceover import VoiceOverManager
from tools.capcut import CapCutManager

class VideoLocalizeAgent:
    def __init__(self, output_dir="output"):
        self.capcut = CapCutManager()
        self.voiceover = VoiceOverManager()
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    async def run(self, video_id: str, options: Dict = None):
        """执行完整的本地化流程"""
        options = options or {
            "generate_srt": True,
            "generate_voice": True,
            "inject_capcut": True
        }

        print(f"🚀 [Agent] 开始处理视频: {video_id}")
        
        # 1. 运行翻译工作流
        print("\n--- 步骤 1: 翻译字幕 ---")
        inputs = {"messages": [HumanMessage(content=video_id)], "video_id": video_id}
        final_state = translation_app.invoke(inputs)
        srt_items = final_state.get("translated_transcript", [])
        
        if not srt_items:
            print("❌ 翻译失败，流程终止。")
            return

        # 2. 生成 SRT 文件
        srt_path = os.path.join(self.output_dir, f"subtitle_{video_id}.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            for idx, item in enumerate(srt_items, start=1):
                f.write(f"{idx}\n")
                f.write(f"{format_time(item['start'])} --> {format_time(item['end'])}\n")
                f.write(f"{item['text']}\n\n")
        print(f"✅ SRT 文件已生成: {srt_path}")

        # 3. 生成配音 (可选)
        voice_path = None
        if options.get("generate_voice"):
            print("\n--- 步骤 2: 生成印尼语配音 ---")
            full_text = " ".join([item['text'] for item in srt_items if item['text']])
            voice_path = os.path.join(self.output_dir, f"voice_{video_id}.mp3")
            await self.voiceover.text_to_speech(full_text, voice_path)
            print(f"✅ 配音文件已生成: {voice_path}")

        # 4. 寻找剪映草稿
        if options.get("inject_capcut"):
            print("\n--- 步骤 3: 检查剪映草稿 ---")
            latest = self.capcut.get_latest_draft()
            if latest:
                print(f"📂 发现最近草稿: {latest['name']}")
                content = self.capcut.read_draft_content(latest['path'])
                if content:
                    texts = self.capcut.extract_texts(content)
                    print(f"📝 提取到 {len(texts)} 条文本素材。")
                else:
                    print("⚠️ 无法读取草稿内容（可能已加密或格式不支持）。")
                    print(f"💡 请手动将 {srt_path} 导入剪映。")
            else:
                print("📭 未发现任何剪映草稿。")

        print("\n🎉 [Agent] 任务完成！")
        return {
            "srt": srt_path,
            "voice": voice_path
        }
