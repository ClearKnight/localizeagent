import json
import requests
import time
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

class TranslationRefiner:
    def __init__(self, api_key=None, base_url="https://api.deepseek.com", model="deepseek-chat", temperature=0.3):
        """
        使用云端 LLM (兼容 OpenAI 格式) 对机翻结果进行微调和润色
        推荐: DeepSeek-V3, GPT-4o-mini
        """
        self.api_key = api_key
        self.base_url = f"{base_url.rstrip('/')}/chat/completions"
        self.model = model
        self.temperature = float(temperature)

    def refine_single(self, orig: str, machine: str) -> str:
        """单条润色逻辑"""
        if not self.api_key:
            return machine # 无 Key 则回退
            
        if not orig.strip():
            return ""

        prompt = f"""You are a professional subtitle reviewer for English-Indonesian video localization.
Task: Refine the provided [Google Machine Translation] based on the [Original English].

Guidelines:
1. Fix grammatical errors and unnatural phrasing in Indonesian.
2. Ensure the tone matches the video context (usually natural and conversational).
3. Keep it concise for subtitle display (avoid overly long lines).
4. If the machine translation is already perfect, keep it as is.

[Original English]: {orig}
[Google Machine Translation]: {machine}

Output ONLY the refined [Indonesian Translation] without any explanation.
Refined:"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "stream": False
            }
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                refined_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                return refined_text.replace('"', '').replace('「', '').replace('」', '')
            return machine
        except:
            return machine

    def refine_batch(self, original_texts: List[str], machine_translations: List[str], max_workers: int = 5) -> List[str]:
        """并行润色，并针对免费 API 进行频率限制控制"""
        if not self.api_key:
            print("⚠️ 未配置 API Key，将跳过 LLM 润色步骤。")
            return machine_translations

        total = len(original_texts)
        refined_results = [None] * total
        
        # 如果是 Gemini 免费层级 (15 RPM)，我们降低并发并增加间隔
        is_free_tier = "gemini" in self.base_url.lower() or "free" in self.model.lower()
        if is_free_tier:
            print("   ℹ️ 检测到可能是免费 API，启用频率保护模式 (15 RPM)...")
            max_workers = 1 # 免费层级建议单线程以防封禁
        
        print(f"   🚀 云端并行润色中 (并发: {max_workers})...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(self.refine_single, orig, machine): i 
                for i, (orig, machine) in enumerate(zip(original_texts, machine_translations))
            }
            
            completed = 0
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                refined_results[index] = future.result()
                completed += 1
                
                # 针对免费 API 增加强制间隔
                if is_free_tier and completed < total:
                    time.sleep(4) # 60s / 15RPM = 4s/req
                
                percent = (completed / total) * 100
                print(f"\r   润色进度: [{'#' * int(percent // 5)}{'.' * (20 - int(percent // 5))}] {percent:.1f}% ({completed}/{total})", end="", flush=True)
        
        print("\n")
        return refined_results
