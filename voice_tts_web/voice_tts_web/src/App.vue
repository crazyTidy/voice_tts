<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <h1>智能语音克隆演示系统</h1>
      </el-header>
      <el-main>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="语音合成" name="tts">
            <TTSPanel ref="ttsRef" />
          </el-tab-pane>
          <el-tab-pane label="语音识别" name="asr">
            <ASRPanel />
          </el-tab-pane>
          <el-tab-pane label="预设管理" name="preset">
            <PresetManager @use-preset="handleUsePreset" />
          </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TTSPanel from './components/TTSPanel.vue'
import ASRPanel from './components/ASRPanel.vue'
import PresetManager from './components/PresetManager.vue'
import { getPresetAudio, type Preset } from './api/preset'
import { ElMessage } from 'element-plus'

const activeTab = ref('tts')
const ttsRef = ref()

const handleUsePreset = async (preset: Preset) => {
  try {
    const res = await getPresetAudio(preset.id)
    // Switch to TTS tab and populate form
    activeTab.value = 'tts'
    ElMessage.success(`已加载预设: ${preset.name}`)
  } catch (error) {
    ElMessage.error('加载预设失败')
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.el-header {
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.el-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>
