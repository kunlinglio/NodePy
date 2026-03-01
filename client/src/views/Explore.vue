<script lang='ts' setup>
import { ref } from 'vue'
//@ts-ignore
import SvgIcon from '@jamescoyle/vue-icon'
import {
  mdiPlayCircleOutline,
  mdiBookOpenPageVariant,
  mdiCloudDownloadOutline,
  mdiCheckCircleOutline,
  mdiLightbulb,
} from '@mdi/js'
import { usePageStore } from '@/stores/pageStore'

const pageStore = usePageStore()

// 视频教程数据
const videos = ref([
  {
    id: 1,
    title: '快速开始',
    description: '5 分钟学会 NodePy 基础操作，了解节点拖拽、连接和执行的基本流程。',
    duration: '5:30',
    thumbnail: '📹',
    difficulty: 'beginner',
    views: 1200
  },
  {
    id: 2,
    title: '表格数据处理',
    description: '深入学习如何使用 Pandas 节点进行数据清洗、过滤和转换。',
    duration: '12:45',
    thumbnail: '📊',
    difficulty: 'intermediate',
    views: 856
  },
  {
    id: 3,
    title: '金融数据分析',
    description: '从零开始构建一个完整的量化分析工作流，包括数据获取、计算和回测。',
    duration: '28:15',
    thumbnail: '📈',
    difficulty: 'advanced',
    views: 2341
  },
  {
    id: 4,
    title: '图表与可视化',
    description: '掌握各种图表节点的使用方式，创建专业级的数据可视化设计。',
    duration: '15:20',
    thumbnail: '🎨',
    difficulty: 'intermediate',
    views: 945
  }
])

// 文档数据
const docs = ref([
  {
    id: 1,
    title: '用户指南',
    description: '完整的 NodePy 使用指南，涵盖从入门到精通的全套教程。',
    icon: mdiBookOpenPageVariant,
    category: 'guide',
    pages: 45,
    updated: '2024-02-28'
  },
  {
    id: 2,
    title: '节点参考',
    description: '所有节点的详细说明，包括参数配置、输入输出类型和使用示例。',
    icon: mdiCloudDownloadOutline,
    category: 'reference',
    pages: 120,
    updated: '2024-02-25'
  },
  {
    id: 3,
    title: '常见问题',
    description: '常见问题解答，快速解决您在使用过程中遇到的问题。',
    icon: mdiLightbulb,
    category: 'faq',
    pages: 28,
    updated: '2024-02-20'
  },
  {
    id: 4,
    title: 'API 文档',
    description: '开发者 API 文档，用于集成和扩展 NodePy 功能。',
    icon: mdiCheckCircleOutline,
    category: 'api',
    pages: 87,
    updated: '2024-02-15'
  }
])

const difficultyLabels = {
  beginner: '初级',
  intermediate: '中级',
  advanced: '进阶'
}

const difficultyColors = {
  beginner: '#10b981',
  intermediate: '#f59e0b',
  advanced: '#ef4444'
}

// pageStore.setCurrentPage('Explore')
</script>
<template>
    <div class="explore-container">
      <!-- 背景装饰元素 -->
      <div class="background-elements">
        <div class="bg-circle circle-1"></div>
        <div class="bg-circle circle-2"></div>
        <div class="bg-circle circle-3"></div>
      </div>

      <!-- 主内容区 -->
      <div class="explore-content">
        <!-- 视频教程部分 -->
        <div class="section video-section">
          <div class="section-header">
            <h2 class="section-title">
              <svg-icon :path="mdiPlayCircleOutline" :size="32" type="mdi" class="title-icon"></svg-icon>
              视频教程
            </h2>
            <p class="section-subtitle">从入门到精通，通过视频快速学习 NodePy</p>
          </div>

          <div class="videos-grid">
            <div
              v-for="video in videos"
              :key="video.id"
              class="video-card"
            >
              <div class="video-thumbnail">
                <span class="emoji">{{ video.thumbnail }}</span>
                <div class="video-overlay">
                  <div class="play-btn">
                    <svg-icon :path="mdiPlayCircleOutline" :size="48" type="mdi"></svg-icon>
                  </div>
                </div>
                <div class="video-duration">{{ video.duration }}</div>
                <div class="difficulty-badge" :style="{ backgroundColor: difficultyColors[video.difficulty] }">
                  {{ difficultyLabels[video.difficulty] }}
                </div>
              </div>
              <div class="video-info">
                <h3 class="video-title">{{ video.title }}</h3>
                <p class="video-description">{{ video.description }}</p>
                <div class="video-meta">
                  <span class="views">👁️ {{ video.views }} 次观看</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 文档教程部分 -->
        <div class="section doc-section">
          <div class="section-header">
            <h2 class="section-title">
              <svg-icon :path="mdiBookOpenPageVariant" :size="32" type="mdi" class="title-icon"></svg-icon>
              文档教程
            </h2>
            <p class="section-subtitle">详细的参考文档，帮助您深入了解每个功能的细节</p>
          </div>

          <div class="docs-grid">
            <div
              v-for="doc in docs"
              :key="doc.id"
              class="doc-card"
            >
              <div class="doc-header">
                <div class="doc-icon">
                  <svg-icon :path="doc.icon" :size="28" type="mdi"></svg-icon>
                </div>
                <div class="doc-meta">
                  <span class="doc-category">{{ doc.category.toUpperCase() }}</span>
                  <span class="doc-pages">{{ doc.pages }} 页</span>
                </div>
              </div>
              <h3 class="doc-title">{{ doc.title }}</h3>
              <p class="doc-description">{{ doc.description }}</p>
              <div class="doc-footer">
                <span class="updated">更新于 {{ doc.updated }}</span>
                <button class="read-btn">立即阅读</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 关于我们部分 -->
        <div class="section about-section">
          <div class="about-container">
            <div class="about-content">
              <h2 class="about-title">关于 NodePy</h2>
              <p class="about-text">
                NodePy 是一个专为金融数据分析设计的可视化编程平台。我们致力于让数据分析变得更加简单、高效、有趣。
              </p>
              <p class="about-text">
                无论您是初学者还是专业分析师，NodePy 都能为您提供强大的工具和流畅的体验，让您专注于数据本身，而不是代码的复杂性。
              </p>

              <div class="about-features">
                <div class="about-feature-item">
                  <div class="feature-number">7+</div>
                  <p>数据类型支持</p>
                </div>
                <div class="about-feature-item">
                  <div class="feature-number">50+</div>
                  <p>内置节点组件</p>
                </div>
                <div class="about-feature-item">
                  <div class="feature-number">100%</div>
                  <p>免费开源</p>
                </div>
              </div>
            </div>

            <div class="about-illustration">
              <div class="illustration-item">
                <span class="illus-emoji">🚀</span>
                <p>快速开始</p>
              </div>
              <div class="illustration-item">
                <span class="illus-emoji">🎯</span>
                <p>精准控制</p>
              </div>
              <div class="illustration-item">
                <span class="illus-emoji">📊</span>
                <p>强大分析</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>
<style lang='scss' scoped>
@use '@/common/global.scss' as *;
@use '@/common/node.scss' as *;

.explore-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  width: 100%;
  min-height: 0;
  overflow-x: hidden;
  background-color: $background-color;
  user-select: none;
}

.background-elements {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;

  .bg-circle {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    opacity: 0.6;
  }

  .circle-1 {
    width: 400px;
    height: 400px;
    top: -100px;
    right: -100px;
    background: rgba($stress-color, 0.15);
  }

  .circle-2 {
    width: 300px;
    height: 300px;
    bottom: 100px;
    left: -50px;
    background: rgba($compute-node-color, 0.15);
  }

  .circle-3 {
    width: 200px;
    height: 200px;
    top: 30%;
    left: 20%;
    background: rgba($visualize-node-color, 0.1);
  }
}

.explore-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  z-index: 1;
  position: relative;
  overflow-y: auto;
}

.section {
  width: 100%;
  padding: 80px 40px;
  box-sizing: border-box;
  max-width: 1500px;
  margin: 0 auto;

  @media (max-width: 768px) {
    padding: 50px 20px;
  }
}

.section-header {
  text-align: center;
  margin-bottom: 60px;

  .section-title {
    font-size: 32px;
    font-weight: 800;
    color: #333;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;

    .title-icon {
      color: $stress-color;
      opacity: 0.8;
    }
  }

  .section-subtitle {
    font-size: 18px;
    color: #666;
  }
}

// 视频教程部分
.video-section {
  min-height: auto;

  .videos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 30px;
  }

  .video-card {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    transition: all 0.3s ease;
    border: 1px solid transparent;
    display: flex;
    flex-direction: column;

    &:hover {
      transform: translateY(-8px);
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
      border-color: rgba($stress-color, 0.2);

      .video-overlay {
        opacity: 1;
      }

      .play-btn {
        transform: scale(1.1);
      }
    }

    .video-thumbnail {
      position: relative;
      width: 100%;
      height: 180px;
      background: linear-gradient(135deg, rgba($stress-color, 0.1), rgba($compute-node-color, 0.1));
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;

      .emoji {
        font-size: 64px;
        opacity: 0.5;
      }

      .video-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: all 0.3s ease;
      }

      .play-btn {
        width: 60px;
        height: 60px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        color: $stress-color;
      }

      .video-duration {
        position: absolute;
        bottom: 12px;
        right: 12px;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
      }

      .difficulty-badge {
        position: absolute;
        top: 12px;
        right: 12px;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
      }
    }

    .video-info {
      padding: 20px;
      flex: 1;
      display: flex;
      flex-direction: column;

      .video-title {
        font-size: 16px;
        font-weight: 700;
        color: #333;
        margin-bottom: 8px;
        line-height: 1.4;
      }

      .video-description {
        font-size: 13px;
        color: #666;
        line-height: 1.5;
        margin-bottom: 12px;
        flex: 1;
      }

      .video-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 12px;
        color: #999;

        .views {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }
  }
}

// 文档教程部分
.doc-section {
  background: rgba($stress-color, 0.02);
  min-height: auto;

  .docs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 30px;
  }

  .doc-card {
    background: white;
    border-radius: 12px;
    padding: 28px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    transition: all 0.3s ease;
    border: 1px solid transparent;
    display: flex;
    flex-direction: column;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
      border-color: rgba($stress-color, 0.2);
    }

    .doc-header {
      display: flex;
      align-items: flex-start;
      gap: 16px;
      margin-bottom: 16px;

      .doc-icon {
        width: 50px;
        height: 50px;
        border-radius: 10px;
        background: linear-gradient(135deg, rgba($stress-color, 0.2), rgba($compute-node-color, 0.2));
        display: flex;
        align-items: center;
        justify-content: center;
        color: $stress-color;
        flex-shrink: 0;
      }

      .doc-meta {
        display: flex;
        flex-direction: column;
        gap: 4px;
        flex: 1;

        .doc-category {
          font-size: 11px;
          font-weight: 700;
          color: $stress-color;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .doc-pages {
          font-size: 12px;
          color: #999;
        }
      }
    }

    .doc-title {
      font-size: 18px;
      font-weight: 700;
      color: #333;
      margin-bottom: 10px;
    }

    .doc-description {
      font-size: 13px;
      color: #666;
      line-height: 1.6;
      margin-bottom: 16px;
      flex: 1;
    }

    .doc-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;

      .updated {
        font-size: 12px;
        color: #999;
      }

      .read-btn {
        background: none;
        border: none;
        color: $stress-color;
        font-weight: 600;
        cursor: pointer;
        font-size: 13px;
        padding: 0;
        transition: all 0.2s ease;

        &:hover {
          transform: translateX(4px);
        }
      }
    }
  }
}

// 关于我们部分
.about-section {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;

  .about-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 80px;
    background: white;
    border-radius: 20px;
    padding: 60px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);

    @media (max-width: 992px) {
      flex-direction: column;
      gap: 40px;
      padding: 40px;
    }

    .about-content {
      flex: 1;

      .about-title {
        font-size: 32px;
        font-weight: 900;
        color: #333;
        margin-bottom: 24px;
      }

      .about-text {
        font-size: 16px;
        line-height: 1.8;
        color: #666;
        margin-bottom: 20px;
      }

      .about-features {
        display: flex;
        gap: 40px;
        margin-top: 40px;

        @media (max-width: 992px) {
          flex-wrap: wrap;
          gap: 30px;
        }

        .about-feature-item {
          text-align: center;
          flex: 1;
          min-width: 120px;

          .feature-number {
            font-size: 32px;
            font-weight: 900;
            color: $stress-color;
            margin-bottom: 8px;
          }

          p {
            font-size: 14px;
            color: #666;
            font-weight: 600;
          }
        }
      }
    }

    .about-illustration {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 40px;
      flex-wrap: wrap;

      .illustration-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        text-align: center;

        .illus-emoji {
          font-size: 64px;
          filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
        }

        p {
          font-size: 14px;
          font-weight: 700;
          color: #333;
        }
      }
    }
  }
}
</style>