<template>
  <div class="hybrid-deployment">
    <!-- 左侧：三个特性卡片，垂直等分 -->
    <div class="features-minimal">
      <div class="feature-card">
        <div class="feature-icon">
          <i class="mdi mdi-lock-open-outline"></i>
        </div>
        <div class="feature-content">
          <strong>开源透明</strong>
          <span>代码完全开放，无供应商锁定</span>
        </div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">
          <i class="mdi mdi-server"></i>
        </div>
        <div class="feature-content">
          <strong>私有化部署</strong>
          <span>数据存储在您的服务器，安全合规</span>
        </div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">
          <i class="mdi mdi-cloud-sync"></i>
        </div>
        <div class="feature-content">
          <strong>混合模式</strong>
          <span>云端/自托管无缝切换，弹性伸缩</span>
        </div>
      </div>
    </div>

    <!-- 右侧：代码展示卡片 -->
    <div class="code-card">
      <div class="code-header">
        <div class="dot-group">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
        </div>
        <!-- <span class="code-label">terminal</span> -->
      </div>
      <div class="code-block">
        <pre><code ref="codeBlock" class="language-bash"># 克隆项目
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
      <!-- <div class="code-footer">
        <span>🚀 一键启动企业级环境</span>
        <span class="copy-hint">支持自托管 & 云部署</span>
      </div> -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import hljs from 'highlight.js/lib/core';
import bash from 'highlight.js/lib/languages/bash';

hljs.registerLanguage('bash', bash);

const codeBlock = ref<HTMLElement | null>(null);

onMounted(() => {
  if (codeBlock.value) {
    hljs.highlightElement(codeBlock.value);
  }
});
</script>

<style scoped lang="scss">
.hybrid-deployment {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 0.8fr 1fr;  /* 左侧宽度收窄 */
  gap: 32px;
  align-items: stretch;  /* 使左右两侧高度一致 */
}

/* 左侧容器：高度撑满，垂直均分三个卡片 */
.features-minimal {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 0;  /* 卡片之间无间隙，由内部 padding 控制视觉间距 */
}

/* 每个卡片均分剩余高度，且内容垂直居中 */
.feature-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 16px 18px;
  transition: all 0.2s ease;
  box-shadow: 0 8px 20px rgba(2,6,23,0.25);
  margin-bottom: 16px;  /* 卡片之间的间距，不破坏均分逻辑 */

  &:last-child {
    margin-bottom: 0;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px -6px rgba(0, 0, 0, 0.08);
    border-color: #cbd5e1;
  }

  .feature-icon {
    flex-shrink: 0;
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
    border-radius: 12px;
    color: #8dd6ff;
    font-size: 1.5rem;
  }

  .feature-content {
    flex: 1;

    strong {
      display: block;
      font-size: 1rem;
      font-weight: 700;
      color: #eef2ff;
      margin-bottom: 4px;
    }

    span {
      font-size: 0.8rem;
      color: #c7d2e0;
      line-height: 1.4;
    }
  }
}

/* 右侧代码卡片（保持原有风格） */
.code-card {
  background: rgba(255,255,255,0.04);
  border-radius: 18px;
  box-shadow: 0 12px 30px rgba(2,6,23,0.25);
  border: 1px solid rgba(255,255,255,0.06);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  height: fit-content;  /* 高度由内容决定，左侧会拉伸与之匹配 */

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 30px -12px rgba(0, 0, 0, 0.1);
  }

  .code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  background: rgba(255,255,255,0.02);
  border-bottom: 1px solid rgba(255,255,255,0.03);

    .dot-group {
      display: flex;
      gap: 8px;
      .dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        &.red { background: #ef4444; }
        &.yellow { background: #f59e0b; }
        &.green { background: #10b981; }
      }
    }

    .code-label {
      font-family: 'SimHei', 'Microsoft YaHei', sans-serif;
      font-size: 0.7rem;
      color: #475569;
    //   background: #ffffff;
      padding: 4px 12px;
      border-radius: 20px;
      letter-spacing: 0.5px;
    //   border: 1px solid #e2e8f0;
    }
  }

  .code-block {
  padding: 16px;
  background: rgba(255,255,255,0.02);
  overflow-x: auto;

    pre {
      margin: 0;
      font-family: 'Fira Code', 'Monaco', 'Menlo', monospace;
      font-size: 0.8rem;
      line-height: 1.6;
      code {
        background: transparent;
        padding: 0;
        border-radius: 0;
        font-weight: 400;
      }
    }

    &::-webkit-scrollbar {
      height: 6px;
    }
    &::-webkit-scrollbar-track {
      background: #f1f5f9;
      border-radius: 10px;
    }
    &::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 10px;
    }
  }

  .code-footer {
    display: flex;
    justify-content: space-between;
    padding: 10px 20px;
    background: #f8fafc;
    border-top: 1px solid #eef2ff;
    font-size: 0.7rem;
    color: #64748b;

    .copy-hint {
      color: #3b82f6;
      font-weight: 500;
    }
  }
}

/* 避免 highlight.js 的浅色主题在深色面板中出现白色背景重影 */
/* 使用深度穿透，确保 highlight.js 动态插入的 token 元素也被覆盖 */
.hybrid-deployment :deep(.hljs) {
  background: transparent !important;
  color: #e6eef8 !important;
}
.hybrid-deployment :deep(.hljs .hljs-comment),
.hybrid-deployment :deep(.hljs .hljs-quote) {
  color: #9aa6b4 !important;
  font-style: italic;
}

/* 常见 token 颜色覆盖（深色面板） */
.hybrid-deployment :deep(.hljs .hljs-keyword),
.hybrid-deployment :deep(.hljs .hljs-selector-tag),
.hybrid-deployment :deep(.hljs .hljs-subst) {
  color: #c084fc !important;
  font-weight: 600 !important;
}
.hybrid-deployment :deep(.hljs .hljs-number),
.hybrid-deployment :deep(.hljs .hljs-literal),
.hybrid-deployment :deep(.hljs .hljs-variable),
.hybrid-deployment :deep(.hljs .hljs-template-variable),
.hybrid-deployment :deep(.hljs .hljs-tag .hljs-attr) {
  color: #60a5fa !important;
}
.hybrid-deployment :deep(.hljs .hljs-string),
.hybrid-deployment :deep(.hljs .hljs-doctag) {
  color: #7dd3fc !important;
}
.hybrid-deployment :deep(.hljs .hljs-title),
.hybrid-deployment :deep(.hljs .hljs-section),
.hybrid-deployment :deep(.hljs .hljs-selector-id) {
  color: #93c5fd !important;
}
.hybrid-deployment :deep(.hljs .hljs-built_in),
.hybrid-deployment :deep(.hljs .hljs-builtin-name),
.hybrid-deployment :deep(.hljs .hljs-type) {
  color: #60a5fa !important;
}
.hybrid-deployment :deep(.hljs .hljs-attr),
.hybrid-deployment :deep(.hljs .hljs-symbol),
.hybrid-deployment :deep(.hljs .hljs-bullet),
.hybrid-deployment :deep(.hljs .hljs-link) {
  color: #fbbf24 !important;
}

/* 对 pre.hljs 和 code.hljs 也做显式透明覆盖，防止其他全局样式生效 */
.hybrid-deployment :deep(pre.hljs),
.hybrid-deployment :deep(code.hljs) {
  background: transparent !important;
  color: inherit !important;
}

/* 响应式：小屏幕改为上下布局 */
@media (max-width: 768px) {
  .hybrid-deployment {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .features-minimal {
    height: auto;
    gap: 16px;
  }

  .feature-card {
    flex: none;
    margin-bottom: 0;
  }
}
</style>