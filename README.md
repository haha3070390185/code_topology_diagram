# 代码逻辑拓扑图工具

一个用于可视化Python项目代码调用关系的本地工具。

## 功能特性

- **自动扫描**: 自动扫描指定目录下的所有Python文件
- **智能分析**: 使用Python AST库深度分析代码结构和调用关系
- **可视化展示**: 基于relation-graph库的交互式关系图
- **深色主题**: 专业深色背景，低亮度护眼
- **流动动画**: 连线带有流畅的流动动画效果，直观展示调用方向
- **类型区分**: 支持模块、类、函数、方法四种代码元素类型
- **节点详情**: 点击节点查看详细信息（文件路径、行号、文档字符串等）

## 技术栈

### 后端
- **框架**: FastAPI
- **核心库**: ast (Python标准库)
- **服务器**: Uvicorn

### 前端
- **框架**: Vue 3 (Composition API)
- **样式**: TailwindCSS
- **关系图**: relation-graph
- **HTTP客户端**: Axios

## 项目结构

```
code_topology_diagram/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI主入口
│   │   └── code_analyzer.py   # AST代码分析器
│   ├── requirements.txt       # Python依赖
│   └── run.py                 # 启动脚本
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/
│   │   │   └── CodeTopology.vue  # 主组件
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── test_project/               # 测试用例项目
│   ├── main.py
│   ├── module_a.py
│   └── module_b.py
├── start_backend.bat          # Windows后端启动脚本
├── start_frontend.bat         # Windows前端启动脚本
└── README.md
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+ (建议使用LTS版本)

### 步骤1: 启动后端服务

**方式一: 使用启动脚本 (Windows)**
```bash
# 双击运行 start_backend.bat
# 或者在命令行执行
start_backend.bat
```

**方式二: 手动启动**
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务 (开发模式，带热重载)
python run.py
# 或者
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动

> API文档地址: http://localhost:8000/docs

### 步骤2: 启动前端服务

**方式一: 使用启动脚本 (Windows)**
```bash
# 双击运行 start_frontend.bat
# 或者在命令行执行
start_frontend.bat
```

**方式二: 手动启动**
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:3000 启动

### 步骤3: 使用工具

1. 打开浏览器访问 http://localhost:3000
2. 在输入框中输入要分析的Python项目目录路径
   - 例如可以使用项目中的测试目录: `g:\Trea_Coding_\code_topology_diagram\test_project`
3. 点击「开始分析」按钮
4. 等待分析完成，拓扑图将自动渲染
5. 点击节点查看详细信息
6. 使用右上角的按钮可以缩放视图或重置视图

## 功能说明

### 节点类型

工具识别并显示四种代码元素类型:

| 类型 | 图标 | 颜色 | 说明 |
|------|------|------|------|
| 模块 | 📁 | 绿色 (#67c23a) | Python文件 (.py) |
| 类 | 🏷️ | 蓝色 (#409eff) | class定义 |
| 函数 | ⚡ | 橙色 (#e6a23c) | 模块级别的def |
| 方法 | 🔧 | 红色 (#f56c6c) | 类中的def |

### 关系类型

- **包含 (contains)**: 模块包含类和函数，类包含方法
- **调用 (calls)**: 函数/方法调用其他函数/方法
- **继承 (inherits)**: 类继承关系

### 交互功能

- **缩放**: 鼠标滚轮缩放视图
- **拖拽**: 按住鼠标左键拖拽背景移动视图
- **节点详情**: 点击任意节点查看详细信息面板
- **节点移动**: 可以直接拖拽单个节点调整位置
- **工具栏**: 右上角按钮支持重置视图、放大、缩小

## 后端API说明

### GET /scan
扫描并分析指定目录的Python代码

**参数:**
- `path` (string, required): 要分析的目录绝对路径
- `max_depth` (int, optional): 最大扫描深度，默认5，范围1-20

**响应:**
```json
{
  "nodes": [
    {
      "id": "module_xxx",
      "text": "模块名",
      "category": "module",
      "meta": {
        "file_path": "文件路径",
        "line_number": 1,
        "type": "module",
        "docstring": "文档字符串"
      }
    }
  ],
  "lines": [
    {
      "from": "源节点ID",
      "to": "目标节点ID",
      "text": "关系类型",
      "color": "#4a9eff"
    }
  ],
  "categories": [
    {"name": "模块", "type": "module", "color": "#67c23a"}
  ]
}
```

### GET /files
列出指定目录下的文件

**参数:**
- `path` (string, required): 目录路径
- `extension` (string, optional): 文件扩展名过滤

### GET /
健康检查接口

## 设计特点

### 深色主题
- 主背景: `#0f172a` (深蓝灰)
- 卡片背景: `#1e293b`
- 边框颜色: `#334155`
- 文字颜色: `#e2e8f0` (浅色文字)

### 流动动画
连线使用CSS动画实现流动效果:
- 虚线样式: `stroke-dasharray: 6, 6`
- 动画周期: 1.5秒
- 无限循环

## 测试

项目包含一个测试用例目录 `test_project`，可以用于验证工具功能:

- **module_a.py**: 包含一个函数和一个基础类
- **module_b.py**: 导入并使用module_a，包含派生类
- **main.py**: 主入口，调用所有模块

这个测试用例涵盖了:
- 跨模块导入和调用
- 类继承关系
- 方法内部调用
- 文档字符串

## 注意事项

1. **路径格式**: Windows系统请使用绝对路径，例如 `C:\Users\Project` 或 `g:\Trea_Coding_\code_topology_diagram\test_project`

2. **权限问题**: 确保对要分析的目录有读取权限

3. **大项目**: 对于非常大的Python项目（超过1000个文件），分析可能需要较长时间

4. **语法要求**: 被分析的Python代码必须是语法正确的，否则AST解析会失败

5. **动态代码**: 动态导入 (`__import__`) 和运行时生成的代码可能无法被正确分析

## 开发说明

### 后端开发
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 开发模式启动
python run.py
```

### 前端开发
```bash
cd frontend

# 安装依赖
npm install

# 开发模式 (热重载)
npm run dev

# 构建生产版本
npm run build
```

## License

MIT
