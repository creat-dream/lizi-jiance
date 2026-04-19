"""
大模型API客户端 - 支持通义千问等国内大模型
"""
import requests
import json
from typing import Dict, Any, Optional


class LLMClient:
    """大模型API客户端"""
    
    def __init__(self, api_key: str, api_url: str, model: str = "qwen-turbo"):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        
    def parse_coa_report(self, pdf_text: str) -> Optional[Dict[str, Any]]:
        """
        解析COA报告文本
        
        Args:
            pdf_text: 从PDF提取的文本内容
            
        Returns:
            解析后的结构化数据
        """
        prompt = self._build_prompt(pdf_text)
        
        try:
            response = self._call_api(prompt)
            return self._parse_response(response)
        except Exception as e:
            print(f"API调用失败: {e}")
            return None
    
    def _build_prompt(self, pdf_text: str) -> str:
        """构建Prompt模板"""
        return f"""你是一个专业的COA（Certificate of Analysis）检测报告解析助手。

请从以下PDF文本中提取关键信息，并以JSON格式返回：

需要提取的字段：
1. coa_no: COA编号
2. lot_no: 材料批号（LOT No.）
3. customer: 顾客名称
4. brand: 材料牌号
5. delivery_date: 发货日期
6. test_items: 检测项目数组，每个项目包含：
   - name: 项目名称（中文）
   - name_en: 项目名称（英文）
   - unit: 单位
   - standard: 执行标准
   - condition: 测试条件
   - specification: 技术指标（保持原文，如"≥18"）
   - result: 检测结果（转换为数值，如18.6）
   - conclusion: 结论（合格/不合格）

注意：
- 如果某项信息缺失，使用空字符串或null
- result字段必须是数值类型，如果原文是"REPORT"或无法转换，设为null
- 只返回JSON格式数据，不要其他说明

PDF文本内容：
{pdf_text}

请只返回JSON格式数据，不要其他说明。"""

    def _call_api(self, prompt: str) -> str:
        """调用大模型API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "result_format": "message",
                "max_tokens": 2000,
                "temperature": 0.1
            }
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        return response.text
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """解析API响应"""
        try:
            data = json.loads(response_text)
            # 通义千问的响应格式
            if "output" in data and "choices" in data["output"]:
                content = data["output"]["choices"][0]["message"]["content"]
                # 提取JSON部分
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = content.strip()
                return json.loads(json_str)
            return data
        except Exception as e:
            print(f"解析响应失败: {e}")
            print(f"原始响应: {response_text}")
            raise
