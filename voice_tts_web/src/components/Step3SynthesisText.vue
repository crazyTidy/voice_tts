<template>
  <div class="step-container">
    <h3 class="step-title">请输入要合成的文字内容</h3>

    <div class="summary">
      <p><strong>已完成的步骤：</strong></p>
      <p>✓ 已上传参考音频</p>
      <p>✓ 参考音频文本：{{ promptTextPreview }}</p>
    </div>

    <el-input
      v-model="synthesisText"
      type="textarea"
      :rows="10"
      placeholder="请输入要合成的文字内容"
      :maxlength="maxLength"
      show-word-limit
    />

    <div class="action-buttons">
      <el-button @click="clearText">清空</el-button>
    </div>

    <div class="instructions">
      <p><strong>提示：</strong></p>
      <ul>
        <li>文本长度建议在 {{ maxLength }} 字符以内</li>
        <li>输入完成后，点击"下一步"进入生成步骤</li>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  promptText: string
}

interface Emits {
  (e: 'prev'): void
  (e: 'next', text: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const synthesisText = ref('')
const maxLength = 500

const promptTextPreview = computed(() => {
  if (props.promptText.length <= 50) return props.promptText
  return props.promptText.slice(0, 50) + '...'
})

const canGoNext = computed(() => {
  const text = synthesisText.value.trim()
  return text.length > 0 && text.length <= maxLength
})

function clearText() {
  synthesisText.value = ''
}

function goPrev() {
  emit('prev')
}

function goNext() {
  emit('next', synthesisText.value.trim())
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
   Summary Box
   ======================================== */

.summary {
  padding: var(--spacing-md);
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-lg);
  border-left: 3px solid var(--color-accent-green);
}

.summary p {
  font-family: var(--font-body);
  margin: 4px 0;
  color: var(--text-primary);
}

.summary strong {
  font-family: var(--font-heading);
  color: var(--color-accent-green);
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
</style>
