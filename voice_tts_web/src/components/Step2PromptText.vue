<template>
  <div class="step-container">
    <h3 class="step-title">请输入参考音频对应的文字内容</h3>

    <!-- 预设保存 -->
    <div class="preset-section">
      <el-button
        :icon="Star"
        @click="showSaveDialog = true"
        type="warning"
        :disabled="!canSavePreset"
      >
        保存为预设
      </el-button>

      <el-tooltip content="保存当前音频和文本，方便下次使用" placement="top">
        <el-icon class="info-icon"><InfoFilled /></el-icon>
      </el-tooltip>
    </div>

    <div v-if="referenceAudio" class="audio-preview">
      <p class="preview-label">已上传的参考音频</p>
      <audio :src="referenceAudio.url" controls />
    </div>

    <el-input
      v-model="promptText"
      type="textarea"
      :rows="8"
      placeholder="请输入上传的参考音频对应的文字内容，或点击下方按钮自动识别"
      maxlength="500"
      show-word-limit
    />

    <div class="action-buttons">
      <el-button
        v-if="asrEnabled"
        type="primary"
        @click="handleASR"
        :loading="isASRLoading"
      >
        提取音频文字
      </el-button>
      <el-button @click="clearText">清空</el-button>
    </div>

    <div class="instructions">
      <p><strong>提示：</strong></p>
      <ul>
        <li v-if="asrEnabled">您可以手动输入文字内容，或点击"提取音频文字"按钮自动识别</li>
        <li v-else>请手动输入参考音频对应的文字内容</li>
        <li>此文本将用于帮助AI学习声音特征</li>
        <li>填写完文本后，可以保存为预设以便下次使用</li>
      </ul>
    </div>

    <div class="nav-buttons">
      <el-button size="large" @click="goPrev">上一步</el-button>
      <el-button
        type="primary"
        size="large"
        :disabled="!canGoNext"
        @click="goNext"
      >
        下一步
      </el-button>
    </div>

    <!-- 保存预设对话框 -->
    <el-dialog
      v-model="showSaveDialog"
      title="保存音色预设"
      width="400px"
    >
      <el-form :model="presetForm" label-width="80px">
        <el-form-item label="预设名称">
          <el-input
            v-model="presetForm.name"
            placeholder="请输入预设名称"
            maxlength="50"
            show-word-limit
            autofocus
          />
        </el-form-item>

        <el-alert
          title="将保存当前音频和文本作为预设"
          type="info"
          :closable="false"
          show-icon
          style="margin-top: 16px"
        />
      </el-form>

      <template #footer>
        <el-button @click="showSaveDialog = false">取消</el-button>
        <el-button type="primary" @click="savePreset" :loading="isSaving" :disabled="!presetForm.name.trim()">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Star, InfoFilled } from '@element-plus/icons-vue'
import { presetApi } from '../api/preset'
import type { AudioFile } from '../types'

interface Props {
  referenceAudio: AudioFile | null
  asrEnabled: boolean
  initialText?: string
}

interface Emits {
  (e: 'prev'): void
  (e: 'next', text: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const promptText = ref(props.initialText || '')
const isASRLoading = ref(false)
const showSaveDialog = ref(false)
const presetForm = ref({
  name: ''
})
const isSaving = ref(false)

// 监听 initialText 变化
watch(() => props.initialText, (newText) => {
  if (newText && !promptText.value) {
    promptText.value = newText
  }
})

const canGoNext = computed(() => promptText.value.trim().length > 0)
const canSavePreset = computed(() => {
  return props.referenceAudio && props.referenceAudio.file && promptText.value.trim().length > 0
})

async function savePreset() {
  const name = presetForm.value.name.trim()

  if (!name) {
    ElMessage.warning('请输入预设名称')
    return
  }

  if (!props.referenceAudio?.file) {
    ElMessage.warning('请先上传音频文件')
    return
  }

  if (!promptText.value.trim()) {
    ElMessage.warning('请先输入参考文本')
    return
  }

  try {
    isSaving.value = true
    await presetApi.createPreset({
      name,
      prompt_text: promptText.value.trim(),
      audio: props.referenceAudio.file
    })

    ElMessage.success('保存成功')
    showSaveDialog.value = false
    presetForm.value.name = ''
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    isSaving.value = false
  }
}

async function handleASR() {
  if (!props.referenceAudio) {
    ElMessage.warning('请先上传或录制参考音频')
    return
  }

  isASRLoading.value = true
  try {
    // TODO: 调用 ASR API
    // const result = await ttsApi.transcribe({ audio_path: props.referenceAudio.file })
    // promptText.value = result.text

    // 模拟 ASR 调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    promptText.value = "这是一个模拟的ASR识别结果，请替换为实际的API调用。"

    ElMessage.success('音频文字提取成功')
  } catch (error: any) {
    ElMessage.error(error.message || '音频文字提取失败')
  } finally {
    isASRLoading.value = false
  }
}

function clearText() {
  promptText.value = ''
}

function goPrev() {
  emit('prev')
}

function goNext() {
  emit('next', promptText.value.trim())
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
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: 20px;
  padding: var(--spacing-md);
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-warning);
}

.info-icon {
  color: var(--color-mid-gray);
  cursor: help;
  transition: color var(--transition-fast);
}

.info-icon:hover {
  color: var(--color-accent-orange);
}

/* ========================================
   Audio Preview
   ======================================== */

.audio-preview {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.preview-label {
  margin: 0 0 12px 0;
  font-family: var(--font-heading);
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 14px;
}

.audio-preview audio {
  width: 100%;
  max-width: 400px;
  border-radius: var(--radius-sm);
}

/* ========================================
   Action Buttons
   ======================================== */

.action-buttons {
  display: flex;
  gap: var(--spacing-sm);
  margin: var(--spacing-md) 0;
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
   Element Plus Overrides
   ======================================== */

/* Textarea */
:deep(.el-textarea__inner) {
  font-family: var(--font-body);
  font-size: 15px;
  line-height: 1.7;
  border-color: var(--border-color);
}

:deep(.el-textarea__inner:focus) {
  border-color: var(--color-accent-orange);
}

/* Input */
:deep(.el-input__inner) {
  font-family: var(--font-body);
}

/* Dialog */
:deep(.el-dialog) {
  border-radius: var(--radius-xl);
}

:deep(.el-dialog__title) {
  font-family: var(--font-heading);
  font-weight: 600;
}

/* Alert */
:deep(.el-alert) {
  border-radius: var(--radius-md);
}

:deep(.el-alert__title) {
  font-family: var(--font-body);
}

/* Form label */
:deep(.el-form-item__label) {
  font-family: var(--font-heading);
  font-weight: 500;
}
</style>
