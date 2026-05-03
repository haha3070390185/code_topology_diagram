import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from code_analyzer import CodeAnalyzer

app = FastAPI(title="代码逻辑拓扑图工具", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisResult(BaseModel):
    nodes: List[Dict[str, Any]]
    lines: List[Dict[str, Any]]
    categories: List[Dict[str, Any]]

@app.get("/")
def read_root():
    return {"message": "代码逻辑拓扑图工具API", "version": "1.0.0"}

@app.get("/scan", response_model=AnalysisResult)
def scan_directory(
    path: str = Query(..., description="要扫描的目录路径"),
    max_depth: Optional[int] = Query(5, description="最大扫描深度", ge=1, le=20)
):
    """
    扫描指定目录下的.py文件，分析代码调用关系
    """
    # 验证路径是否存在
    directory = Path(path)
    if not directory.exists():
        raise HTTPException(status_code=404, detail=f"目录不存在: {path}")
    
    if not directory.is_dir():
        raise HTTPException(status_code=400, detail=f"路径不是目录: {path}")
    
    # 创建分析器并执行分析
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_directory(directory, max_depth=max_depth)
    
    # 转换为relation-graph需要的格式
    nodes = []
    lines = []
    categories = []
    
    # 生成节点
    for node_id, node_data in result["nodes"].items():
        node = {
            "id": node_id,
            "text": node_data["name"],
            "category": node_data["type"],
            "meta": {
                "file_path": node_data["file_path"],
                "line_number": node_data.get("line_number", 0),
                "type": node_data["type"],
                "docstring": node_data.get("docstring", "")
            }
        }
        nodes.append(node)
    
    # 生成边（调用关系）
    for edge in result["edges"]:
        line = {
            "from": edge["source"],
            "to": edge["target"],
            "text": edge["type"],
            "color": "#4a9eff"
        }
        lines.append(line)
    
    # 生成分类
    categories = [
        {"name": "模块", "type": "module", "color": "#67c23a"},
        {"name": "类", "type": "class", "color": "#409eff"},
        {"name": "函数", "type": "function", "color": "#e6a23c"},
        {"name": "方法", "type": "method", "color": "#f56c6c"}
    ]
    
    return AnalysisResult(nodes=nodes, lines=lines, categories=categories)

@app.get("/files")
def list_files(
    path: str = Query(..., description="要列出的目录路径"),
    extension: Optional[str] = Query(None, description="文件扩展名过滤，如：.py")
):
    """
    列出指定目录下的文件
    """
    directory = Path(path)
    if not directory.exists():
        raise HTTPException(status_code=404, detail=f"目录不存在: {path}")
    
    if not directory.is_dir():
        raise HTTPException(status_code=400, detail=f"路径不是目录: {path}")
    
    files = []
    for item in directory.iterdir():
        if item.is_file():
            if extension and item.suffix != extension:
                continue
            files.append({
                "name": item.name,
                "path": str(item.absolute()),
                "size": item.stat().st_size,
                "modified": item.stat().st_mtime
            })
    
    return {"files": files, "path": path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
