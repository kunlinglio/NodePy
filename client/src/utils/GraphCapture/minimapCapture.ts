import { useGraphStore } from '@/stores/graphStore';

/**
 * SVG 转 PNG 的轻量级方法 - 直接导出SVG为图片，性能远优于 html2canvas
 */
const svgToPng = async (svgElement: SVGSVGElement, width: number, height: number): Promise<string | null> => {
  try {
    // 创建Canvas
    const canvas = document.createElement('canvas')
    canvas.width = width * 2 // 高分辨率
    canvas.height = height * 2
    const ctx = canvas.getContext('2d')
    if (!ctx) return null

    // 填充白色背景
    ctx.fillStyle = '#f6f9fb'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // 获取SVG的XML
    const svgString = new XMLSerializer().serializeToString(svgElement)
    const blob = new Blob([svgString], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)

    // 创建图像并绘制到Canvas
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
        URL.revokeObjectURL(url)
        resolve(canvas.toDataURL('image/png'))
      }
      img.onerror = () => {
        URL.revokeObjectURL(url)
        resolve(null)
      }
      img.src = url
    })
  } catch (error) {
    return null
  }
}

/**
 * 处理小地图SVG样式的虚拟处理（创建临时style元素，不修改原DOM）
 */
const processMinimapSvgStyle = (svgElement: SVGSVGElement, tempContainer: HTMLElement): void => {
  // 使用 CSS 而不是逐个修改元素属性，性能更好
  const style = document.createElement('style')
  style.textContent = `
    .temp-minimap .vue-flow_minimap-node { fill: #555555; stroke: #222222; stroke-width: 1.5; }
    .temp-minimap .vue-flow_minimap-node rect { fill: #555555; stroke: #222222; stroke-width: 1.5; }
    .temp-minimap path { stroke: #333333; stroke-width: 2; }
    .temp-minimap svg { background: #f6f9fb; }
    .temp-minimap .vue-flow__minimap-mask,
    .temp-minimap .vue-flow__minimap-background { display: none; }
  `
  tempContainer.appendChild(style)
  tempContainer.classList.add('temp-minimap')
}

/**
 * 简化版截图 - 直接导出SVG为PNG，性能最优
 */
const captureMinimapSimple = async (miniMapElement: HTMLElement): Promise<string | null> => {
  try {
    const svgElement = miniMapElement.querySelector('svg') as SVGSVGElement
    if (!svgElement) return null

    // 浅度克隆SVG
    const clonedSvg = svgElement.cloneNode(true) as SVGSVGElement

    // 使用CSS样式处理，性能优于逐元素修改
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
    const style = document.createElementNS('http://www.w3.org/2000/svg', 'style')
    style.textContent = `
      .vue-flow_minimap-node rect { fill: #555555; stroke: #222222; stroke-width: 1.5; }
      path { stroke: #333333; stroke-width: 2; }
      .vue-flow__minimap-mask { display: none; }
      .vue-flow__minimap-background { display: none; }
    `
    defs.appendChild(style)
    clonedSvg.insertBefore(defs, clonedSvg.firstChild)

    // 设置背景
    const bgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
    bgRect.setAttribute('width', '100%')
    bgRect.setAttribute('height', '100%')
    bgRect.setAttribute('fill', '#f6f9fb')
    clonedSvg.insertBefore(bgRect, clonedSvg.firstChild)

    const imageData = await svgToPng(clonedSvg, 800, 450)
    return imageData
  } catch (error) {
    return null
  }
}

/**
 * 小地图截图功能 - 优化版本，去除html2canvas，使用SVG直接转PNG
 */
export const captureMiniMap = async (vueFlowRef: any): Promise<string | null> => {
  if (!vueFlowRef) {
    return null
  }

  try {
    // 获取小地图元素
    const miniMapElement = vueFlowRef.querySelector('.vue-flow__minimap') as HTMLElement
    if (!miniMapElement) {
      return null
    }

    // 检查是否存在节点，如果没有节点则直接返回null
    const graphStore = useGraphStore()
    if (graphStore.nodes.length === 0) {
      return null
    }

    // 直接使用简化版截图（性能最优）
    const imageData = await captureMinimapSimple(miniMapElement)

    if (imageData) {
      const base64String = imageData.replace(/^data:image\/\w+;base64,/, '')
      return base64String
    }

    return null
  } catch (error) {
    return null
  }
}

/**
 * 保存截图到本地
 */
export const saveMinimapScreenshot = (imageData: string, projectId: string): void => {
  try {
    const link = document.createElement('a')
    link.href = imageData
    link.download = `minimap-capture-${projectId}-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

  } catch (error) {

  }
}

/**
 * 自动截图并返回 Base64 字符串
 */
export const autoCaptureMinimap = async (vueFlowRef: any): Promise<string | null> => {
  try {
    // 直接调用，无需多余等待
    const base64String = await captureMiniMap(vueFlowRef)
    return base64String || null
  } catch (error) {
    return null
  }
}
