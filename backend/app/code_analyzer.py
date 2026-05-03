import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

class CodeAnalyzer:
    """
    代码分析器，使用AST分析Python代码的调用关系
    """
    
    def __init__(self):
        # 存储所有节点信息
        self.nodes: Dict[str, Dict[str, Any]] = {}
        # 存储所有边（调用关系）
        self.edges: List[Dict[str, Any]] = []
        # 用于跟踪当前处理的文件和作用域
        self.current_file: str = ""
        self.current_scope: List[str] = []
        # 用于跟踪导入的模块和函数
        self.imports: Dict[str, str] = {}
        # 用于跟踪所有定义的名称
        self.all_defined_names: Dict[str, str] = {}
    
    def analyze_directory(self, directory: Path, max_depth: int = 5) -> Dict[str, Any]:
        """
        分析目录下的所有.py文件
        """
        self.nodes.clear()
        self.edges.clear()
        self.imports.clear()
        self.all_defined_names.clear()
        
        # 首先收集所有文件，建立全局名称映射
        all_py_files = self._collect_python_files(directory, max_depth)
        
        # 第一遍扫描：收集所有定义的名称
        for file_path in all_py_files:
            self._scan_file_for_definitions(file_path)
        
        # 第二遍扫描：分析调用关系
        for file_path in all_py_files:
            self._analyze_file(file_path)
        
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }
    
    def _collect_python_files(self, directory: Path, max_depth: int) -> List[Path]:
        """
        收集目录下所有的.py文件
        """
        py_files = []
        
        def _scan_dir(current_dir: Path, depth: int):
            if depth > max_depth:
                return
            
            for item in current_dir.iterdir():
                if item.is_file() and item.suffix == ".py":
                    py_files.append(item)
                elif item.is_dir() and not item.name.startswith(".") and item.name != "__pycache__":
                    _scan_dir(item, depth + 1)
        
        _scan_dir(directory, 0)
        return py_files
    
    def _scan_file_for_definitions(self, file_path: Path):
        """
        扫描文件中的所有定义，建立全局名称映射
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            module_name = file_path.stem
            file_key = str(file_path.absolute())
            
            # 添加模块节点
            module_id = f"module_{file_key}"
            self.all_defined_names[module_name] = module_id
            self.all_defined_names[file_path.stem] = module_id
            
            # 分析模块中的定义
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    class_id = f"class_{file_key}_{class_name}"
                    self.all_defined_names[class_name] = class_id
                    
                    # 分析类中的方法
                    for body_node in node.body:
                        if isinstance(body_node, ast.FunctionDef):
                            method_name = body_node.name
                            method_id = f"method_{file_key}_{class_name}_{method_name}"
                            self.all_defined_names[f"{class_name}.{method_name}"] = method_id
                
                elif isinstance(node, ast.FunctionDef):
                    # 检查是否是模块级别的函数
                    is_module_level = False
                    for parent in ast.iter_child_nodes(tree):
                        if parent is node:
                            is_module_level = True
                            break
                    
                    if is_module_level:
                        func_name = node.name
                        func_id = f"function_{file_key}_{func_name}"
                        self.all_defined_names[func_name] = func_id
        
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
    
    def _analyze_file(self, file_path: Path):
        """
        分析单个文件
        """
        self.current_file = str(file_path.absolute())
        self.current_scope = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            module_name = file_path.stem
            file_key = self.current_file
            
            # 添加模块节点
            module_id = f"module_{file_key}"
            self.nodes[module_id] = {
                "name": module_name,
                "type": "module",
                "file_path": self.current_file,
                "line_number": 1,
                "docstring": ast.get_docstring(tree) or ""
            }
            
            # 分析导入
            self._analyze_imports(tree, file_key)
            
            # 分析类和函数定义
            self._analyze_module_body(tree, module_id, file_key)
        
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
    
    def _analyze_imports(self, tree: ast.Module, file_key: str):
        """
        分析文件中的导入语句
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    as_name = alias.asname or module_name
                    # 检查是否在全局定义中
                    if module_name in self.all_defined_names:
                        self.imports[as_name] = self.all_defined_names[module_name]
                    # 也可能导入的是模块中的成员，需要处理
            
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module
                for alias in node.names:
                    name = alias.name
                    as_name = alias.asname or name
                    # 检查是否在全局定义中
                    # 可能是模块名.函数名的形式
                    full_name = f"{module_name}.{name}" if module_name else name
                    if name in self.all_defined_names:
                        self.imports[as_name] = self.all_defined_names[name]
                    elif full_name in self.all_defined_names:
                        self.imports[as_name] = self.all_defined_names[full_name]
    
    def _analyze_module_body(self, tree: ast.Module, parent_id: str, file_key: str):
        """
        分析模块主体
        """
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                self._analyze_class(node, parent_id, file_key)
            elif isinstance(node, ast.FunctionDef):
                self._analyze_function(node, parent_id, file_key, is_method=False)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                # 模块级别的调用
                self._analyze_call(node.value, parent_id, file_key)
    
    def _analyze_class(self, node: ast.ClassDef, parent_id: str, file_key: str):
        """
        分析类定义
        """
        class_name = node.name
        class_id = f"class_{file_key}_{class_name}"
        
        # 获取文档字符串
        docstring = ast.get_docstring(node) or ""
        
        # 添加类节点
        self.nodes[class_id] = {
            "name": class_name,
            "type": "class",
            "file_path": self.current_file,
            "line_number": node.lineno,
            "docstring": docstring
        }
        
        # 添加从父节点到类的边
        self.edges.append({
            "source": parent_id,
            "target": class_id,
            "type": "contains"
        })
        
        # 分析基类
        for base in node.bases:
            self._analyze_base_class(base, class_id, file_key)
        
        # 分析类体
        self.current_scope.append(class_name)
        for body_node in node.body:
            if isinstance(body_node, ast.FunctionDef):
                self._analyze_function(body_node, class_id, file_key, is_method=True)
            elif isinstance(body_node, ast.Expr) and isinstance(body_node.value, ast.Call):
                self._analyze_call(body_node.value, class_id, file_key)
        self.current_scope.pop()
    
    def _analyze_base_class(self, base: ast.expr, class_id: str, file_key: str):
        """
        分析基类引用
        """
        # 提取基类名称
        base_name = self._extract_name_from_expr(base)
        if base_name:
            # 检查是否是导入的名称
            if base_name in self.imports:
                target_id = self.imports[base_name]
                self.edges.append({
                    "source": class_id,
                    "target": target_id,
                    "type": "inherits"
                })
            elif base_name in self.all_defined_names:
                target_id = self.all_defined_names[base_name]
                self.edges.append({
                    "source": class_id,
                    "target": target_id,
                    "type": "inherits"
                })
    
    def _analyze_function(self, node: ast.FunctionDef, parent_id: str, file_key: str, is_method: bool):
        """
        分析函数定义
        """
        func_name = node.name
        node_type = "method" if is_method else "function"
        
        if is_method:
            class_name = self.current_scope[-1]
            func_id = f"method_{file_key}_{class_name}_{func_name}"
        else:
            func_id = f"function_{file_key}_{func_name}"
        
        # 获取文档字符串
        docstring = ast.get_docstring(node) or ""
        
        # 添加函数节点
        self.nodes[func_id] = {
            "name": func_name,
            "type": node_type,
            "file_path": self.current_file,
            "line_number": node.lineno,
            "docstring": docstring
        }
        
        # 添加从父节点到函数的边
        self.edges.append({
            "source": parent_id,
            "target": func_id,
            "type": "contains"
        })
        
        # 分析函数体中的调用
        self.current_scope.append(func_name)
        self._analyze_function_body(node, func_id, file_key)
        self.current_scope.pop()
    
    def _analyze_function_body(self, node: ast.FunctionDef, func_id: str, file_key: str):
        """
        分析函数体中的调用
        """
        for body_node in ast.walk(node):
            if isinstance(body_node, ast.Call):
                self._analyze_call(body_node, func_id, file_key)
    
    def _analyze_call(self, call_node: ast.Call, caller_id: str, file_key: str):
        """
        分析函数调用
        """
        # 提取被调用的函数名称
        func_name = self._extract_name_from_expr(call_node.func)
        
        if func_name:
            # 检查是否是导入的名称
            if func_name in self.imports:
                target_id = self.imports[func_name]
                self.edges.append({
                    "source": caller_id,
                    "target": target_id,
                    "type": "calls"
                })
            elif func_name in self.all_defined_names:
                target_id = self.all_defined_names[func_name]
                self.edges.append({
                    "source": caller_id,
                    "target": target_id,
                    "type": "calls"
                })
    
    def _extract_name_from_expr(self, expr: ast.expr) -> Optional[str]:
        """
        从表达式中提取名称
        """
        if isinstance(expr, ast.Name):
            return expr.id
        elif isinstance(expr, ast.Attribute):
            # 处理类似 obj.method 的调用
            attr_name = expr.attr
            # 尝试获取对象名
            if isinstance(expr.value, ast.Name):
                obj_name = expr.value.id
                # 检查是否是导入的模块
                if obj_name in self.imports:
                    # 可能是模块中的函数
                    full_name = f"{obj_name}.{attr_name}"
                    if full_name in self.all_defined_names:
                        return full_name
                return attr_name
            return attr_name
        elif isinstance(expr, ast.Call):
            # 嵌套调用，提取外层
            return self._extract_name_from_expr(expr.func)
        return None
    
    def get_analysis_result(self) -> Dict[str, Any]:
        """
        获取分析结果
        """
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }
