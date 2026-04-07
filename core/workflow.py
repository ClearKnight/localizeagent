import os
import time
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from tools.youtube import YouTubeFetcher
from tools.translator import SubtitleTranslator
from tools.refiner import TranslationRefiner

# 1. 定义状态
class GraphState(MessagesState):
    video_id: str
    raw_transcript: List[Dict]  # 存储带时间戳的原始数据
    translated_transcript: List[Dict] # 存储带时间戳的机翻数据
    refined_transcript: List[Dict] # 存储带时间戳的微调后数据

# 2. 工具函数：秒转 SRT 时间格式 (00:00:00,000)
def format_time(seconds: float) -> str:
    td_hours = int(seconds // 3600)
    td_mins = int((seconds % 3600) // 60)
    td_secs = int(seconds % 60)
    td_msecs = int((seconds - int(seconds)) * 1000)
    return f"{td_hours:02d}:{td_mins:02d}:{td_secs:02d},{td_msecs:03d}"

# 3. 定义节点逻辑
def fetch_subtitle_node(state: GraphState):
    """抓取结构化字幕数据"""
    video_id = state.get("video_id") or state["messages"][-1].content
    print(f"\n[1/2] 正在抓取视频 {video_id} 的原始字幕数据...")
    
    fetcher = YouTubeFetcher()
    try:
        data = fetcher.fetch(video_id)
        print(f"✅ 抓取成功！共 {len(data)} 条字幕轴。")
        return {
            "raw_transcript": data,
            "video_id": video_id,
            "messages": [SystemMessage(content=f"获取到 {len(data)} 条字幕轴")]
        }
    except Exception as e:
        print(f"❌ 抓取彻底失败: {str(e)}")
        return {"messages": [AIMessage(content=f"抓取失败: {str(e)}")]}

def translate_to_srt_node(state: GraphState):
    """逐行清洗并翻译，保持时间轴不变"""
    raw_data = state.get("raw_transcript", [])
    if not raw_data:
        return {"messages": [AIMessage(content="无字幕数据")]}
    
    print(f"\n[2/2] 开始 SRT 逐行翻译（Google 引擎）...")
    translator = SubtitleTranslator(source='en', target='id')
    
    start_time_total = time.time()
    translated_data = translator.translate_batch(raw_data)

    elapsed_time = time.time() - start_time_total
    print(f"✅ SRT 翻译完成！总耗时: {elapsed_time:.2f} 秒")
    
    return {
        "translated_transcript": translated_data,
        "messages": [AIMessage(content="机翻完成")]
    }

def refine_translation_node(state: GraphState):
    """使用云端 LLM 对机翻结果进行微调和润色"""
    raw_data = state.get("raw_transcript", [])
    machine_data = state.get("translated_transcript", [])
    
    # 尝试从环境变量或配置中获取 Key
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("LLM_MODEL", "deepseek-chat")
    temperature = os.getenv("LLM_TEMPERATURE", 0.3)

    if not machine_data or not api_key:
        if not api_key:
            print("\n💡 提示: 未检测到 LLM_API_KEY，将跳过专家润色步骤，直接使用机翻结果。")
        return {"messages": [AIMessage(content="跳过润色")]}
    
    print(f"\n[3/3] 开始云端专家级微调 ({model}, temp={temperature})...")
    
    refiner = TranslationRefiner(api_key=api_key, base_url=base_url, model=model, temperature=temperature)
    
    # 提取原文和机翻结果
    orig_texts = []
    for e in raw_data:
        if isinstance(e, dict):
            orig_texts.append(e.get('text', ''))
        else:
            orig_texts.append(getattr(e, 'text', ''))
            
    machine_texts = [e['text'] for e in machine_data]
    
    start_time = time.time()
    # 这里的 refine_batch 内部是逐条请求 Ollama 的
    # 如果 Ollama 没开，它会瞬间返回机翻结果
    refined_texts = refiner.refine_batch(orig_texts, machine_texts)
    
    # 将润色后的文本重新组装
    refined_data = []
    for i, entry in enumerate(machine_data):
        refined_data.append({
            'start': entry['start'],
            'end': entry['end'],
            'text': refined_texts[i]
        })
        
    elapsed = time.time() - start_time
    print(f"✅ LLM 微调完成！耗时: {elapsed:.2f} 秒")
    
    return {
        "refined_transcript": refined_data,
        "messages": [AIMessage(content="字幕润色完成")]
    }

# 4. 构建工作流
def create_workflow():
    workflow = StateGraph(GraphState)
    workflow.add_node("fetch", fetch_subtitle_node)
    workflow.add_node("translate", translate_to_srt_node)
    workflow.add_node("refine", refine_translation_node)

    workflow.add_edge(START, "fetch")
    workflow.add_edge("fetch", "translate")
    workflow.add_edge("translate", "refine")
    workflow.add_edge("refine", END)
    return workflow.compile()

app = create_workflow()
