import os
import time
import re
import ssl  # 引入 ssl 模块
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, START, END, MessagesState
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from deep_translator import MyMemoryTranslator

# 1. 定义状态
class GraphState(MessagesState):
    video_id: str
    raw_transcript: List[Dict]  # 存储带时间戳的原始数据
    translated_transcript: List[Dict] # 存储带时间戳的译文数据

# 2. 工具函数：秒转 SRT 时间格式 (00:00:00,000)
def format_time(seconds: float) -> str:
    td_hours = int(seconds // 3600)
    td_mins = int((seconds % 3600) // 60)
    td_secs = int(seconds % 60)
    td_msecs = int((seconds - int(seconds)) * 1000)
    return f"{td_hours:02d}:{td_mins:02d}:{td_secs:02d},{td_msecs:03d}"

# 3. 定义节点逻辑
def fetch_subtitle_node(state: GraphState):
    """抓取结构化字幕数据 (配置代理并增加重试)"""
    video_id = state.get("video_id") or state["messages"][-1].content
    print(f"\n[1/2] 正在通过代理 (7897) 抓取视频 {video_id} 的原始字幕数据...")
    
    # 1. 强力修复：全局设置代理环境变量
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'
    
    # 2. 跳过 SSL 验证
    ssl._create_default_https_context = ssl._create_unverified_context
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 修正：实例化 YouTubeTranscriptApi 后再调用 list
            transcript_list = YouTubeTranscriptApi().list(video_id)
            transcript = transcript_list.find_transcript(['en', 'zh', 'id'])
            data = transcript.fetch()
            print(f"✅ 抓取成功！共 {len(data)} 条字幕轴。")
            
            return {
                "raw_transcript": data,
                "video_id": video_id,
                "messages": [SystemMessage(content=f"获取到 {len(data)} 条字幕轴")]
            }
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ 尝试 {attempt + 1} 失败，正在重试... ({str(e)})")
                time.sleep(2) # 等待 2 秒再试
            else:
                print(f"❌ 抓取彻底失败: {str(e)}")
                return {"messages": [AIMessage(content=f"抓取失败: {str(e)}")]}

def translate_to_srt_node(state: GraphState):
    """逐行清洗并翻译，保持时间轴不变"""
    raw_data = state.get("raw_transcript", [])
    if not raw_data:
        return {"messages": [AIMessage(content="无字幕数据")]}
    
    print(f"\n[2/2] 开始 SRT 逐行翻译（MyMemory 引擎）...")
    translated_data = []
    translator = MyMemoryTranslator(source='english', target='indonesian')
    
    start_time_total = time.time()
    
    # 为了防止 API 频繁请求被封，我们每 10 条字幕合并成一个小块进行翻译
    batch_size = 10 
    for i in range(0, len(raw_data), batch_size):
        batch = raw_data[i : i + batch_size]
        print(f"   - 正在处理第 {i+1}~{min(i+batch_size, len(raw_data))} 条...", end="", flush=True)
        
        for entry in batch:
            # 修正：使用属性访问而不是字典索引
            original_text = entry.text
            
            # 1. 清洗：移除音乐符号和方括号注释
            clean_text = original_text.replace("♪", "")
            clean_text = re.sub(r'\[.*?\]', '', clean_text).strip()
            
            if not clean_text:
                translated_text = ""
            else:
                try:
                    # 2. 翻译
                    translated_text = translator.translate(clean_text)
                except:
                    translated_text = clean_text # 失败则保留原文
            
            # 3. 重新封装
            translated_data.append({
                'start': entry.start,
                'end': entry.start + entry.duration,
                'text': translated_text
            })
            
        print(" ✅")
        # 适当微休，防止 API 限制
        time.sleep(0.5)

    elapsed_time = time.time() - start_time_total
    print(f"✅ SRT 翻译完成！总耗时: {elapsed_time:.2f} 秒")
    
    return {
        "translated_transcript": translated_data,
        "messages": [AIMessage(content="SRT 数据处理完成")]
    }

# 4. 构建工作流
workflow = StateGraph(GraphState)
workflow.add_node("fetch", fetch_subtitle_node)
workflow.add_node("translate", translate_to_srt_node)
workflow.add_edge(START, "fetch")
workflow.add_edge("fetch", "translate")
workflow.add_edge("translate", END)
app = workflow.compile()

# 5. 运行并生成 SRT 文件
if __name__ == "__main__":
    test_video_id = "dQw4w9WgXcQ"
    print(f"--- 启动 SRT 自动化翻译项目 ---")
    
    inputs = {"messages": [HumanMessage(content=test_video_id)], "video_id": test_video_id}
    
    final_state = app.invoke(inputs)
    srt_items = final_state.get("translated_transcript", [])
    
    if srt_items:
        srt_filename = f"subtitle_{test_video_id}.srt"
        with open(srt_filename, "w", encoding="utf-8") as f:
            for idx, item in enumerate(srt_items, start=1):
                f.write(f"{idx}\n")
                f.write(f"{format_time(item['start'])} --> {format_time(item['end'])}\n")
                f.write(f"{item['text']}\n\n")
        
        print(f"\n🎉 恭喜！SRT 文件已生成: {srt_filename}")
        print(f"您可以直接将此文件导入剪映、PR 或 Final Cut Pro 使用。")
