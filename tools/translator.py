import re
import time
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator

class SubtitleTranslator:
    def __init__(self, source='en', target='id'):
        self.translator = GoogleTranslator(source=source, target=target)

    def clean_text(self, text: str) -> str:
        """清洗字幕文本：移除音乐符号和方括号内容"""
        text = text.replace("♪", "")
        text = re.sub(r'\[.*?\]', '', text).strip()
        return text

    def translate_single(self, entry) -> Dict:
        """单条翻译逻辑（供线程池调用）"""
        # 兼容字典和对象两种访问方式
        if isinstance(entry, dict):
            original_text = entry.get('text', '')
            start = entry.get('start', 0)
            duration = entry.get('duration', 0)
        else:
            # 如果是 FetchedTranscriptSnippet 对象
            original_text = getattr(entry, 'text', '')
            start = getattr(entry, 'start', 0)
            duration = getattr(entry, 'duration', 0)

        clean_text = self.clean_text(original_text)
        
        if not clean_text:
            translated_text = ""
        else:
            try:
                # MyMemoryTranslator 没有内置 timeout，但线程池会处理外部中断
                translated_text = self.translator.translate(clean_text)
            except Exception as e:
                # print(f"⚠️ 翻译出错: {e}")
                translated_text = clean_text # 失败保底
        
        return {
            'start': start,
            'end': start + duration,
            'text': translated_text
        }

    def translate_batch(self, raw_data: List[Dict], max_workers: int = 5) -> List[Dict]:
        """使用线程池并发翻译字幕，并实时显示进度"""
        total = len(raw_data)
        translated_data = [None] * total # 预分配空间以保持顺序
        
        print(f"   🚀 开启 {max_workers} 线程并行翻译中...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务，记录原始索引以便后续排序
            future_to_index = {
                executor.submit(self.translate_single, entry): i 
                for i, entry in enumerate(raw_data)
            }
            
            completed_count = 0
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    translated_data[index] = result
                except Exception as e:
                    print(f"\n❌ 索引 {index} 翻译严重错误: {e}")
                    # 极端失败保底
                    entry = raw_data[index]
                    translated_data[index] = {
                        'start': entry.get('start', 0) if isinstance(entry, dict) else getattr(entry, 'start', 0),
                        'end': (entry.get('start', 0) + entry.get('duration', 0)) if isinstance(entry, dict) else (getattr(entry, 'start', 0) + getattr(entry, 'duration', 0)),
                        'text': entry.get('text', '') if isinstance(entry, dict) else getattr(entry, 'text', '')
                    }
                
                completed_count += 1
                # 实时显示进度条效果
                percent = (completed_count / total) * 100
                print(f"\r   进度: [{'#' * int(percent // 5)}{'.' * (20 - int(percent // 5))}] {percent:.1f}% ({completed_count}/{total})", end="", flush=True)

        print("\n") # 换行
        return translated_data
