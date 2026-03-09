<template>
  <div class="step-container">
    <h3 class="step-title">请上传参考音频或使用麦克风录制</h3>

    <!-- 预设选择 -->
    <div class="preset-section">
      <el-button
        :icon="FolderOpened"
        @click="showPresetList = true"
        type="primary"
      >
        从收藏选择 ({{ presets.length }})
      </el-button>
    </div>

    <el-divider>或</el-divider>

    <el-tabs v-model="activeTab" class="audio-tabs">
      <el-tab-pane label="上传音频" name="upload">
        <el-upload
          class="audio-upload"
          drag
          :auto-upload="false"
          :show-file-list="false"
          accept="audio/*"
          @change="handleFileUpload"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽音频文件到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持的音频格式: WAV, MP3, M4A，时长限制在30秒以内
            </div>
          </template>
        </el-upload>

        <div v-if="audioFile" class="audio-preview">
          <audio :src="audioFile.url" controls />

          <div class="audio-actions">
            <el-button
              type="primary"
              size="small"
              :icon="Crop"
              @click="showTrimmer = true"
            >
              裁剪音频
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="clearAudio"
            >
              清除音频
            </el-button>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="录制音频" name="record">
        <div class="record-container">
          <el-button
            v-if="!isRecording"
            type="primary"
            size="large"
            @click="startRecording"
            :icon="Microphone"
          >
            开始录制
          </el-button>
          <el-button
            v-else
            type="danger"
            size="large"
            @click="stopRecording"
            :icon="VideoPause"
          >
            停止录制 ({{ recordingTime }}s)
          </el-button>

          <div v-if="recordedAudio" class="audio-preview">
            <audio :src="recordedAudio.url" controls />
            <div class="audio-info">
              <span>文件: {{ recordedAudio.file.name }}</span>
              <span>时长: {{ recordingTime }}秒</span>
              <span>大小: {{ (recordedAudio.file.size / 1024).toFixed(2) }}KB</span>
            </div>

            <div class="audio-actions">
              <el-button
                type="success"
                size="small"
                @click="downloadRecording"
              >
                下载WAV
              </el-button>
              <el-button
                type="primary"
                size="small"
                :icon="Crop"
                @click="showTrimmer = true"
              >
                裁剪音频
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="clearRecording"
              >
                清除录制
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <div class="instructions">
      <p><strong>提示：</strong></p>
      <ul>
        <li>可以从收藏选择已保存的音色预设</li>
        <li>或上传新的音频文件（WAV, MP3, M4A）</li>
        <li>或使用麦克风录制音频</li>
        <li>音频时长限制在30秒以内</li>
        <li>建议使用清晰、无背景噪音的语音</li>
      </ul>
    </div>

    <div class="nav-buttons">
      <el-button
        type="primary"
        size="large"
        :disabled="!hasAudio"
        @click="goNext"
      >
        下一步
      </el-button>
    </div>

    <!-- 音频裁剪对话框 -->
    <AudioTrimmer
      v-model="showTrimmer"
      :audio-url="currentAudioUrl"
      @confirm="handleTrimConfirm"
    />

    <!-- 预设列表对话框 -->
    <el-dialog
      v-model="showPresetList"
      title="我的音色收藏"
      width="900px"
    >
      <div v-if="isLoadingPresets" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="presets.length === 0" class="empty-state">
        <el-empty description="暂无收藏的音色，请先上传音频并保存预设">
          <el-button type="primary" @click="showPresetList = false">去上传音频</el-button>
        </el-empty>
      </div>

      <el-table v-else :data="presets" style="width: 100%">
        <el-table-column prop="name" label="预设名称" width="180" />
        <el-table-column label="参考文本" min-width="200">
          <template #default="{ row }">
            <div class="text-preview">{{ row.prompt_text }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="loadPreset(row)">
              使用
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled,
  Microphone,
  VideoPause,
  Crop,
  FolderOpened
} from '@element-plus/icons-vue'
import AudioTrimmer from './AudioTrimmer.vue'
import { presetApi, type VoicePreset } from '../api/preset'
import type { AudioFile } from '../types'

interface Emits {
  (e: 'next', audio: AudioFile): void
  (e: 'loadPreset', preset: VoicePreset): void
}

const emit = defineEmits<Emits>()

const activeTab = ref('upload')
const audioFile = ref<AudioFile | null>(null)
const recordedAudio = ref<AudioFile | null>(null)
const isRecording = ref(false)
const recordingTime = ref(0)
const mediaRecorder = ref<MediaRecorder | null>(null)
const recordingTimer = ref<number | null>(null)
const recordedChunks = ref<Blob[]>([])
const showTrimmer = ref(false)
const showPresetList = ref(false)
const presets = ref<VoicePreset[]>([])
const isLoadingPresets = ref(false)

const hasAudio = computed(() => audioFile.value || recordedAudio.value)
const currentAudioUrl = computed(() => {
  return (recordedAudio.value || audioFile.value)?.url || ''
})

onMounted(() => {
  loadPresets()
})

async function loadPresets() {
  try {
    isLoadingPresets.value = true
    presets.value = await presetApi.getPresets()
  } catch (error: any) {
    console.error('加载预设失败:', error)
  } finally {
    isLoadingPresets.value = false
  }
}

async function loadPreset(preset: VoicePreset) {
  showPresetList.value = false

  try {
    // 获取音频文件的完整 URL
    const audioUrl = presetApi.getPresetAudioUrl(preset.id)

    // 获取音频文件
    const response = await fetch(audioUrl)
    const blob = await response.blob()

    // 检查返回的数据格式
    let audioBlob: Blob
    if (response.headers.get('content-type')?.includes('application/json')) {
      // 如果返回的是 JSON，说明是 base64 格式
      const data = await response.json()
      const audioData = atob(data.audio_data)
      const bytes = new Uint8Array(audioData.length)
      for (let i = 0; i < audioData.length; i++) {
        bytes[i] = audioData.charCodeAt(i)
      }
      audioBlob = new Blob([bytes], { type: 'audio/wav' })
    } else {
      // 直接是二进制数据
      audioBlob = blob
    }

    const url = URL.createObjectURL(audioBlob)
    const file = new File([audioBlob], `preset_${preset.id}.wav`, { type: 'audio/wav' })

    audioFile.value = { file, url }

    ElMessage.success(`已加载预设: ${preset.name}`)

    // 触发加载预设事件，父组件会保存预设信息并跳转到步骤3
    emit('loadPreset', preset)
  } catch (error) {
    console.error('加载预设音频失败:', error)
    ElMessage.error('加载预设音频失败')
  }
}

function handleFileUpload(file: any) {
  const rawFile = file.raw
  if (!rawFile) return

  if (!rawFile.type.startsWith('audio/')) {
    ElMessage.error('请上传音频文件')
    return
  }

  const url = URL.createObjectURL(rawFile)
  audioFile.value = {
    file: rawFile,
    url
  }

  // 清除录制音频
  if (recordedAudio.value?.url) {
    URL.revokeObjectURL(recordedAudio.value.url)
    recordedAudio.value = null
  }

  const audio = new Audio(url)
  audio.addEventListener('loadedmetadata', () => {
    if (audio.duration > 30) {
      ElMessage.warning('音频时长超过30秒，建议裁剪后使用')
    }
  })
}

async function startRecording() {
  try {
    console.log('[录音] 开始初始化录音...')

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    console.log('[录音] 获取到音频流:', stream)

    // 检测浏览器支持的音频格式
    let mimeType = 'audio/webm'
    let fileExtension = 'webm'

    const supportedTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/ogg;codecs=opus'
    ]

    for (const type of supportedTypes) {
      if (MediaRecorder.isTypeSupported(type)) {
        mimeType = type
        if (type.includes('mp4')) fileExtension = 'mp4'
        if (type.includes('ogg')) fileExtension = 'ogg'
        console.log('[录音] 使用格式:', mimeType)
        break
      }
    }

    // 创建 MediaRecorder
    const options: MediaRecorderOptions = mimeType ? { mimeType } : {}
    mediaRecorder.value = new MediaRecorder(stream, options)
    console.log('[录音] MediaRecorder 创建成功:', mediaRecorder.value.mimeType)

    // 清空之前的录制数据
    recordedChunks.value = []
    console.log('[录音] 已清空之前的录制数据')

    // 设置数据可用事件处理器（必须在 start 之前）
    mediaRecorder.value.ondataavailable = (event) => {
      console.log('[录音] ondataavailable 触发, 数据大小:', event.data?.size)
      if (event.data && event.data.size > 0) {
        recordedChunks.value.push(event.data)
        console.log('[录音] 数据块已添加, 当前总块数:', recordedChunks.value.length)
      } else {
        console.warn('[录音] 收到空数据块')
      }
    }

    // 设置停止事件处理器
    mediaRecorder.value.onstop = async () => {
      console.log('[录音] onstop 触发')
      console.log('[录音] 总数据块数:', recordedChunks.value.length)

      // 计算总数据大小
      const totalSize = recordedChunks.value.reduce((sum, chunk) => sum + chunk.size, 0)
      console.log('[录音] 总数据大小:', totalSize, 'bytes')

      if (recordedChunks.value.length === 0 || totalSize === 0) {
        console.error('[录音] 错误: 没有录制到任何数据!')
        ElMessage.error('录音失败: 没有录制到数据，请重试')
        return
      }

      // 创建 blob
      const actualMimeType = mediaRecorder.value?.mimeType || 'audio/webm'
      const blob = new Blob(recordedChunks.value, { type: actualMimeType })
      console.log('[录音] Blob 创建成功, 大小:', blob.size, 'bytes')

      try {
        // 转换为 WAV 格式
        console.log('[录音] 开始转换为 WAV...')
        const wavBlob = await convertToWav(blob)
        console.log('[录音] WAV 转换成功, 大小:', wavBlob.size, 'bytes')

        const url = URL.createObjectURL(wavBlob)
        const file = new File([wavBlob], `recording_${Date.now()}.wav`, { type: 'audio/wav' })
        recordedAudio.value = { file, url }

        console.log('[录音] WAV 文件已创建:', { name: file.name, size: file.size, type: file.type })
        ElMessage.success(`录音完成，时长: ${recordingTime.value}秒`)
      } catch (error) {
        console.error('[录音] WAV 转换失败:', error)
        ElMessage.error('WAV 转换失败，请重试')
      }

      // 停止所有音频轨道
      stream.getTracks().forEach(track => track.stop())
      console.log('[录音] 音频轨道已停止')

      // 清除上传音频
      if (audioFile.value?.url) {
        URL.revokeObjectURL(audioFile.value.url)
        audioFile.value = null
      }
    }

    // 开始录制（不使用 timeslice 参数，让浏览器自动管理）
    mediaRecorder.value.start()
    console.log('[录音] 录制已开始')

    isRecording.value = true
    recordingTime.value = 0

    // 启动计时器
    recordingTimer.value = window.setInterval(() => {
      recordingTime.value++

      // 每5秒请求一次数据，确保不会丢失
      if (recordingTime.value % 5 === 0 && mediaRecorder.value?.state === 'recording') {
        console.log('[录音] 请求分段数据, 录制时长:', recordingTime.value)
        mediaRecorder.value.requestData()
      }

      if (recordingTime.value >= 30) {
        console.log('[录音] 达到最大时长，停止录制')
        stopRecording()
        ElMessage.warning('已达到最大录制时长30秒')
      }
    }, 1000)

  } catch (error: any) {
    console.error('[录音] 启动失败:', error)
    ElMessage.error(`无法访问麦克风: ${error.message || '请检查权限设置'}`)
    isRecording.value = false
  }
}

function stopRecording() {
  if (mediaRecorder.value && isRecording.value) {
    console.log('[录音] 准备停止录制...')

    // 请求最后一次数据确保不丢失
    if (mediaRecorder.value.state === 'recording') {
      console.log('[录音] 请求最后的数据段')
      mediaRecorder.value.requestData()
    }

    // 停止录制
    mediaRecorder.value.stop()
    console.log('[录音] MediaRecorder 已停止')

    // 清理计时器
    isRecording.value = false
    if (recordingTimer.value) {
      clearInterval(recordingTimer.value)
      recordingTimer.value = null
      console.log('[录音] 计时器已清理')
    }
  }
}

function clearAudio() {
  if (audioFile.value?.url) {
    URL.revokeObjectURL(audioFile.value.url)
  }
  audioFile.value = null
}

function clearRecording() {
  if (recordedAudio.value?.url) {
    URL.revokeObjectURL(recordedAudio.value.url)
  }
  recordedAudio.value = null
  recordedChunks.value = []
  recordingTime.value = 0
}

function downloadRecording() {
  if (!recordedAudio.value) return
  const url = URL.createObjectURL(recordedAudio.value.file)
  const a = document.createElement('a')
  a.href = url
  a.download = recordedAudio.value.file.name
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success(`已下载: ${recordedAudio.value.file.name}`)
}

function handleTrimConfirm(blob: Blob) {
  const url = URL.createObjectURL(blob)
  const file = new File([blob], 'trimmed_audio.wav', { type: 'audio/wav' })

  if (activeTab.value === 'upload') {
    if (audioFile.value?.url) {
      URL.revokeObjectURL(audioFile.value.url)
    }
    audioFile.value = { file, url }
  } else {
    if (recordedAudio.value?.url) {
      URL.revokeObjectURL(recordedAudio.value.url)
    }
    recordedAudio.value = { file, url }
  }

  ElMessage.success('音频裁剪成功')
}

function goNext() {
  const audio = recordedAudio.value || audioFile.value
  if (audio) {
    emit('next', audio)
  }
}

function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN')
  } catch {
    return dateString
  }
}

async function convertToWav(blob: Blob): Promise<Blob> {
  const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
  const arrayBuffer = await blob.arrayBuffer()
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)

  const numberOfChannels = audioBuffer.numberOfChannels
  const sampleRate = audioBuffer.sampleRate
  const format = 1
  const bitDepth = 16

  const bytesPerSample = bitDepth / 8
  const blockAlign = numberOfChannels * bytesPerSample

  const data = []
  for (let i = 0; i < audioBuffer.length; i++) {
    for (let channel = 0; channel < numberOfChannels; channel++) {
      const sample = audioBuffer.getChannelData(channel)[i]
      const int16 = Math.max(-1, Math.min(1, sample)) * 0x7FFF
      data.push(int16)
    }
  }

  const dataLength = data.length * bytesPerSample
  const buffer = new ArrayBuffer(44 + dataLength)
  const view = new DataView(buffer)

  const writeString = (offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i))
    }
  }

  writeString(0, 'RIFF')
  view.setUint32(4, 36 + dataLength, true)
  writeString(8, 'WAVE')
  writeString(12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, format, true)
  view.setUint16(22, numberOfChannels, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * blockAlign, true)
  view.setUint16(32, blockAlign, true)
  view.setUint16(34, bitDepth, true)
  writeString(36, 'data')
  view.setUint32(40, dataLength, true)

  let offset = 44
  for (let i = 0; i < data.length; i++) {
    view.setInt16(offset, data[i], true)
    offset += 2
  }

  return new Blob([buffer], { type: 'audio/wav' })
}
</script>

<style scoped>
/* ========================================
   Step Container - Anthropic Brand Styling
   ======================================== */

.step-container {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}

.step-title {
  font-family: var(--font-heading);
  font-size: 24px;
  font-weight: 600;
  margin-bottom: var(--spacing-lg);
  text-align: center;
  color: var(--color-dark);
  letter-spacing: -0.01em;
}

/* ========================================
   Preset Section
   ======================================== */

.preset-section {
  display: flex;
  justify-content: center;
  margin-bottom: var(--spacing-lg);
}

/* ========================================
   Audio Tabs
   ======================================== */

.audio-tabs {
  margin-bottom: var(--spacing-lg);
}

.audio-upload {
  margin-bottom: var(--spacing-md);
}

/* ========================================
   Audio Preview
   ======================================== */

.audio-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-md);
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-md);
  margin-top: var(--spacing-md);
  border: 1px solid var(--border-color);
}

.audio-preview audio {
  width: 100%;
  max-width: 400px;
  border-radius: var(--radius-sm);
}

.audio-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: 12px;
}

/* ========================================
   Record Container
   ======================================== */

.record-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-xl);
}

/* ========================================
   Instructions Box
   ======================================== */

.instructions {
  padding: var(--spacing-md);
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-lg);
  border-left: 3px solid var(--color-accent-blue);
}

.instructions p {
  font-family: var(--font-body);
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--text-primary);
}

.instructions strong {
  font-family: var(--font-heading);
  color: var(--color-accent-blue);
}

.instructions ul {
  margin: 0;
  padding-left: 20px;
}

.instructions li {
  margin-bottom: 4px;
  color: var(--text-secondary);
}

/* ========================================
   Navigation Buttons
   ======================================== */

.nav-buttons {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
}

/* ========================================
   Text Preview
   ======================================== */

.text-preview {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-secondary);
}

/* ========================================
   Empty & Loading States
   ======================================== */

.empty-state,
.loading-state {
  padding: 40px 0;
}

/* ========================================
   Element Plus Overrides
   ======================================== */

/* Upload drag area */
:deep(.el-upload-dragger) {
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

:deep(.el-upload-dragger:hover) {
  border-color: var(--color-accent-orange);
  background-color: var(--bg-tertiary);
}

/* Dialog */
:deep(.el-dialog) {
  border-radius: var(--radius-xl);
}

:deep(.el-dialog__title) {
  font-family: var(--font-heading);
  font-weight: 600;
}

/* Tabs */
:deep(.el-tabs__nav-wrap::after) {
  background-color: var(--border-color);
}

:deep(.el-tabs__item) {
  font-family: var(--font-heading);
}

:deep(.el-tabs__item.is-active) {
  color: var(--color-accent-orange);
}

:deep(.el-tabs__active-bar) {
  background-color: var(--color-accent-orange);
}

/* Divider */
:deep(.el-divider__text) {
  font-family: var(--font-body);
  color: var(--text-secondary);
  background-color: transparent;
}

:deep(.el-divider) {
  border-top-color: var(--border-color);
}
</style>
