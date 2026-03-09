<template>
  <el-card class="asr-panel">
    <template #header>
      <span>语音识别 (ASR)</span>
    </template>

    <el-form label-width="100px">
      <el-form-item label="音频文件">
        <el-upload
          :auto-upload="false"
          :on-change="handleAudioChange"
          :show-file-list="false"
          accept="audio/*"
        >
          <el-button>选择音频</el-button>
        </el-upload>
        <span v-if="audioFile" style="margin-left: 10px">{{ audioFile.name }}</span>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleTranscribe" :loading="loading">识别</el-button>
      </el-form-item>

      <el-form-item label="识别结果" v-if="result">
        <el-input v-model="result" type="textarea" :rows="4" readonly />
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { transcribeAudio } from '../api/asr'

const audioFile = ref<File | null>(null)
const result = ref('')
const loading = ref(false)

const handleAudioChange = (file: any) => {
  audioFile.value = file.raw
}

const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const base64 = (reader.result as string).split(',')[1]
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

const handleTranscribe = async () => {
  if (!audioFile.value) {
    ElMessage.warning('请选择音频文件')
    return
  }

  loading.value = true
  try {
    const audioData = await fileToBase64(audioFile.value)
    const res = await transcribeAudio({ audio_data: audioData })
    result.value = res.text
    ElMessage.success('识别成功')
  } catch (error) {
    ElMessage.error('识别失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.asr-panel {
  margin-bottom: 20px;
}
</style>
