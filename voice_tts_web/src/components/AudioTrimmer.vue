<template>
  <el-dialog
    v-model="visible"
    title="裁剪音频"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="trimmer-container">
      <div class="audio-preview">
        <audio ref="audioRef" :src="audioUrl" controls @loadedmetadata="onAudioLoaded" />
        <p class="duration-info">总时长: {{ formatTime(duration) }}</p>
      </div>

      <el-form label-width="100px">
        <el-form-item label="开始时间(秒)">
          <el-input-number
            v-model="manualStart"
            :min="0"
            :max="duration"
            :precision="2"
            :step="0.1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="结束时间(秒)">
          <el-input-number
            v-model="manualEnd"
            :min="0"
            :max="duration"
            :precision="2"
            :step="0.1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="裁剪时长">
          <span class="duration-display">{{ formatTime(manualEnd - manualStart) }}</span>
        </el-form-item>
      </el-form>

      <div v-if="warning" class="warning-message">
        <el-alert :title="warning" type="warning" :closable="false" show-icon />
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleConfirm" :disabled="!isValidRange">
        确认裁剪
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  modelValue: boolean
  audioUrl: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', blob: Blob): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const audioRef = ref<HTMLAudioElement>()
const duration = ref(0)
const manualStart = ref(0)
const manualEnd = ref(0)
const warning = ref('')

const isValidRange = computed(() => {
  return manualEnd.value - manualStart.value >= 0.5
})

watch(() => props.audioUrl, () => {
  if (props.audioUrl) {
    resetValues()
  }
})

watch(visible, (val) => {
  if (val && props.audioUrl) {
    resetValues()
  }
})

watch([manualStart, manualEnd], () => {
  validateTimes()
})

function onAudioLoaded() {
  if (audioRef.value) {
    duration.value = audioRef.value.duration
    manualEnd.value = duration.value
  }
}

function resetValues() {
  manualStart.value = 0
  manualEnd.value = duration.value
  warning.value = ''
}

function validateTimes() {
  if (manualStart.value >= manualEnd.value) {
    warning.value = '开始时间必须小于结束时间'
    return
  }

  const range = manualEnd.value - manualStart.value
  if (range < 0.5) {
    warning.value = '裁剪时长不能少于 0.5 秒'
    return
  }

  if (range > duration.value) {
    warning.value = '裁剪时长不能超过音频总时长'
    return
  }

  warning.value = ''
}

async function handleConfirm() {
  if (!isValidRange.value) {
    ElMessage.warning('裁剪时长不能少于 0.5 秒')
    return
  }

  try {
    const start = manualStart.value
    const end = manualEnd.value

    // 使用 Web Audio API 裁剪音频
    const audioContext = new AudioContext()
    const response = await fetch(props.audioUrl)
    const arrayBuffer = await response.arrayBuffer()
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)

    const sampleRate = audioBuffer.sampleRate
    const startSample = Math.floor(start * sampleRate)
    const endSample = Math.floor(end * sampleRate)
    const sampleCount = endSample - startSample

    const offlineContext = new OfflineAudioContext(
      audioBuffer.numberOfChannels,
      sampleCount,
      sampleRate
    )

    const trimmedBuffer = offlineContext.createBuffer(
      audioBuffer.numberOfChannels,
      sampleCount,
      sampleRate
    )

    for (let channel = 0; channel < audioBuffer.numberOfChannels; channel++) {
      const channelData = audioBuffer.getChannelData(channel)
      const trimmedData = trimmedBuffer.getChannelData(channel)
      for (let i = 0; i < sampleCount; i++) {
        trimmedData[i] = channelData[startSample + i]
      }
    }

    // 转换为 WAV 格式
    const wavBlob = audioBufferToWav(trimmedBuffer)

    emit('confirm', wavBlob)
    handleClose()
    ElMessage.success('音频裁剪成功')
  } catch (error) {
    console.error('裁剪音频失败:', error)
    ElMessage.error('裁剪音频失败，请重试')
  }
}

function audioBufferToWav(buffer: AudioBuffer): Blob {
  const length = buffer.length * buffer.numberOfChannels * 2 + 44
  const arrayBuffer = new ArrayBuffer(length)
  const view = new DataView(arrayBuffer)
  let offset = 0

  // 写入 WAV 头
  writeString(view, offset, 'RIFF')
  offset += 4
  view.setUint32(offset, length - 8, true)
  offset += 4
  writeString(view, offset, 'WAVE')
  offset += 4
  writeString(view, offset, 'fmt ')
  offset += 4
  view.setUint32(offset, 16, true)
  offset += 4
  view.setUint16(offset, 1, true)
  offset += 2
  view.setUint16(offset, buffer.numberOfChannels, true)
  offset += 2
  view.setUint32(offset, buffer.sampleRate, true)
  offset += 4
  view.setUint32(offset, buffer.sampleRate * 2 * buffer.numberOfChannels, true)
  offset += 4
  view.setUint16(offset, buffer.numberOfChannels * 2, true)
  offset += 2
  view.setUint16(offset, 16, true)
  offset += 2
  writeString(view, offset, 'data')
  offset += 4
  view.setUint32(offset, length - offset - 4, true)
  offset += 4

  // 写入音频数据
  for (let i = 0; i < buffer.length; i++) {
    for (let channel = 0; channel < buffer.numberOfChannels; channel++) {
      const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[i]))
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true)
      offset += 2
    }
  }

  return new Blob([arrayBuffer], { type: 'audio/wav' })
}

function writeString(view: DataView, offset: number, string: string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i))
  }
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  const ms = Math.floor((seconds % 1) * 100)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`
}

function handleClose() {
  visible.value = false
}
</script>

<style scoped>
/* ========================================
   Audio Trimmer - Anthropic Brand Styling
   ======================================== */

.trimmer-container {
  padding: var(--spacing-md) 0;
}

.audio-preview {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-lg);
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid var(--border-color);
}

.audio-preview audio {
  width: 100%;
  max-width: 400px;
  margin-bottom: 12px;
  border-radius: var(--radius-sm);
}

.duration-info {
  margin: 0;
  font-family: var(--font-heading);
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.duration-display {
  font-family: var(--font-heading);
  font-size: 16px;
  font-weight: 600;
  color: var(--color-accent-orange);
}

.warning-message {
  margin-top: var(--spacing-md);
}

/* ========================================
   Element Plus Overrides
   ======================================== */

/* Form labels */
:deep(.el-form-item__label) {
  font-family: var(--font-heading);
  font-weight: 500;
  color: var(--text-secondary);
}

/* Dialog */
:deep(.el-dialog) {
  border-radius: var(--radius-xl);
}

:deep(.el-dialog__title) {
  font-family: var(--font-heading);
  font-weight: 600;
}

/* Input number */
:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-input__inner) {
  font-family: var(--font-body);
}
</style>
