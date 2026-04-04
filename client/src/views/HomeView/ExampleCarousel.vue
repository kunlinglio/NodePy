<template>
  <div class="example-carousel">
    <div class="editor-mockup">
      <div class="mockup-header">
        <div class="window-controls">
          <span></span><span></span><span></span>
        </div>
        <div class="file-name">{{ currentName }}</div>
        <!-- <div class="mockup-actions">
          <div class="run-indicator"></div>
        </div> -->
      </div>
      <div class="mockup-body">
        <!-- 添加 transition 实现淡入淡出切换 -->
        <transition name="fade" mode="out-in">
          <VueFlow
            :key="currentExampleIndex"
            :nodes="currentNodes"
            :edges="currentEdges"
            :node-types="nodeTypes"
            :default-viewport="{ zoom: 0.5 }"
            :min-zoom="0.3"
            :max-zoom="1.5"
            fit-view-on-init
            class="demo-flow"
            id="demo"
          >
            <Background color="rgba(50, 50, 50, 0.05)" variant="dots" :gap="20" :size="4"/>
            <template #edge-NodePyEdge="NodePyEdgeProps">
              <NodePyEdge v-bind="NodePyEdgeProps"/>
            </template>
            <template #connection-line="ConnectionLineProps">
              <NodePyConnectionLine v-bind="ConnectionLineProps"/>
            </template>
          </VueFlow>
        </transition>
      </div>
      <!-- 进度条 -->
      <div class="carousel-progress">
        <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
      </div>
    </div>

    <!-- 圆点指示器：阻止事件冒泡，避免与 Home 拖拽冲突 -->
    <div class="carousel-indicators" @mousedown.stop @touchstart.stop>
      <span
        v-for="(_, index) in 4"
        :key="index"
        class="indicator-dot"
        :class="{ active: currentExampleIndex === index }"
        @click="switchExample(index)"
      ></span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, markRaw } from 'vue';
import { VueFlow, useVueFlow } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import '@vue-flow/core/dist/style.css';
import '@vue-flow/core/dist/theme-default.css';

import NodePyEdge from '@/components/NodePyEdge.vue';
import NodePyConnectionLine from '@/components/NodePyConnectionLine.vue';

// 导入所有节点组件
import ConstNode from '@/components/nodes/input/ConstNode.vue';
import NumberBinOpNode from '@/components/nodes/compute/NumberBinOpNode.vue';
import DateTimeNode from '@/components/nodes/input/DateTimeNode.vue';
import DatetimeComputeNode from '@/components/nodes/datetimeProcess/DatetimeComputeNode.vue';
import KlineNode from '@/components/nodes/input/KlineNode.vue';
import QuickPlotNode from '@/components/nodes/visualize/QuickPlotNode.vue';
import StatsNode from '@/components/nodes/analysis/StatsNode.vue';
import ToFloatNode from '@/components/nodes/compute/ToFloatNode.vue';
import ToIntNode from '@/components/nodes/compute/ToIntNode.vue';
import LinearRegressionNode from '@/components/nodes/machineLearning/LinearRegressionNode.vue';
import RegressionScoreNode from '@/components/nodes/machineLearning/RegressionScoreNode.vue';
import FilterNode from '@/components/nodes/tableProcess/FilterNode.vue';
import UploadNode from '@/components/nodes/file/UploadNode.vue';
import TableFromFileNode from '@/components/nodes/file/TableFromFileNode.vue';
import DualAxisPlotNode from '@/components/nodes/visualize/DualAxisPlotNode.vue';
import MergeNode from '@/components/nodes/tableProcess/MergeNode.vue';

const nodeTypes = {
  ConstNode: markRaw(ConstNode),
  NumberBinOpNode: markRaw(NumberBinOpNode),
  DateTimeNode: markRaw(DateTimeNode),
  DatetimeComputeNode: markRaw(DatetimeComputeNode),
  KlineNode: markRaw(KlineNode),
  QuickPlotNode: markRaw(QuickPlotNode),
  StatsNode: markRaw(StatsNode),
  ToFloatNode: markRaw(ToFloatNode),
  ToIntNode: markRaw(ToIntNode),
  LinearRegressionNode: markRaw(LinearRegressionNode),
  RegressionScoreNode: markRaw(RegressionScoreNode),
  FilterNode: markRaw(FilterNode),
  UploadNode: markRaw(UploadNode),
  TableFromFileNode: markRaw(TableFromFileNode),
  DualAxisPlotNode: markRaw(DualAxisPlotNode),
  MergeNode: markRaw(MergeNode),
};

// 示例数据（保持原样）
const nodes1 = ref([
  { id: 'DateTimeNode_1', type: 'DateTimeNode', position: { x: 20, y: 30 }, data: { param: { value: '', isNow: true }, dbclicked: false, runningtime: 0.0893150000820242 }, class: 'nowheel' },
  { id: 'DateTimeNode_2', type: 'DateTimeNode', position: { x: 350, y: 400 }, data: { param: { value: '', isNow: false }, dbclicked: false, runningtime: 0.04911700000320707 }, class: 'nowheel' },
  { id: 'ConstNode_1', type: 'ConstNode', position: { x: 20, y: 200 }, data: { param: { value: 0, data_type: 'int' }, dbclicked: false, runningtime: 0.07266500006153365 }, class: 'nowheel' },
  { id: 'DatetimeComputeNode_1', type: 'DatetimeComputeNode', position: { x: 350, y: 30 }, data: { param: { op: 'ADD' , unit: 'DAYS', value: 0, data_type: 'int'}, dbclicked: false, runningtime: 0.15581699994982046 }, class: 'nowheel' },
  { id: 'KlineNode_1', type: 'KlineNode', position: { x: 680, y: 150 }, data: { param: { data_type: 'stock', symbol: '', start_time: null, end_time: null, interval: '1m' }, dbclicked: false, runningtime: 710.2902609999546 }, class: 'nowheel' }
]);
const nodes2 = ref([
  { id: 'StatsNode_1', type: 'StatsNode', position: { x: 20, y: 50 }, data: { param: {}, dbclicked: false, runningtime: 0.2 }, class: 'nowheel' },
  { id: 'ConstNode_3', type: 'ConstNode', position: { x: 290, y: 300 }, data: { param: { value: 10, data_type: 'int' }, dbclicked: false, runningtime: 0.05348499962565256 }, class: 'nowheel' },
  { id: 'NumberBinOpNode_1', type: 'NumberBinOpNode', position: { x: 560, y: 201 }, data: { param: { op: 'DIV' }, dbclicked: false, runningtime: 0.0}, class: 'nowheel' },
  { id: 'ToFloatNode_1', type: 'ToFloatNode', position: { x: 290, y: 170 }, data: { param: {}, dbclicked: false, runningtime: 0.0 }, class: 'nowheel' },
  { id: 'ToIntNode_1', type: 'ToIntNode', position: { x: 830, y: 321 }, data: { param: {}, dbclicked: false, runningtime: 0.0 }, class: 'nowheel' }
]);
const nodes3 = ref([
  { id: 'LinearRegressionNode_1', type: 'LinearRegressionNode', position: { x: 825, y: 300 }, data: { param: {feature_cols: ['Open', 'Close'],target_col: "Volume"}, dbclicked: false, runningtime: 53.1 }, class: 'nowheel' },
  { id: 'UploadNode_1', type: 'UploadNode', position: { x: 0, y: 50 }, data: { param: {}, dbclicked: false, runningtime: 0.05667999994329875 }, class: 'nowheel' },
  { id: 'RegressionScoreNode_1', type: 'RegressionScoreNode', position: { x: 1100, y: 138 }, data: { param: {}, dbclicked: false, runningtime: 17.8 }, class: 'nowheel' },
  { id: 'FilterNode_1', type: 'FilterNode', position: { x: 550, y: 50 }, data: { param: {}, dbclicked: false, runningtime: 0.5 }, class: 'nowheel' },
  { id: 'TableFromFileNode_1', type: 'TableFromFileNode', position: { x: 275, y: 75 }, data: { param: {}, dbclicked: false, runningtime: 19.82704400052171 }, class: 'nowheel' }
]);
const nodes4 = ref([
  { id: 'DualAxisPlotNode_1', type: 'DualAxisPlotNode', position: { x: 950, y: 500 }, data: { param: {}, dbclicked: false, runningtime: 471.34476699920924 }, class: 'nowheel' },
  { id: 'KlineNode_1', type: 'KlineNode', position: { x: 50, y: 50 }, data: { param: { data_type: 'stock', symbol: 'AAPL', start_time: '2023-01-01', end_time: '2023-12-31', interval: '1d' }, dbclicked: false, runningtime: 329.65625900033046 }, class: 'nowheel' },
  { id: 'KlineNode_2', type: 'KlineNode', position: { x: 50, y: 500 }, data: { param: { data_type: 'stock', symbol: 'GOOGL', start_time: '2023-01-01', end_time: '2023-12-31', interval: '1d' }, dbclicked: false, runningtime: 176.7138300001534 }, class: 'nowheel' },
  { id: 'MergeNode_1', type: 'MergeNode', position: { x: 500, y: 400 }, data: { param: { join_type: 'inner', left_on: [], right_on: [] }, dbclicked: false, runningtime: 1.6944159997365205 }, class: 'nowheel' },
  { id: 'QuickPlotNode_1', type: 'QuickPlotNode', position: { x: 500, y: 600}, data: { param: {plot_type: ['line'],title: null,x_col: "Open Time",y_col: ['Open'],y_axis: ['left']}, dbclicked: false, runningtime: 435.82994200005487 }, class: 'nowheel' }
]);

const edges1 = ref([
  { id: 'vueflow__edge-DateTimeNode_1datetime-DatetimeComputeNode_1datetime', source: 'DateTimeNode_1', target: 'DatetimeComputeNode_1', sourceHandle: 'datetime', targetHandle: 'datetime', animated: true , type: 'NodePyEdge'},
  { id: 'vueflow__edge-ConstNode_1const-DatetimeComputeNode_1value', source: 'ConstNode_1', target: 'DatetimeComputeNode_1', sourceHandle: 'const', targetHandle: 'value', animated: true , type: 'NodePyEdge'},
  { id: 'vueflow__edge-DatetimeComputeNode_1result-KlineNode_1start_time', source: 'DatetimeComputeNode_1', target: 'KlineNode_1', sourceHandle: 'result', targetHandle: 'start_time', animated: true , type: 'NodePyEdge'},
  { id: 'vueflow__edge-DateTimeNode_2datetime-KlineNode_1end_time', source: 'DateTimeNode_2', target: 'KlineNode_1', sourceHandle: 'datetime', targetHandle: 'end_time', animated: true , type: 'NodePyEdge'}
]);
const edges2 = ref([
  { id: 'vueflow__edge-ConstNode_3const-NumberBinOpNode_1y', source: 'ConstNode_3', target: 'NumberBinOpNode_1', sourceHandle: 'const', targetHandle: 'y', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-StatsNode_1count-ToFloatNode_1input', source: 'StatsNode_1', target: 'ToFloatNode_1', sourceHandle: 'count', targetHandle: 'input', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-ToFloatNode_1output-NumberBinOpNode_1x', source: 'ToFloatNode_1', target: 'NumberBinOpNode_1', sourceHandle: 'output', targetHandle: 'x', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-NumberBinOpNode_1result-ToIntNode_1input', source: 'NumberBinOpNode_1', target: 'ToIntNode_1', sourceHandle: 'result', targetHandle: 'input', animated: true, type: 'NodePyEdge' }
]);
const edges3 = ref([
  { id: 'vueflow__edge-LinearRegressionNode_1model-RegressionScoreNode_1model', source: 'LinearRegressionNode_1', target: 'RegressionScoreNode_1', sourceHandle: 'model', targetHandle: 'model', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-FilterNode_1true_table-RegressionScoreNode_1table', source: 'FilterNode_1', target: 'RegressionScoreNode_1', sourceHandle: 'true_table', targetHandle: 'table', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-FilterNode_1false_table-LinearRegressionNode_1table', source: 'FilterNode_1', target: 'LinearRegressionNode_1', sourceHandle: 'false_table', targetHandle: 'table', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-UploadNode_1file-TableFromFileNode_1file', source: 'UploadNode_1', target: 'TableFromFileNode_1', sourceHandle: 'file', targetHandle: 'file', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-TableFromFileNode_1table-FilterNode_1table', source: 'TableFromFileNode_1', target: 'FilterNode_1', sourceHandle: 'table', targetHandle: 'table', animated: true, type: 'NodePyEdge' }
]);
const edges4 = ref([
  { id: 'vueflow__edge-KlineNode_1kline_data-MergeNode_1table_1', source: 'KlineNode_1', target: 'MergeNode_1', sourceHandle: 'kline_data', targetHandle: 'table_1', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-KlineNode_2kline_data-MergeNode_1table_2', source: 'KlineNode_2', target: 'MergeNode_1', sourceHandle: 'kline_data', targetHandle: 'table_2', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-MergeNode_1merged_table-DualAxisPlotNode_1input', source: 'MergeNode_1', target: 'DualAxisPlotNode_1', sourceHandle: 'merged_table', targetHandle: 'input', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-KlineNode_2kline_data-QuickPlotNode_1input', source: 'KlineNode_2', target: 'QuickPlotNode_1', sourceHandle: 'kline_data', targetHandle: 'input', animated: true, type: 'NodePyEdge' }
]);

const currentExampleIndex = ref(0);
const carouselTimer = ref<NodeJS.Timeout | null>(null);
const progressInterval = ref<NodeJS.Timeout | null>(null);
const progressPercent = ref(0);

const currentName = computed(() => {
  switch(currentExampleIndex.value) {
    case 0: return "DataFetch.nodepy";
    case 1: return "DataProcess.nodepy";
    case 2: return "MachineLearning.nodepy";
    case 3: return "DataVisulization.nodepy";
    default: return "DataFetch.nodepy";
  }
});

const currentNodes = computed(() => {
  switch(currentExampleIndex.value) {
    case 0: return nodes1.value;
    case 1: return nodes2.value;
    case 2: return nodes3.value;
    case 3: return nodes4.value;
    default: return nodes1.value;
  }
});

const currentEdges = computed(() => {
  switch(currentExampleIndex.value) {
    case 0: return edges1.value;
    case 1: return edges2.value;
    case 2: return edges3.value;
    case 3: return edges4.value;
    default: return edges1.value;
  }
});

const startProgress = () => {
  if (progressInterval.value) clearInterval(progressInterval.value);
  progressPercent.value = 0;
  progressInterval.value = setInterval(() => {
    if (progressPercent.value < 100) {
      progressPercent.value = Math.min(progressPercent.value + 2, 100);
    }
  }, 60);
};

const resetCarouselAndProgress = () => {
  if (progressInterval.value) clearInterval(progressInterval.value);
  progressPercent.value = 0;
  startProgress();
  if (carouselTimer.value) clearInterval(carouselTimer.value);
  carouselTimer.value = setInterval(() => {
    currentExampleIndex.value = (currentExampleIndex.value + 1) % 4;
    resetCarouselAndProgress();
  }, 3000);
};

const stopCarouselAndProgress = () => {
  if (carouselTimer.value) {
    clearInterval(carouselTimer.value);
    carouselTimer.value = null;
  }
  if (progressInterval.value) {
    clearInterval(progressInterval.value);
    progressInterval.value = null;
  }
};

const switchExample = (index: number) => {
  if (currentExampleIndex.value === index) return;
  currentExampleIndex.value = index;
  stopCarouselAndProgress();
  resetCarouselAndProgress();
};

const { onNodesInitialized, fitView } = useVueFlow('demo');

onNodesInitialized(() => {
  nextTick(() => {
    fitView({
      padding: 0.1,
      maxZoom: 0.65,
    });
  });
});

onMounted(() => {
  resetCarouselAndProgress();
});

onUnmounted(() => {
  stopCarouselAndProgress();
});
</script>

<style scoped lang="scss">
:deep(.vue-flow__handle) {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    border: none;
}

.example-carousel {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.editor-mockup {
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 15px 30px -10px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0,0,0,0.05);
  overflow: hidden;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;

  .mockup-header {
    background: #f1f5f9;
    padding: 8px 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #e2e8f0;
    position: relative;

    .window-controls span {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 8px;
      &:nth-child(1) { background: #ff5f56; }
      &:nth-child(2) { background: #ffbd2e; }
      &:nth-child(3) { background: #27c93f; }
    }

    .file-name {
      font-size: 0.8rem;
      font-weight: 500;
      color: grey;
      background: transparent;
      padding: 0;
      border-radius: 0;
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
      white-space: nowrap;
    }

    .mockup-actions {
      .run-indicator {
        width: 12px;
        height: 12px;
        background: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
      }
    }
  }

  .mockup-body {
    height: 450px;
    background: #fefefe;
    position: relative;
  }

  .carousel-progress {
    height: 3px;
    // background: #e2e8f0;
    width: 100%;
    overflow: hidden;

    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, #2563eb, #7c3aed);
      width: 0%;
      transition: width 60ms linear;
    }
  }
}

/* 圆点指示器 */
.carousel-indicators {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
  padding: 0 16px;

  .indicator-dot {
    width: 8px;
    height: 8px;
    border-radius: 10px;
    background: #cbd5e1;
    transition: 0.2s;
    cursor: pointer;
    &.active {
      width: 28px;
      background: #2563eb;
    }
  }
}

/* VueFlow 切换淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .editor-mockup .mockup-header .file-name {
    font-size: 0.7rem;
    white-space: normal;
    transform: translateX(-50%);
    width: auto;
  }
}
</style>