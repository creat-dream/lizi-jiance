"""
PDF解析模块 - 提取PDF文本并调用大模型解析
"""
import fitz  # PyMuPDF
import os
from typing import Dict, Any, Optional
from .llm_client import LLMClient


class PDFParser:
    """PDF解析器"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        
    def extract_text(self, pdf_path: str) -> str:
        """
        从PDF文件中提取文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            提取的文本内容
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            raise Exception(f"PDF解析失败: {e}")
        
        return text
    
    def parse_pdf(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        解析PDF文件，提取结构化数据
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            解析后的结构化数据，包含文件路径信息
        """
        # 提取文本
        text = self.extract_text(pdf_path)
        
        if not text.strip():
            print(f"警告: PDF文件内容为空 - {pdf_path}")
            return None
        
        # 调用大模型解析
        result = self.llm_client.parse_coa_report(text)
        
        if result:
            # 添加文件路径信息
            result["file_path"] = pdf_path
            result["file_name"] = os.path.basename(pdf_path)
            
            # 验证结果
            if self.validate_result(result):
                return result
            else:
                print(f"解析结果验证失败: {pdf_path}")
                return None
        
        return None
    
    def validate_result(self, data: Dict[str, Any]) -> bool:
        """
        验证解析结果的完整性
        
        Args:
            data: 解析结果数据
            
        Returns:
            是否通过验证
        """
        # 检查必要字段
        required_fields = ["coa_no", "lot_no", "test_items"]
        for field in required_fields:
            if field not in data or not data[field]:
                print(f"缺少必要字段: {field}")
                return False
        
        # 检查检测项目
        if not isinstance(data["test_items"], list) or len(data["test_items"]) == 0:
            print("检测项目为空或格式错误")
            return False
        
        # 检查每个检测项目
        for item in data["test_items"]:
            if "name" not in item or not item["name"]:
                print("检测项目缺少名称")
                return False
        
        return True
    
    def parse_multiple_pdfs(self, pdf_paths: list) -> list:
        """
        批量解析多个PDF文件
        
        Args:
            pdf_paths: PDF文件路径列表
            
        Returns:
            解析结果列表
        """
        results = []
        for path in pdf_paths:
            print(f"正在解析: {path}")
            result = self.parse_pdf(path)
            if result:
                results.append(result)
                print(f"解析成功: {result.get('lot_no', 'Unknown')}")
            else:
                print(f"解析失败: {path}")
        
        return results
