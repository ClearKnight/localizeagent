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
            "inject_capcut": True,
            "target_draft_path": None
        }

        print(f"🚀 [Agent] 开始处理视频: {video_id}")
        
        # 1. 运行翻译工作流
        print("\n--- 步骤 1: 翻译字幕 ---")
        inputs = {"messages": [HumanMessage(content=video_id)], "video_id": video_id}
        final_state = translation_app.invoke(inputs)
        
        # 优先使用润色后的字幕，如果没有则使用机翻
        srt_items = final_state.get("refined_transcript") or final_state.get("translated_transcript", [])
        
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
            print("\n--- 步骤 3: 自动导入剪映 ---")
            
            target_draft_path = options.get("target_draft_path")
            
            if target_draft_path:
                # 方案 A: 自动注入 (针对已有字幕轨道的项目)
                success = self.capcut.inject_subtitles(target_draft_path, srt_items)
                
                # 方案 B: 素材夹同步 (将产物直接放入剪映项目的 Resources 目录，方便手动一键拖入)
                self._import_to_resources(target_draft_path, srt_path, voice_path)
                
                if success:
                    print(f"✨ 字幕已成功注入轨道！")
                else:
                    print(f"💡 注入轨道未完成（可能是空项目），但素材已放入项目文件夹，请在剪映中直接拖入。")
            else:
                print("📭 未选择任何剪映草稿，跳过导入。")

        print("\n🎉 [Agent] 任务完成！")
        return {
            "srt": srt_path,
            "voice": voice_path
        }

    def _import_to_resources(self, draft_path, srt_path, voice_path):
        """将生成的素材物理复制到剪映项目的 Resources 目录"""
        try:
            res_dir = os.path.join(draft_path, "Resources")
            if not os.path.exists(res_dir):
                os.makedirs(res_dir)
            
            # 复制 SRT
            dest_srt = os.path.join(res_dir, os.path.basename(srt_path))
            import shutil
            shutil.copy2(srt_path, dest_srt)
            
            # 复制 MP3
            if voice_path:
                dest_voice = os.path.join(res_dir, os.path.basename(voice_path))
                shutil.copy2(voice_path, dest_voice)
            
            print(f"📂 素材已物理同步至剪映资源库: {os.path.basename(draft_path)}/Resources/")
        except Exception as e:
            print(f"⚠️ 素材同步失败: {e}")
