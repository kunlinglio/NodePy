<script lang="ts" setup>
import { useLoginStore } from '@/stores/loginStore';
import { usePageStore } from '@/stores/pageStore';
import { onMounted, computed, ref, markRaw, watch, onUnmounted, nextTick } from 'vue';
import NodePyEdge from '@/components/NodePyEdge.vue';
import NodePyConnectionLine from '@/components/NodePyConnectionLine.vue';
import { useRouter } from 'vue-router';
import { VueFlow } from '@vue-flow/core'
import { useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
import type { ExploreListItem } from '@/utils/api';
import ExampleDemoFrame from './ExampleView/ExampleDemoFrame.vue'

import SvgIcon from '@jamescoyle/vue-icon';
import {
  mdiRocketLaunchOutline,
  mdiGithub,
  mdiGraph,
  mdiTableLarge,
  mdiChartScatterPlot,
  mdiFunctionVariant,
  mdiBrain,
  mdiTextSearch,
  mdiCalendarClock,
  mdiFileDocumentMultiple,
  mdiCloudCheck,
  mdiShieldLock,
  mdiCog,
  mdiDatabase,
  mdiChartLine,
  mdiCubeOutline,
  mdiTune,
  mdiFinance,
  mdiTrendingUp,
  mdiRobot,
  mdiVectorPolygon,
  mdiCellphoneLink,
  mdiServer,
  mdiResistorNodes,
  mdiChartBoxOutline,
  mdiSecurity,
  mdiChevronLeft,   // 新增：左箭头图标
  mdiChevronRight   // 新增：右箭头图标
} from '@mdi/js';

import ConstNode from '@/components/nodes/input/ConstNode.vue'
import NumberBinOpNode from '@/components/nodes/compute/NumberBinOpNode.vue'
import DateTimeNode from '@/components/nodes/input/DateTimeNode.vue'
import DatetimeComputeNode from '@/components/nodes/datetimeProcess/DatetimeComputeNode.vue'
import KlineNode from '@/components/nodes/input/KlineNode.vue'
import QuickPlotNode from '@/components/nodes/visualize/QuickPlotNode.vue'
import StatsNode from '@/components/nodes/analysis/StatsNode.vue'
import ToFloatNode from '@/components/nodes/compute/ToFloatNode.vue'
import ToIntNode from '@/components/nodes/compute/ToIntNode.vue'
import LinearRegressionNode from '@/components/nodes/machineLearning/LinearRegressionNode.vue'
import RegressionScoreNode from '@/components/nodes/machineLearning/RegressionScoreNode.vue'
import FilterNode from '@/components/nodes/tableProcess/FilterNode.vue'
import UploadNode from '@/components/nodes/file/UploadNode.vue'
import TableFromFileNode from '@/components/nodes/file/TableFromFileNode.vue'
import DualAxisPlotNode from '@/components/nodes/visualize/DualAxisPlotNode.vue'
import MergeNode from '@/components/nodes/tableProcess/MergeNode.vue'
import { useModalStore } from '@/stores/modalStore';
import AdminAccountInfo from '@/components/AdminAccountInfo.vue';

const pageStore = usePageStore()
const loginStore = useLoginStore()
const modalStore = useModalStore()
const router = useRouter()

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
  MergeNode: markRaw(MergeNode)
}

const nodes1 = ref([
  {
    id: 'DateTimeNode_1',
    type: 'DateTimeNode',
    position: { x: 20, y: 30 },
    data: { param: { value: '', isNow: true }, dbclicked: false, runningtime: 0.0893150000820242 },
    class: 'nowheel'
  },
  {
    id: 'DateTimeNode_2',
    type: 'DateTimeNode',
    position: { x: 350, y: 400 },
    data: { param: { value: '', isNow: false }, dbclicked: false, runningtime: 0.04911700000320707 },
    class: 'nowheel'
  },
  {
    id: 'ConstNode_1',
    type: 'ConstNode',
    position: { x: 20, y: 200 },
    data: { param: { value: 0, data_type: 'int' }, dbclicked: false, runningtime: 0.07266500006153365 },
    class: 'nowheel'
  },
  {
    id: 'DatetimeComputeNode_1',
    type: 'DatetimeComputeNode',
    position: { x: 350, y: 30 },
    data: { param: { op: 'ADD' , unit: 'DAYS', value: 0, data_type: 'int'}, dbclicked: false, runningtime: 0.15581699994982046 },
    class: 'nowheel'
  },
  {
    id: 'KlineNode_1',
    type: 'KlineNode',
    position: { x: 680, y: 150 },
    data: { param: { data_type: 'stock', symbol: '', start_time: null, end_time: null, interval: '1m' }, dbclicked: false, runningtime: 710.2902609999546 },
    class: 'nowheel'
  }
])

const nodes2 = ref([
  {
    id: 'StatsNode_1',
    type: 'StatsNode',
    position: { x: 20, y: 50 },
    data: { param: {}, dbclicked: false, runningtime: 0.2 },
    class: 'nowheel'
  },
  {
    id: 'ConstNode_3',
    type: 'ConstNode',
    position: { x: 290, y: 300 },
    data: { param: { value: 10, data_type: 'int' }, dbclicked: false, runningtime: 0.05348499962565256 },
    class: 'nowheel'
  },
  {
    id: 'NumberBinOpNode_1',
    type: 'NumberBinOpNode',
    position: { x: 560, y: 201 },
    data: { param: { op: 'DIV' }, dbclicked: false, runningtime: 0.0},
    class: 'nowheel'
  },
  {
    id: 'ToFloatNode_1',
    type: 'ToFloatNode',
    position: { x: 290, y: 170 },
    data: { param: {}, dbclicked: false, runningtime: 0.0 },
    class: 'nowheel'
  },
  {
    id: 'ToIntNode_1',
    type: 'ToIntNode',
    position: { x: 830, y: 321 },
    data: { param: {}, dbclicked: false, runningtime: 0.0 },
    class: 'nowheel'
  }
])

const nodes3 = ref([
  {
    id: 'LinearRegressionNode_1',
    type: 'LinearRegressionNode',
    position: { x: 825, y: 300 },
    data: { param: {feature_cols: ['Open', 'Close'],target_col: "Volume"}, dbclicked: false, runningtime: 53.1 },
    class: 'nowheel'
  },
  {
    id: 'UploadNode_1',
    type: 'UploadNode',
    position: { x: 0, y: 50 },
    data: { param: {}, dbclicked: false, runningtime: 0.05667999994329875 },
    class: 'nowheel'
  },
  {
    id: 'RegressionScoreNode_1',
    type: 'RegressionScoreNode',
    position: { x: 1100, y: 138 },
    data: { param: {}, dbclicked: false, runningtime: 17.8 },
    class: 'nowheel'
  },
  {
    id: 'FilterNode_1',
    type: 'FilterNode',
    position: { x: 550, y: 50 },
    data: { param: {}, dbclicked: false, runningtime: 0.5 },
    class: 'nowheel'
  },
  {
    id: 'TableFromFileNode_1',
    type: 'TableFromFileNode',
    position: { x: 275, y: 75 },
    data: { param: {}, dbclicked: false, runningtime: 19.82704400052171 },
    class: 'nowheel'
  }
])

const nodes4 = ref([
  {
    id: 'DualAxisPlotNode_1',
    type: 'DualAxisPlotNode',
    position: { x: 950, y: 500 },
    data: { param: {}, dbclicked: false, runningtime: 471.34476699920924 },
    class: 'nowheel'
  },
  {
    id: 'KlineNode_1',
    type: 'KlineNode',
    position: { x: 50, y: 50 },
    data: { param: { data_type: 'stock', symbol: 'AAPL', start_time: '2023-01-01', end_time: '2023-12-31', interval: '1d' }, dbclicked: false, runningtime: 329.65625900033046 },
    class: 'nowheel'
  },
  {
    id: 'KlineNode_2',
    type: 'KlineNode',
    position: { x: 50, y: 500 },
    data: { param: { data_type: 'stock', symbol: 'GOOGL', start_time: '2023-01-01', end_time: '2023-12-31', interval: '1d' }, dbclicked: false, runningtime: 176.7138300001534 },
    class: 'nowheel'
  },
  {
    id: 'MergeNode_1',
    type: 'MergeNode',
    position: { x: 500, y: 400 },
    data: { param: { join_type: 'inner', left_on: [], right_on: [] }, dbclicked: false, runningtime: 1.6944159997365205 },
    class: 'nowheel'
  },
  {
    id: 'QuickPlotNode_1',
    type: 'QuickPlotNode',
    position: { x: 500, y: 600},
    data: { param: {plot_type: ['line'],title: null,x_col: "Open Time",y_col: ['Open'],y_axis: ['left']}, dbclicked: false, runningtime: 435.82994200005487 },
    class: 'nowheel'
  }
])

const edges1 = ref([
  { id: 'vueflow__edge-DateTimeNode_1datetime-DatetimeComputeNode_1datetime', source: 'DateTimeNode_1', target: 'DatetimeComputeNode_1', sourceHandle: 'datetime', targetHandle: 'datetime', animated: true , type: 'NodePyEdge'},
  { id: 'vueflow__edge-ConstNode_1const-DatetimeComputeNode_1value', source: 'ConstNode_1', target: 'DatetimeComputeNode_1', sourceHandle: 'const', targetHandle: 'value', animated: true , type: 'NodePyEdge'},
  { id: 'vueflow__edge-DatetimeComputeNode_1result-KlineNode_1start_time', source: 'DatetimeComputeNode_1', target: 'KlineNode_1', sourceHandle: 'result', targetHandle: 'start_time', animated: true , type: 'NodePyEdge'},
  { id: 'vueflow__edge-DateTimeNode_2datetime-KlineNode_1end_time', source: 'DateTimeNode_2', target: 'KlineNode_1', sourceHandle: 'datetime', targetHandle: 'end_time', animated: true , type: 'NodePyEdge'}
])

const edges2 = ref([
  { id: 'vueflow__edge-ConstNode_3const-NumberBinOpNode_1y', source: 'ConstNode_3', target: 'NumberBinOpNode_1', sourceHandle: 'const', targetHandle: 'y', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-StatsNode_1count-ToFloatNode_1input', source: 'StatsNode_1', target: 'ToFloatNode_1', sourceHandle: 'count', targetHandle: 'input', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-ToFloatNode_1output-NumberBinOpNode_1x', source: 'ToFloatNode_1', target: 'NumberBinOpNode_1', sourceHandle: 'output', targetHandle: 'x', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-NumberBinOpNode_1result-ToIntNode_1input', source: 'NumberBinOpNode_1', target: 'ToIntNode_1', sourceHandle: 'result', targetHandle: 'input', animated: true, type: 'NodePyEdge' }
])

const edges3 = ref([
  { id: 'vueflow__edge-LinearRegressionNode_1model-RegressionScoreNode_1model', source: 'LinearRegressionNode_1', target: 'RegressionScoreNode_1', sourceHandle: 'model', targetHandle: 'model', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-FilterNode_1true_table-RegressionScoreNode_1table', source: 'FilterNode_1', target: 'RegressionScoreNode_1', sourceHandle: 'true_table', targetHandle: 'table', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-FilterNode_1false_table-LinearRegressionNode_1table', source: 'FilterNode_1', target: 'LinearRegressionNode_1', sourceHandle: 'false_table', targetHandle: 'table', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-UploadNode_1file-TableFromFileNode_1file', source: 'UploadNode_1', target: 'TableFromFileNode_1', sourceHandle: 'file', targetHandle: 'file', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-TableFromFileNode_1table-FilterNode_1table', source: 'TableFromFileNode_1', target: 'FilterNode_1', sourceHandle: 'table', targetHandle: 'table', animated: true, type: 'NodePyEdge' }
])

const edges4 = ref([
  { id: 'vueflow__edge-KlineNode_1kline_data-MergeNode_1table_1', source: 'KlineNode_1', target: 'MergeNode_1', sourceHandle: 'kline_data', targetHandle: 'table_1', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-KlineNode_2kline_data-MergeNode_1table_2', source: 'KlineNode_2', target: 'MergeNode_1', sourceHandle: 'kline_data', targetHandle: 'table_2', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-MergeNode_1merged_table-DualAxisPlotNode_1input', source: 'MergeNode_1', target: 'DualAxisPlotNode_1', sourceHandle: 'merged_table', targetHandle: 'input', animated: true, type: 'NodePyEdge' },
  { id: 'vueflow__edge-KlineNode_2kline_data-QuickPlotNode_1input', source: 'KlineNode_2', target: 'QuickPlotNode_1', sourceHandle: 'kline_data', targetHandle: 'input', animated: true, type: 'NodePyEdge' }
])

// 当前选中的示例索引
const currentExampleIndex = ref(0)

// 自动轮播定时器
const carouselTimer = ref<NodeJS.Timeout | null>(null)
// 进度条定时器
const progressInterval = ref<NodeJS.Timeout | null>(null)
// 进度百分比 (0-100)
const progressPercent = ref(0)

const currentName = computed(()=>{
  switch(currentExampleIndex.value) {
    case 0: return "DataFetch.nodepy"
    case 1: return "DataProcess.nodepy"
    case 2: return "MachineLearning.nodepy"
    case 3: return "DataVisulization.nodepy"
    default: return "DataFetch.nodepy"
  }
})
// 计算当前应该显示的节点和边
const currentNodes = computed(() => {
  switch(currentExampleIndex.value) {
    case 0: return nodes1.value
    case 1: return nodes2.value
    case 2: return nodes3.value
    case 3: return nodes4.value
    default: return nodes1.value
  }
})

const currentEdges = computed(() => {
  switch(currentExampleIndex.value) {
    case 0: return edges1.value
    case 1: return edges2.value
    case 2: return edges3.value
    case 3: return edges4.value
    default: return edges1.value
  }
})

// 特性列表 - 新增 mediaUrl 用于展示 GIF/视频
const features = [
  {
    icon: mdiGraph,
    title: '严格类型系统',
    description: '支持 Int, Float, Bool, String, Table, File, Datetime 七大类型，确保数据流转的准确性。',
    nodeType: 'input',
    mediaUrl: 'https://placehold.co/400x200/2563eb/white?text=Strict+Type+System'
  },
  {
    icon: mdiTableLarge,
    title: 'Pandas 表格处理',
    description: '内置强大的表格处理能力，支持过滤、去重、缺失值处理、列运算等复杂操作。',
    nodeType: 'tableProcess',
    mediaUrl: 'https://placehold.co/400x200/3b82f6/white?text=Pandas+Processing'
  },
  {
    icon: mdiChartScatterPlot,
    title: '专业可视化',
    description: '支持散点图、折线图、柱状图、面积图、K线图等多种专业金融图表绘制。',
    nodeType: 'visualize',
    mediaUrl: 'https://placehold.co/400x200/8b5cf6/white?text=Visualization'
  },
  {
    icon: mdiFunctionVariant,
    title: 'Python 驱动',
    description: '底层完全由 Python 驱动，兼容 Python 生态，计算结果精准可靠。',
    nodeType: 'compute',
    mediaUrl: 'https://placehold.co/400x200/06b6d4/white?text=Python+Driven'
  },
  {
    icon: mdiBrain,
    title: '机器学习支持',
    description: '集成 scikit-learn，支持线性回归、逻辑回归等多种机器学习算法。',
    nodeType: 'machineLearning',
    mediaUrl: 'https://placehold.co/400x200/ec4899/white?text=Machine+Learning'
  },
  {
    icon: mdiTextSearch,
    title: '文本处理',
    description: '内置分词、正则匹配、情感分析等强大的文本处理能力。',
    nodeType: 'stringProcess',
    mediaUrl: 'https://placehold.co/400x200/f59e0b/white?text=Text+Processing'
  },
  {
    icon: mdiCalendarClock,
    title: '时间序列',
    description: '完整的时间序列数据处理能力，支持日期计算、移动窗口等操作。',
    nodeType: 'datetimeProcess',
    mediaUrl: 'https://placehold.co/400x200/10b981/white?text=Time+Series'
  },
  {
    icon: mdiFileDocumentMultiple,
    title: '文件系统',
    description: '支持 CSV、Excel、JSON 等多种文件格式的导入导出，配额管理更安全。',
    nodeType: 'file',
    mediaUrl: 'https://placehold.co/400x200/6b7280/white?text=File+System'
  }
]

// 实例项目列表
const examples = ref<ExploreListItem[]>([])

// 启动进度条更新
const startProgress = () => {
  if (progressInterval.value) clearInterval(progressInterval.value)
  progressPercent.value = 0
  progressInterval.value = setInterval(() => {
    if (progressPercent.value < 100) {
      progressPercent.value = Math.min(progressPercent.value + 2, 100)
    }
  }, 60) // 3000ms / 50步 = 60ms/步
}

// 重置进度条并重启自动轮播计时
const resetCarouselAndProgress = () => {
  // 重置进度条
  if (progressInterval.value) clearInterval(progressInterval.value)
  progressPercent.value = 0
  startProgress()
  // 重置自动轮播计时
  if (carouselTimer.value) clearInterval(carouselTimer.value)
  carouselTimer.value = setInterval(() => {
    currentExampleIndex.value = (currentExampleIndex.value + 1) % 4
    resetCarouselAndProgress()
  }, 3000)
}

// 停止所有定时器
const stopCarouselAndProgress = () => {
  if (carouselTimer.value) {
    clearInterval(carouselTimer.value)
    carouselTimer.value = null
  }
  if (progressInterval.value) {
    clearInterval(progressInterval.value)
    progressInterval.value = null
  }
}

// 手动切换示例
const switchExample = (index: number) => {
  if (currentExampleIndex.value === index) return
  currentExampleIndex.value = index
  stopCarouselAndProgress()
  resetCarouselAndProgress()
}

// ================= 生态圆柱体轮播逻辑 (增强版：无限循环 + 平滑旋转) =================
// 生态卡片数据（共6个）
const ecosystemItems = [
  {
    icon: mdiDatabase,
    title: '数据接入',
    description: '支持股票、加密货币、宏观经济数据等实时/历史数据源'
  },
  {
    icon: mdiTune,
    title: '数据清洗',
    description: '缺失值处理、异常检测、数据标准化、去重聚合'
  },
  {
    icon: mdiChartLine,
    title: '技术指标',
    description: '内置MACD、RSI、布林带等50+种技术分析指标'
  },
  {
    icon: mdiRobot,
    title: '机器学习',
    description: '回归、分类、聚类算法，支持模型训练与评估'
  },
  {
    icon: mdiVectorPolygon,
    title: '策略回测',
    description: '事件驱动回测框架，精准评估策略表现'
  },
  {
    icon: mdiCellphoneLink,
    title: '实时监控',
    description: 'WebSocket实时行情接入，策略信号实时推送'
  }
]

// 当前旋转角度（单位：度），可以无限累加/累减，实现无缝循环
const currentEcoAngle = ref(0)
// 生态自动轮播定时器
let ecoAutoTimer: NodeJS.Timeout | null = null
// 是否正在悬停（悬停时暂停自动轮播）
const isEcoHovering = ref(false)

// 获取当前高亮索引（0-5）
const currentEcoIndex = computed(() => {
  // 取模运算，确保结果在 0-5 之间
  const raw = Math.round(currentEcoAngle.value / 60)
  return ((raw % 6) + 6) % 6
})

// 旋转到指定索引（使用最短路径增量，保证动画平滑不绕远）
const rotateToEcoIndex = (targetIndex: number) => {
  const currentIndex = currentEcoIndex.value
  let delta = targetIndex - currentIndex
  // 选择最短路径
  if (delta > 3) delta -= 6
  if (delta < -3) delta += 6
  currentEcoAngle.value += delta * 60
}

// 下一个（增加60度）
const nextEco = () => {
  currentEcoAngle.value += 60
  resetEcoAutoTimer()
}

// 上一个（减少60度）
const prevEco = () => {
  currentEcoAngle.value -= 60
  resetEcoAutoTimer()
}

// 启动生态自动轮播（每3秒切换一次）
const startEcoAutoTimer = () => {
  if (ecoAutoTimer) clearInterval(ecoAutoTimer)
  ecoAutoTimer = setInterval(() => {
    if (!isEcoHovering.value) {
      nextEco()
    }
  }, 3000)
}

// 重置生态自动轮播计时（用户点击箭头后重新计时）
const resetEcoAutoTimer = () => {
  if (ecoAutoTimer) {
    clearInterval(ecoAutoTimer)
    ecoAutoTimer = null
  }
  startEcoAutoTimer()
}

// 暂停生态自动轮播（鼠标移入）
const pauseEcoAuto = () => {
  isEcoHovering.value = true
}

// 恢复生态自动轮播（鼠标移出）
const resumeEcoAuto = () => {
  isEcoHovering.value = false
  resetEcoAutoTimer()
}

// ================= 原有 onMounted 等逻辑 =================
onMounted(async () => {
  loginStore.checkAuthStatus()
  pageStore.setCurrentPage('Home')
  try {
    const authService = AuthenticatedServiceFactory.getService()
    // const res = await authService.getExploreProjectsApiExploreExploreProjectsGet()
    // examples.value = res.projects
  } catch (e) {
    console.error('Failed to fetch examples:', e)
  }

  // 启动示例自动轮播和进度条
  resetCarouselAndProgress()
  
  // 启动生态圆柱体自动轮播
  startEcoAutoTimer()
})

const { onNodeClick, findNode, onConnect, onNodesInitialized, fitView, onNodeDragStop, addEdges, getNodes, onPaneClick, screenToFlowCoordinate } = useVueFlow('demo')

onNodesInitialized(() => {
  nextTick(() => {
    fitView({
      padding: 0.1,
      maxZoom: 0.65,
    })
  })
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopCarouselAndProgress()
  if (ecoAutoTimer) clearInterval(ecoAutoTimer)
})

function jumpToLogin() {
  router.push({
    name: 'login'
  })
}

function jumpToProject() {
  router.push({
    name: 'project'
  })
}

// 跳转到案例
function jumpToExample() {
  router.push({
    name: 'example'
  })
}

// 用户是否已登录
const isLoggedIn = computed(() => loginStore.loggedIn)

// 快速开始按钮行为
function quickStart() {
  if (isLoggedIn.value) {
    jumpToProject()
  } else {
    jumpToLogin()
  }
}

// 跳转到GitHub
function jumpToGithub() {
  window.open('https://github.com/LKLLLLLLLLLL/NodePy', '_blank')
}

function jumpToAdmin(){
  if (loginStore.loggedIn) {
      const UserAccessWidth = 300
      const UserAccessHeight = 240
      modalStore.createModal({
        component: AdminAccountInfo,
        title: '用户权限',
        isActive: true,
        isResizable: false,
        isDraggable: true,
        isModal: true,
        position: {
          x: window.innerWidth / 2 - UserAccessWidth / 2,
          y: window.innerHeight / 2 - UserAccessHeight / 2
        },
        size: {
          width: UserAccessWidth,
          height: UserAccessHeight
        },
        id: 'user-access',
    })
    return;
  }
  router.push({ name: 'adminlogin' });
}
</script>

<template>
  <div class="home-container">
    <!-- 动态背景粒子层 -->
    <div class="particle-bg"></div>
    <div class="gradient-orb orb-1"></div>
    <div class="gradient-orb orb-2"></div>
    <div class="gradient-orb orb-3"></div>

    <div class="home-content">
      <div class="scroll-content">
        <!-- Hero Section 优化布局：更直观的描述 + 快速开始按钮 -->
        <div class="section hero-section">
          <div class="hero-top">
            <h1 class="hero-title">
              NodePy
              <span class="gradient-text">基于节点的金融数据分析平台</span>
            </h1>
            <p class="hero-subtitle">
              无需编写复杂代码，通过拖拽节点即可完成从数据获取、清洗、计算到可视化的全过程。
            </p>
            
            <!-- 快速开始按钮 -->
            <div class="quick-start-wrapper">
              <button @click="quickStart" class="quick-start-btn">
                <!-- <svg-icon :path="mdiRocketLaunchOutline" :size="20" class="btn-icon" /> -->
                快速开始
              </button>
            </div>
          </div>
          
          <!-- 可视化展示区（保持不变） -->
          <div class="hero-visual">
            <div class="editor-mockup">
              <div class="mockup-header">
                <div class="window-controls">
                  <span></span><span></span><span></span>
                </div>
                <div class="file-name">{{ currentName }}</div>
                <div class="mockup-actions">
                  <div class="run-indicator"></div>
                </div>
              </div>
              <div class="mockup-body">
                <VueFlow
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
                  <Background color="rgba(50, 50, 50, 0.03)" variant="dots" :gap="16" :size="2"/>
                  <template #edge-NodePyEdge="NodePyEdgeProps">
                    <NodePyEdge v-bind="NodePyEdgeProps"/>
                  </template>
                  <template #connection-line="ConnectionLineProps">
                    <NodePyConnectionLine v-bind="ConnectionLineProps"/>
                  </template>
                </VueFlow>
              </div>
              <!-- 进度条 -->
              <div class="carousel-progress">
                <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
              </div>
              <div class="carousel-indicators">
                <span
                  v-for="(_, index) in 4"
                  :key="index"
                  class="indicator-dot"
                  :class="{ active: currentExampleIndex === index }"
                  @click="switchExample(index)"
                ></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 核心优势 Features - 改为 GIF/视频展示区域 -->
        <div class="section features-section">
          <div class="section-header">
            <h2 class="section-title">专为量化而生，<span class="gradient-text">开箱即用</span></h2>
            <p class="section-subtitle">从数据获取到策略回测，NodePy 提供一站式金融数据分析解决方案</p>
          </div>
          <div class="features-media-grid">
            <div
              v-for="(feature, index) in features"
              :key="index"
              class="feature-media-card"
              :class="`type-${feature.nodeType}`"
            >
              <div class="feature-media">
                <!-- 展示 GIF/视频，实际使用时替换为真实资源 -->
                <img :src="feature.mediaUrl" :alt="feature.title" class="feature-gif">
              </div>
              <div class="feature-info">
                <div class="feature-icon">
                  <svg-icon :path="feature.icon" :size="24" type="mdi"></svg-icon>
                </div>
                <h3>{{ feature.title }}</h3>
                <p>{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 全新生态展示: 立体圆柱体轮播 (增强版：大半径 + 两侧渐变遮罩 + 炫酷卡片) -->
        <div class="section ecosystem-section">
          <div class="section-header">
            <h2 class="section-title">丰富的<span class="gradient-text">节点生态</span></h2>
            <p class="section-subtitle">覆盖数据分析全流程，满足复杂金融场景需求</p>
          </div>
          
          <div class="cylinder-carousel-wrapper"
               @mouseenter="pauseEcoAuto"
               @mouseleave="resumeEcoAuto">
            <button class="carousel-arrow left-arrow" @click="prevEco">
              <svg-icon :path="mdiChevronLeft" :size="32" />
            </button>
            <div class="cylinder-container">
              <div class="cylinder-stage">
                <div class="cylinder-carousel"
                     :style="{ transform: `rotateY(${currentEcoAngle}deg)` }">
                  <div v-for="(item, idx) in ecosystemItems"
                       :key="idx"
                       class="cylinder-card"
                       :style="{ transform: `rotateY(${idx * 60}deg) translateZ(420px)` }">
                    <div class="card-inner">
                      <div class="eco-icon">
                        <svg-icon :path="item.icon" :size="44" />
                      </div>
                      <h4>{{ item.title }}</h4>
                      <p>{{ item.description }}</p>
                      <div class="card-glow"></div>
                    </div>
                  </div>
                </div>
              </div>
              <!-- 左右两侧渐变遮罩，制造淡出效果 -->
              <div class="cylinder-mask mask-left"></div>
              <div class="cylinder-mask mask-right"></div>
            </div>
            <button class="carousel-arrow right-arrow" @click="nextEco">
              <svg-icon :path="mdiChevronRight" :size="32" />
            </button>
          </div>
          <!-- 指示点 -->
          <div class="cylinder-indicators">
            <span v-for="(_, idx) in ecosystemItems"
                  :key="idx"
                  class="cylinder-dot"
                  :class="{ active: currentEcoIndex === idx }"
                  @click="rotateToEcoIndex(idx)"></span>
          </div>
        </div>

        <!-- 应用场景 / 模板案例 -->
        <div class="section showcase-section">
          <div class="section-header">
            <h2 class="section-title">精选<span class="gradient-text">工作流模板</span></h2>
            <p class="section-subtitle">从经典策略到前沿应用，快速启动您的项目</p>
          </div>
          <div class="showcase-grid">
            <div class="showcase-card" @click="jumpToExample">
              <div class="showcase-img placeholder-img-1"></div>
              <div class="showcase-info">
                <h3>量化选股策略</h3>
                <p>多因子选股 + 回测分析，一键生成绩效报告</p>
                <div class="showcase-tags">
                  <span>机器学习</span>
                  <span>回测</span>
                </div>
              </div>
            </div>
            <div class="showcase-card" @click="jumpToExample">
              <div class="showcase-img placeholder-img-2"></div>
              <div class="showcase-info">
                <h3>高频数据处理</h3>
                <p>Tick级数据清洗、聚合、特征工程流水线</p>
                <div class="showcase-tags">
                  <span>实时计算</span>
                  <span>大数据</span>
                </div>
              </div>
            </div>
            <div class="showcase-card" @click="jumpToExample">
              <div class="showcase-img placeholder-img-3"></div>
              <div class="showcase-info">
                <h3>风险敞口分析</h3>
                <p>投资组合风险度量，VaR/CVaR 计算可视化</p>
                <div class="showcase-tags">
                  <span>风险管理</span>
                  <span>可视化</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 混合部署与自托管优势 (优化布局 + 新命令) -->
        <div class="section hybrid-section">
          <div class="hybrid-container">
            <div class="hybrid-text">
              <span class="hybrid-badge">企业级</span>
              <h2>云原生 + 自托管<br>双重保障</h2>
              <p>支持在云端快速体验，也支持部署在您的自有服务器。数据不出域，满足金融级安全合规要求。</p>
              <div class="hybrid-features">
                <div><svg-icon :path="mdiCloudCheck" :size="20"/> 弹性伸缩，按需付费</div>
                <div><svg-icon :path="mdiShieldLock" :size="20"/> 私有化部署，数据主权</div>
                <div><svg-icon :path="mdiServer" :size="20"/> 混合模式，无缝切换</div>
              </div>
            </div>
            <div class="hybrid-visual">
              <div class="code-block">
                <pre><code># 克隆项目
git clone https://github.com/LKLLLLLLLLLL/NodePy.git
cd NodePy

# 安装 Python 依赖 (使用 uv)
uv sync --all-groups

# 安装前端依赖
cd client
npm install
cd ..

# 自定义配置 (编辑 /server/config.py 文件)

# 构建并启动生产环境
uv run task prod</code></pre>
              </div>
            </div>
          </div>
        </div>

        <!-- CTA 区域 -->
        <div class="section cta-section">
          <div class="cta-card">
            <div class="cta-content">
              <h2>准备好开始了吗？</h2>
              <p>立即注册，开启您的可视化金融分析之旅</p>
              <div class="cta-buttons">
                <button @click="jumpToExample" class="cta-btn outline">探索案例</button>
                <button @click="isLoggedIn ? jumpToProject() : jumpToLogin()" class="cta-btn solid">
                  {{ isLoggedIn ? '进入工作台' : '免费注册' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 页脚 -->
        <div class="footer-section">
          <div class="footer-main">
            <div class="footer-brand">
              <h3>NodePy</h3>
              <p>下一代可视化金融数据分析平台</p>
              <div class="admin-entrance" @click="jumpToAdmin">管理员入口</div>
            </div>
            <div class="footer-links">
              <div class="link-group">
                <h4>产品</h4>
                <a @click="jumpToExample">案例</a>
                <a @click="jumpToProject">工作台</a>
              </div>
              <div class="link-group">
                <h4>支持</h4>
                <a>文档</a>
                <a>社区</a>
              </div>
              <div class="link-group">
                <h4>关于</h4>
                <a @click="jumpToGithub">GitHub</a>
                <a>团队</a>
              </div>
            </div>
          </div>
          <div class="footer-copyright">
            <p>© 2025 NodePy Team. 数据驱动未来，节点构建智能。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '@/common/global.scss' as *;
@use '@/common/node.scss' as *;
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&display=swap');

// 重置与基础
.home-container {
  font-family: 'Inter', sans-serif;
  flex: 1;
  position: relative;
  background: #f8faff;
  overflow-x: hidden;
  color: #1e293b;
}

// 动态背景元素
.particle-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(#3b82f6 0.5px, transparent 0.5px);
  background-size: 24px 24px;
  opacity: 0.3;
  pointer-events: none;
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  z-index: 0;
  pointer-events: none;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: #3b82f6;
  top: -200px;
  right: -150px;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: #8b5cf6;
  bottom: 100px;
  left: -100px;
}

.orb-3 {
  width: 300px;
  height: 300px;
  background: #06b6d4;
  top: 60%;
  left: 40%;
}

.home-content {
  position: relative;
  z-index: 2;
  overflow-y: auto;
  height: 100%;
}

.section {
  max-width: 1280px;
  margin: 0 auto;
  padding: 80px 24px;

  @media (max-width: 768px) {
    padding: 48px 20px;
  }
}

.section-header {
  text-align: center;
  margin-bottom: 48px;

  .section-title {
    font-size: 2.5rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #0f172a;
    margin-bottom: 16px;
  }

  .section-subtitle {
    font-size: 1.125rem;
    color: #475569;
    max-width: 600px;
    margin: 0 auto;
  }
}

.gradient-text {
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

// Hero 区域优化
.hero-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  // gap: 48px;
  padding-top: 60px;
  padding-bottom: 60px;
  min-height: auto;

  .hero-top {
    max-width: 900px;
  }

  .hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.02em;
    color: #0f172a;
    margin-bottom: 24px;
    display: flex;
    flex-direction: column;
    gap: 8px;

    .gradient-text {
      font-size: 2rem;
    }

    @media (max-width: 768px) {
      font-size: 2.5rem;
      .gradient-text {
        font-size: 1.5rem;
      }
    }
  }

  .hero-subtitle {
    font-size: 1.125rem;
    color: #475569;
    line-height: 1.6;
    margin-bottom: 32px;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;

    strong {
      color: #2563eb;
      font-weight: 600;
    }
  }

  // 快速开始按钮区域
  .quick-start-wrapper {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-bottom: 48px;

    .quick-start-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      color: white;
      border: none;
      padding: 12px 32px;
      border-radius: 40px;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);

      .btn-icon {
        transition: transform 0.2s ease;
      }

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
        
        .btn-icon {
          transform: translateX(2px);
        }
      }
    }

    .outline-btn {
      background: transparent;
      border: 1px solid #cbd5e1;
      padding: 12px 32px;
      border-radius: 40px;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;
      color: #1e293b;

      &:hover {
        background: #f1f5f9;
        border-color: #94a3b8;
      }
    }
  }

  .hero-visual {
    width: 100%;
    max-width: 900px;
    margin: 0 auto;
    pointer-events: none;
  }
}

.editor-mockup {
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 30px 50px -20px rgba(0,0,0,0.2);
  border: 1px solid rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  overflow: hidden;

  .mockup-header {
    background: #f1f5f9;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #e2e8f0;

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
      color: #334155;
      background: white;
      padding: 4px 12px;
      border-radius: 20px;
    }
  }

  .mockup-body {
    height: 480px;
    background: #fefefe;
    position: relative;
  }

  .carousel-progress {
    height: 3px;
    background: #e2e8f0;
    width: 100%;
    overflow: hidden;

    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, #2563eb, #7c3aed);
      width: 0%;
      transition: width 60ms linear;
    }
  }

  .carousel-indicators {
    display: flex;
    justify-content: center;
    gap: 10px;
    padding: 16px;
    background: white;
    border-top: 1px solid #f0f2f5;

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
}

// 新的 Features 媒体网格 (GIF/视频展示)
.features-media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 28px;
}

.feature-media-card {
  background: white;
  border-radius: 24px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border: 1px solid rgba(0,0,0,0.03);

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 30px -12px rgba(0,0,0,0.15);
    border-color: rgba(37,99,235,0.2);
  }

  .feature-media {
    width: 100%;
    height: 180px;
    overflow: hidden;
    background: #f1f5f9;

    .feature-gif {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s ease;
    }

    &:hover .feature-gif {
      transform: scale(1.02);
    }
  }

  .feature-info {
    padding: 20px;
    position: relative;

    .feature-icon {
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 12px;
      background: #eef2ff;
      color: #2563eb;
      margin-bottom: 16px;
    }

    h3 {
      font-size: 1.2rem;
      font-weight: 700;
      margin-bottom: 8px;
    }

    p {
      color: #475569;
      line-height: 1.5;
      font-size: 0.85rem;
    }
  }
}

// ========== 立体圆柱体轮播样式 (增强版：大半径，两侧渐变遮罩，炫酷卡片) ==========
.cylinder-carousel-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 40px 0;
  padding: 20px 0;
}

.carousel-arrow {
  background: rgba(255,255,255,0.9);
  border: 1px solid rgba(37,99,235,0.2);
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
  color: #1e293b;
  backdrop-filter: blur(8px);
  z-index: 20;
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
  
  &:hover {
    background: white;
    transform: scale(1.08);
    box-shadow: 0 12px 24px rgba(37,99,235,0.2);
    color: #2563eb;
    border-color: #2563eb;
  }
  
  &.left-arrow {
    margin-right: 20px;
  }
  
  &.right-arrow {
    margin-left: 20px;
  }
  
  @media (max-width: 768px) {
    width: 36px;
    height: 36px;
    &.left-arrow { margin-right: 10px; }
    &.right-arrow { margin-left: 10px; }
  }
}

.cylinder-container {
  flex: 1;
  max-width: 1100px;
  perspective: 1600px;
  overflow: visible;
  position: relative;
}

.cylinder-stage {
  width: 100%;
  height: 380px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.cylinder-carousel {
  position: relative;
  width: 300px;
  height: 340px;
  transform-style: preserve-3d;
  transition: transform 0.7s cubic-bezier(0.25, 0.85, 0.35, 1);
  will-change: transform;
}

.cylinder-card {
  position: absolute;
  top: 0;
  left: 0;
  width: 300px;
  height: 340px;
  border-radius: 28px;
  background: linear-gradient(145deg, rgba(255,255,255,0.95), rgba(249,250,255,0.98));
  backdrop-filter: blur(2px);
  box-shadow: 0 25px 40px -12px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.8);
  border: 1px solid rgba(255,255,255,0.6);
  transition: all 0.3s ease;
  cursor: default;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 28px;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #2563eb, #7c3aed, #06b6d4);
    border-radius: 28px 28px 0 0;
  }
  
  .card-inner {
    width: 100%;
    position: relative;
    z-index: 2;
  }
  
  .eco-icon {
    margin-bottom: 24px;
    color: #2563eb;
    background: linear-gradient(135deg, #eef2ff, #ffffff);
    width: 70px;
    height: 70px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 30px;
    margin-left: auto;
    margin-right: auto;
    box-shadow: 0 8px 16px -8px rgba(0,0,0,0.1);
    
    svg {
      width: 44px;
      height: 44px;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.05));
    }
  }
  
  h4 {
    font-size: 1.4rem;
    font-weight: 800;
    margin-bottom: 14px;
    background: linear-gradient(135deg, #0f172a, #1e293b);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    letter-spacing: -0.01em;
  }
  
  p {
    font-size: 0.9rem;
    color: #475569;
    line-height: 1.5;
    font-weight: 500;
  }
  
  .card-glow {
    position: absolute;
    bottom: -20px;
    left: 10%;
    width: 80%;
    height: 40px;
    background: radial-gradient(ellipse, rgba(37,99,235,0.2), transparent);
    filter: blur(12px);
    z-index: 0;
    pointer-events: none;
  }
  
  &:hover {
    transform: translateY(-6px) rotateY(0deg) !important;
    box-shadow: 0 35px 50px -20px rgba(0,0,0,0.35);
    border-color: rgba(37,99,235,0.3);
    
    .card-glow {
      opacity: 0.7;
      transform: scale(1.1);
    }
  }
  
  @media (max-width: 768px) {
    width: 260px;
    height: 300px;
    padding: 20px;
    h4 { font-size: 1.2rem; }
    p { font-size: 0.8rem; }
    .eco-icon { width: 56px; height: 56px; svg { width: 36px; height: 36px; } }
  }
}

// 左右渐变遮罩，制造淡出效果，提升圆柱体两侧视觉深度
.cylinder-mask {
  position: absolute;
  top: 0;
  width: 120px;
  height: 100%;
  pointer-events: none;
  z-index: 15;
  transition: opacity 0.3s ease;
  
  &.mask-left {
    left: 0;
    background: linear-gradient(to right, rgba(248,250,255,0.95), rgba(248,250,255,0));
  }
  
  &.mask-right {
    right: 0;
    background: linear-gradient(to left, rgba(248,250,255,0.95), rgba(248,250,255,0));
  }
  
  @media (max-width: 768px) {
    width: 60px;
  }
}

.cylinder-indicators {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-top: 32px;
  
  .cylinder-dot {
    width: 10px;
    height: 10px;
    border-radius: 12px;
    background: #cbd5e1;
    transition: all 0.2s ease;
    cursor: pointer;
    
    &.active {
      width: 32px;
      background: linear-gradient(90deg, #2563eb, #7c3aed);
      box-shadow: 0 0 6px rgba(37,99,235,0.4);
    }
    
    &:hover {
      background: #94a3b8;
      transform: scale(1.1);
    }
  }
}

// 保留原生态卡片网格样式（已替换为圆柱体，但保留其他可能引用）
.ecosystem-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.eco-card {
  background: white;
  border-radius: 24px;
  padding: 28px;
  text-align: center;
  transition: 0.2s;
  border: 1px solid #f1f5f9;
  &:hover {
    border-color: #cbd5e1;
    box-shadow: 0 12px 20px -12px rgba(0,0,0,0.08);
  }
  .eco-icon {
    margin-bottom: 20px;
    color: #2563eb;
  }
  h4 { font-weight: 700; margin-bottom: 12px; }
  p { color: #475569; font-size: 0.85rem; }
}

// Showcase
.showcase-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
}

.showcase-card {
  background: white;
  border-radius: 24px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 25px -12px rgba(0,0,0,0.1);
  }
  .showcase-img {
    height: 160px;
    background-size: cover;
    background-position: center;
  }
  .placeholder-img-1 { background: linear-gradient(135deg, #3b82f6, #8b5cf6); }
  .placeholder-img-2 { background: linear-gradient(135deg, #06b6d4, #3b82f6); }
  .placeholder-img-3 { background: linear-gradient(135deg, #f59e0b, #ef4444); }
  .showcase-info {
    padding: 20px;
    h3 { font-weight: 700; margin-bottom: 8px; }
    p { font-size: 0.85rem; color: #475569; margin-bottom: 12px; }
    .showcase-tags span {
      background: #f1f5f9;
      padding: 4px 8px;
      border-radius: 20px;
      font-size: 0.7rem;
      margin-right: 8px;
    }
  }
}

// Hybrid Section (优化布局 + 新命令)
.hybrid-section {
  background: #0f172a;
  margin: 40px auto;
  border-radius: 48px;
  padding: 0;
  .hybrid-container {
    display: flex;
    align-items: center;
    gap: 48px;
    padding: 64px;
    @media (max-width: 768px) { flex-direction: column; padding: 40px; }
  }
  .hybrid-text {
    color: white;
    flex: 1;
    .hybrid-badge {
      background: rgba(255,255,255,0.2);
      padding: 4px 12px;
      border-radius: 40px;
      font-size: 0.7rem;
      font-weight: 600;
    }
    h2 { font-size: 2rem; margin: 20px 0 16px; font-weight: 800; }
    p { color: #cbd5e1; margin-bottom: 24px; }
    .hybrid-features div {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
      svg { color: #3b82f6; }
    }
  }
  .hybrid-visual {
    flex: 1;
    .code-block {
      background: #1e293b;
      border-radius: 20px;
      padding: 20px;
      pre {
        color: #94a3b8;
        font-family: 'Monaco', 'Menlo', monospace;
        margin: 0;
        white-space: pre-wrap;
        font-size: 0.8rem;
        line-height: 1.5;
      }
    }
  }
}

// CTA Card
.cta-section {
  .cta-card {
    background: linear-gradient(145deg, #ffffff, #f8fafc);
    border-radius: 48px;
    padding: 64px;
    text-align: center;
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
    border: 1px solid #eef2ff;
    h2 { font-size: 2rem; font-weight: 800; margin-bottom: 16px; }
    p { color: #475569; margin-bottom: 32px; }
    .cta-buttons {
      display: flex;
      gap: 16px;
      justify-content: center;
      .cta-btn {
        padding: 12px 28px;
        border-radius: 40px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        &.solid {
          background: #0f172a;
          color: white;
          border: none;
          &:hover { background: #1e293b; transform: scale(1.02); }
        }
        &.outline {
          background: transparent;
          border: 1px solid #cbd5e1;
          &:hover { background: #f1f5f9; }
        }
      }
    }
  }
}

// Footer
.footer-section {
  background: transparent;
  border-top: 1px solid #eef2ff;
  padding: 48px 24px 24px;
  max-width: 1280px;
  margin: 0 auto;
  .footer-main {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 40px;
    margin-bottom: 40px;
    .footer-brand {
      h3 { font-size: 1.5rem; font-weight: 800; }
      .admin-entrance {
        font-size: 0.7rem;
        color: #64748b;
        margin-top: 8px;
        cursor: pointer;
        &:hover { color: #2563eb; }
      }
    }
    .footer-links {
      display: flex;
      gap: 48px;
      .link-group {
        h4 { font-weight: 700; margin-bottom: 12px; }
        a {
          display: block;
          color: #475569;
          margin-bottom: 8px;
          cursor: pointer;
          &:hover { color: #0f172a; }
        }
      }
    }
  }
  .footer-copyright {
    text-align: center;
    font-size: 0.75rem;
    color: #94a3b8;
    padding-top: 24px;
    border-top: 1px solid #eef2ff;
  }
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(37,99,235,0.4); }
  70% { box-shadow: 0 0 0 8px rgba(37,99,235,0); }
  100% { box-shadow: 0 0 0 0 rgba(37,99,235,0); }
}
</style>