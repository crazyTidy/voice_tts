<template>
  <div class="step-indicator">
    <div
      v-for="(step, index) in steps"
      :key="index"
      :class="['step-item', getStepClass(index + 1)]"
    >
      <span class="step-number">{{ index + 1 }}</span>
      <span class="step-label">{{ step }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  currentStep: number
}

const props = defineProps<Props>()

const steps = ['上传参考音频', '输入音频文本', '输入合成文本', '生成语音']

function getStepClass(step: number) {
  if (step < props.currentStep) return 'completed'
  if (step === props.currentStep) return 'active'
  return ''
}
</script>

<style scoped>
/* ========================================
   Step Indicator - Anthropic Brand Styling
   ======================================== */

.step-indicator {
  display: flex;
  justify-content: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg) 0;
}

.step-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  opacity: 0.4;
  transition: opacity var(--transition-base);
}

.step-item.active,
.step-item.completed {
  opacity: 1;
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background-color: var(--color-light-gray);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-heading);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-mid-gray);
  transition: all var(--transition-base);
  box-shadow: var(--shadow-sm);
}

/* Active step - Orange accent */
.step-item.active .step-number {
  background-color: var(--color-accent-orange);
  color: var(--color-light);
  box-shadow: 0 4px 12px rgba(217, 119, 87, 0.4);
}

/* Completed step - Green accent */
.step-item.completed .step-number {
  background-color: var(--color-accent-green);
  color: var(--color-light);
  box-shadow: 0 2px 8px rgba(120, 140, 93, 0.3);
}

.step-label {
  font-family: var(--font-heading);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-dark);
}

.step-item.active .step-label {
  color: var(--color-accent-orange);
  font-weight: 600;
}

/* ========================================
   Responsive Design
   ======================================== */
@media (max-width: 768px) {
  .step-indicator {
    gap: var(--spacing-md);
  }

  .step-number {
    width: 32px;
    height: 32px;
    font-size: 13px;
  }

  .step-label {
    display: none;
  }
}
</style>
