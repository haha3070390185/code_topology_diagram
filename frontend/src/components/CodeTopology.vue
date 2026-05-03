<template>
  <div class="code-topology-container">
    <div class="toolbar">
      <div class="toolbar-left">
        <input
          type="text"
          v-model="directoryPath"
          placeholder="输入要分析的文件夹路径（例如：g:\Trea_Coding_\code_topology_diagram\test_project）"
          class="path-input"
        />
        <button
          @click="analyzeDirectory"
          :disabled="analyzing"
          class="analyze-btn"
        >
          {{ analyzing ? '分析中...' : '开始分析' }}
        </button>
      </div>
      <div class="toolbar-right">
        <button
          @click="resetView"
          class="action-btn"
          title="重置视图"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
        <button
          @click="zoomIn"
          class="action-btn"
          title="放大"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
          </svg>
        </button>
        <button
          @click="zoomOut"
          class="action-btn"
          title="缩小"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
          </svg>
        </button>
      </div>
    </div>

    <div class="main-content">
      <div class="legend-panel">
        <h3 class="legend-title">图例</h3>
        <div class="legend-items">
          <div v-for="category in categories" :key="category.type" class="legend-item">
            <span
              class="legend-color"
              :style="{ backgroundColor: category.color }"
            ></span>
            <span class="legend-text">{{ category.name }}</span>
          </div>
          <div class="legend-item">
            <span class="legend-line"></span>
            <span class="legend-text">调用关系</span>
          </div>
        </div>
      </div>

      <div class="graph-container" ref="graphContainer">
        <RelationGraph
          ref="relationGraph"
          :options="graphOptions"
          class="relation-graph"
          @on-node-click="onNodeClick"
          @on-line-click="onLineClick"
        >
          <template #node="{ node, isHover }">
            <div
              class="custom-node"
              :class="[
                `node-${node.category || node.meta?.type || 'default'}`,
                { 'node-hover': isHover },
                { 'node-selected': node.isSelected }
              ]"
            >
              <div class="node-icon">
                <span v-if="node.category === 'module' || node.meta?.type === 'module'">📁</span>
                <span v-else-if="node.category === 'class' || node.meta?.type === 'class'">🏷️</span>
                <span v-else-if="node.category === 'function' || node.meta?.type === 'function'">⚡</span>
                <span v-else-if="node.category === 'method' || node.meta?.type === 'method'">🔧</span>
                <span v-else>📄</span>
              </div>
              <div class="node-content">
                <div class="node-text">{{ node.text || node.name }}</div>
                <div class="node-meta" v-if="node.meta?.type || node.category">
                  {{ node.meta?.type || node.category }}
                </div>
              </div>
            </div>
          </template>
        </RelationGraph>

        <div v-if="!hasData" class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mb-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          <h3 class="text-xl font-medium text-gray-400 mb-2">暂无数据</h3>
          <p class="text-gray-500 text-center max-w-xs">
            请输入要分析的Python项目文件夹路径，然后点击"开始分析"按钮
          </p>
        </div>
      </div>

      <div
        v-if="selectedNode"
        class="detail-panel"
        :class="{ 'panel-open': selectedNode }"
      >
        <div class="detail-header">
          <h3 class="detail-title">节点详情</h3>
          <button @click="selectedNode = null" class="close-btn">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="detail-content">
          <div class="detail-item">
            <span class="detail-label">名称</span>
            <span class="detail-value">{{ selectedNode.text || selectedNode.name }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">类型</span>
            <span
              class="detail-value type-badge"
              :style="{ backgroundColor: getCategoryColor(selectedNode.category || selectedNode.meta?.type) }"
            >
              {{ getCategoryName(selectedNode.category || selectedNode.meta?.type) }}
            </span>
          </div>
          <div v-if="selectedNode.meta?.line_number" class="detail-item">
            <span class="detail-label">行号</span>
            <span class="detail-value">{{ selectedNode.meta.line_number }}</span>
          </div>
          <div v-if="selectedNode.meta?.file_path" class="detail-item">
            <span class="detail-label">文件路径</span>
            <span class="detail-value file-path">{{ selectedNode.meta.file_path }}</span>
          </div>
          <div v-if="selectedNode.meta?.docstring" class="detail-item">
            <span class="detail-label">文档字符串</span>
            <pre class="detail-value docstring">{{ selectedNode.meta.docstring }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import RelationGraph from 'relation-graph/vue3'

import axios from 'axios'

const directoryPath = ref('')
const analyzing = ref(false)
const selectedNode = ref(null)
const graphContainer = ref(null)
const relationGraph = ref(null)
const hasData = ref(false)

const categories = ref([
  { name: '模块', type: 'module', color: '#67c23a' },
  { name: '类', type: 'class', color: '#409eff' },
  { name: '函数', type: 'function', color: '#e6a23c' },
  { name: '方法', type: 'method', color: '#f56c6c' }
])

const graphOptions = ref({
  debug: false,
  defaultFocusRootNode: false,
  defaultExpandLevel: -1,
  layouts: [
    {
      label: '力导向布局',
      layoutName: 'force',
      layoutClassName: 'seeks-layout-force',
      maxNodeCount: 500,
      isDefault: true
    },
    {
      label: '中心布局',
      layoutName: 'center',
      layoutClassName: 'seeks-layout-center',
      maxNodeCount: 500
    },
    {
      label: '树状布局',
      layoutName: 'tree',
      layoutClassName: 'seeks-layout-tree',
      maxNodeCount: 500
    }
  ],
  defaultNodeShape: 1,
  defaultNodeWidth: 160,
  defaultNodeHeight: 60,
  nodePadding: 30,
  lineWidth: 2,
  lineColor: '#4a9eff',
  lineShape: 1,
  showZoomTool: false,
  showNodeTool: false,
  showGraphTool: false,
  allowShowLocateRelationLink: true,
  distanceCoef: 1.2,
  minScale: 0.1,
  maxScale: 5,
  moveToCenterWhenRefresh: false,
  zoomToFitWhenRefresh: false,
  useAnimationWhenRefresh: true
})

const getCategoryColor = (type) => {
  const category = categories.value.find(c => c.type === type)
  return category ? category.color : '#888'
}

const getCategoryName = (type) => {
  const category = categories.value.find(c => c.type === type)
  return category ? category.name : type
}

const analyzeDirectory = async () => {
  if (!directoryPath.value.trim()) {
    alert('请输入要分析的文件夹路径')
    return
  }

  analyzing.value = true
  hasData.value = false

  try {
    console.log('请求路径:', directoryPath.value)
    
    const response = await axios.get('/api/scan', {
      params: {
        path: directoryPath.value,
        max_depth: 5
      }
    })

    const result = response.data
    console.log('API响应:', result)

    if (result.nodes && result.nodes.length > 0) {
      const nodes = result.nodes.map(node => ({
        ...node,
        color: getCategoryColor(node.category),
        borderColor: getCategoryColor(node.category)
      }))

      const lines = result.lines

      let rootId = null
      const nodeIds = new Set(nodes.map(n => n.id))
      const lineTargets = new Set(lines.map(l => l.to))
      
      for (const node of nodes) {
        if (!lineTargets.has(node.id)) {
          rootId = node.id
          break
        }
      }
      
      if (!rootId && nodes.length > 0) {
        rootId = nodes[0].id
      }

      const graphData = {
        rootId: rootId,
        nodes: nodes,
        lines: lines
      }

      console.log('设置图表数据:', graphData)

      await nextTick()
      
      if (relationGraph.value) {
        relationGraph.value.setJsonData(graphData, (graphInstance) => {
          console.log('图表加载完成')
          hasData.value = true
          
          try {
            graphInstance.zoomToFit()
          } catch (e) {
            console.log('缩放适配失败:', e)
          }
        })
      }
    } else {
      alert('未找到可分析的Python代码，请检查路径是否正确')
    }
  } catch (error) {
    console.error('分析失败:', error)
    let errorMsg = '未知错误'
    if (error.response) {
      errorMsg = error.response.data?.detail || `HTTP错误: ${error.response.status}`
    } else if (error.message) {
      errorMsg = error.message
    }
    alert(`分析失败: ${errorMsg}\n\n请确保:\n1. 后端服务已启动 (http://localhost:8000)\n2. 路径是正确的绝对路径\n3. 文件夹包含Python文件`)
  } finally {
    analyzing.value = false
  }
}

const onNodeClick = (nodeObject, event) => {
  console.log('节点点击:', nodeObject)
  selectedNode.value = nodeObject
}

const onLineClick = (lineObject, event) => {
  console.log('连线点击:', lineObject)
}

const resetView = () => {
  if (relationGraph.value) {
    try {
      const graphInstance = relationGraph.value.getInstance()
      if (graphInstance && graphInstance.resetZoom) {
        graphInstance.resetZoom()
      } else if (graphInstance && graphInstance.zoomToFit) {
        graphInstance.zoomToFit()
      }
    } catch (e) {
      console.log('重置视图失败:', e)
    }
  }
}

const zoomIn = () => {
  if (relationGraph.value) {
    try {
      const graphInstance = relationGraph.value.getInstance()
      if (graphInstance) {
        const scale = graphInstance.scale || 1
        graphInstance.scale = scale * 1.2
        graphInstance.refresh()
      }
    } catch (e) {
      console.log('放大失败:', e)
    }
  }
}

const zoomOut = () => {
  if (relationGraph.value) {
    try {
      const graphInstance = relationGraph.value.getInstance()
      if (graphInstance) {
        const scale = graphInstance.scale || 1
        graphInstance.scale = scale * 0.8
        graphInstance.refresh()
      }
    } catch (e) {
      console.log('缩小失败:', e)
    }
  }
}

onMounted(() => {
  console.log('组件已挂载, relation-graph版本:', RelationGraph)
})
</script>

<style scoped>
.code-topology-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #0f172a;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #1e293b;
  border-bottom: 1px solid #334155;
  gap: 16px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  max-width: 900px;
}

.path-input {
  flex: 1;
  min-width: 200px;
  padding: 10px 14px;
  border: 1px solid #334155;
  border-radius: 8px;
  background-color: #0f172a;
  color: #e2e8f0;
  font-size: 14px;
  transition: all 0.2s ease;
  font-family: 'Consolas', 'Monaco', monospace;
}

.path-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.path-input::placeholder {
  color: #64748b;
}

.analyze-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.analyze-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background-color: #334155;
  color: #94a3b8;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: #475569;
  color: #e2e8f0;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.legend-panel {
  width: 180px;
  background-color: #1e293b;
  border-right: 1px solid #334155;
  padding: 16px;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.legend-title {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 16px;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-color {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  flex-shrink: 0;
}

.legend-line {
  width: 20px;
  height: 2px;
  background: repeating-linear-gradient(
    90deg,
    #4a9eff 0,
    #4a9eff 8px,
    transparent 8px,
    transparent 12px
  );
  animation: dash-flow 1.5s linear infinite;
}

.legend-text {
  font-size: 13px;
  color: #94a3b8;
}

.graph-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background-color: #0f172a;
}

.relation-graph {
  width: 100%;
  height: 100%;
}

.custom-node {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background-color: #1e293b;
  border: 2px solid #334155;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 150px;
  box-sizing: border-box;
}

.custom-node.node-hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
}

.custom-node.node-selected {
  box-shadow: 0 0 25px rgba(59, 130, 246, 0.6);
  border-color: #3b82f6;
}

.custom-node.node-module,
.custom-node.node-module {
  border-color: #67c23a;
}

.custom-node.node-class,
.custom-node.node-class {
  border-color: #409eff;
}

.custom-node.node-function,
.custom-node.node-function {
  border-color: #e6a23c;
}

.custom-node.node-method,
.custom-node.node-method {
  border-color: #f56c6c;
}

.node-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.node-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.node-text {
  font-size: 13px;
  font-weight: 500;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-meta {
  font-size: 11px;
  color: #64748b;
  text-transform: capitalize;
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  z-index: 10;
  pointer-events: none;
}

.detail-panel {
  width: 0;
  overflow: hidden;
  background-color: #1e293b;
  border-left: 1px solid #334155;
  transition: width 0.3s ease;
  flex-shrink: 0;
}

.detail-panel.panel-open {
  width: 300px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #334155;
}

.detail-title {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background-color: transparent;
  color: #94a3b8;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: #334155;
  color: #e2e8f0;
}

.detail-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  max-height: calc(100% - 50px);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.detail-value {
  font-size: 13px;
  color: #e2e8f0;
  word-break: break-all;
}

.type-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  width: fit-content;
}

.file-path {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  background-color: #0f172a;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #334155;
}

.docstring {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  background-color: #0f172a;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #334155;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

@keyframes dash-flow {
  to {
    stroke-dashoffset: -24;
  }
}

:deep(.seeks-bg) {
  fill: #0f172a !important;
}

:deep(.seeks-line-inner) {
  stroke: #4a9eff !important;
  stroke-dasharray: 6, 6;
  animation: dash-flow 1.5s linear infinite;
}

:deep(.seeks-node-selected-circle) {
  fill: transparent;
  stroke: #3b82f6;
  stroke-width: 2;
  stroke-dasharray: 5, 5;
  animation: dash-flow 1s linear infinite;
}

:deep(.seeks-line-text) {
  fill: #94a3b8 !important;
  font-size: 12px;
}
</style>
