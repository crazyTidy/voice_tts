<template>
  <el-card class="tts-panel">
    <template #header>
      <span>语音合成 (TTS)</span>
    </template>

    <el-form :model="form" label-width="100px">
      <el-form-item label="参考音频">
        <el-tabs v-model="audioTab">
          <el-tab-pane label="上传音频" name="upload">
            <el-upload
              :auto-upload="false"
              :on-change="handleAudioChange"
              :show-file-list="false"
              accept="audio/*"
            >
              <el-button>选择音频</el-button>
            </el-upload>
            <span v-if="audioFile && audioTab === 'upload'" style="margin-left: 10px">
              {{ audioFile.name }}
              <span v-if="audioDuration > 0"> ({{ audioDuration.toFixed(1) }}秒)</span>
            </span>
          </el-tab-pane>
          <el-tab-pane label="录制音频" name="record">
            <el-button v-if="!isRecording && !recordedBlob" @click="startRecording" type="primary">开始录音</el-button>
            <el-button v-if="isRecording" @click="stopRecording" type="danger">停止录音 ({{ recordDuration.toFixed(1) }}秒)</el-button>
            <span v-if="recordedBlob" style="margin-left: 10px">
              录音完成 ({{ audioDuration.toFixed(1) }}秒)
              <el-button size="small" @click="downloadRecording">下载WAV</el-button>
              <el-button size="small" @click="clearRecording">清除</el-button>
            </span>
          </el-tab-pane>
        </el-tabs>
      </el-form-item>

      <el-form-item label="参考文本">
        <el-input v-model="form.promptText" type="textarea" :rows="2" />
      </el-form-item>

      <el-form-item label="合成文本">
        <el-input v-model="form.text" type="textarea" :rows="4" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleGenerate" :loading="loading">生成语音</el-button>
      </el-form-item>
    </el-form>

    <div v-if="audioUrl">
      <audio :src="audioUrl" controls style="width: 100%"></audio>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { generateSpeech } from '../api/tts'

const form = ref({
  text: '',
  promptText: ''
})

const audioTab = ref('upload')
const audioFile = ref<File | null>(null)
const audioUrl = ref('')
const loading = ref(false)
const audioDuration = ref(0)

const isRecording = ref(false)
const recordedBlob = ref<Blob | null>(null)
const recordDuration = ref(0)
let mediaRecorder: MediaRecorder | null = null
let recordInterval: number | null = null

const handleAudioChange = async (file: any) => {
  audioFile.value = file.raw
  audioDuration.value = await getAudioDuration(file.raw)
}

const getAudioDuration = (file: File): Promise<number> => {
  return new Promise((resolve) => {
    const audio = new Audio()
    audio.onloadedmetadata = () => {
      resolve(audio.duration)
    }
    audio.src = URL.createObjectURL(file)
  })
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    // 尝试使用 WAV 格式，如果不支持则使用默认格式
    const mimeType = MediaRecorder.isTypeSupported('audio/wav')
      ? 'audio/wav'
      : MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : ''

    mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : {})
    const chunks: Blob[] = []

    mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
    mediaRecorder.onstop = async () => {
      console.log('录音停止，chunks数量:', chunks.length)
      const audioBlob = new Blob(chunks, { type: mimeType || 'audio/webm' })
      console.log('audioBlob大小:', audioBlob.size, 'type:', audioBlob.type)

      // 转换为 WAV 格式
      try {
        console.log('开始转换为WAV...')
        recordedBlob.value = await convertToWav(audioBlob)
        console.log('WAV转换成功，大小:', recordedBlob.value.size)
        audioDuration.value = await getAudioDuration(new File([recordedBlob.value], 'recording.wav', { type: 'audio/wav' }))
        console.log('时长:', audioDuration.value)
        ElMessage.success(`录音完成 (${audioDuration.value.toFixed(1)}秒)`)
      } catch (error) {
        ElMessage.error('音频转换失败: ' + error)
        console.error('转换错误:', error)
      }

      stream.getTracks().forEach(track => track.stop())
    }

    mediaRecorder.start()
    isRecording.value = true
    recordDuration.value = 0
    recordInterval = window.setInterval(() => {
      recordDuration.value += 0.1
    }, 100)
  } catch (error) {
    ElMessage.error('无法访问麦克风')
  }
}

const convertToWav = async (blob: Blob): Promise<Blob> => {
  const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
  const arrayBuffer = await blob.arrayBuffer()
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)

  const numberOfChannels = audioBuffer.numberOfChannels
  const sampleRate = audioBuffer.sampleRate
  const format = 1 // PCM
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

const stopRecording = () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
    if (recordInterval) clearInterval(recordInterval)
  }
}

const clearRecording = () => {
  recordedBlob.value = null
  audioDuration.value = 0
  recordDuration.value = 0
}

const downloadRecording = () => {
  if (!recordedBlob.value) return
  const url = URL.createObjectURL(recordedBlob.value)
  const a = document.createElement('a')
  a.href = url
  a.download = `recording_${Date.now()}.wav`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success(`已下载到: ${a.download}`)
}

const fileToBase64 = (file: File | Blob): Promise<string> => {
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

const handleGenerate = async () => {
  if (!form.value.text) {
    ElMessage.warning('请输入合成文本')
    return
  }

  let selectedFile: File | null = null
  if (audioTab.value === 'upload' && audioFile.value) {
    selectedFile = audioFile.value
  } else if (audioTab.value === 'record' && recordedBlob.value) {
    selectedFile = new File([recordedBlob.value], 'recording.wav', { type: 'audio/wav' })
  }

  if (!selectedFile) {
    ElMessage.warning('请上传或录制参考音频')
    return
  }

  loading.value = true
  try {
    const promptSpeech = await fileToBase64(selectedFile)
    const res = await generateSpeech({
      text: form.value.text,
      prompt_text: form.value.promptText,
      prompt_speech_16k: promptSpeech
    })

    const audioData = `data:audio/wav;base64,${res.audio_data}`
    audioUrl.value = audioData
    ElMessage.success('生成成功')
  } catch (error) {
    ElMessage.error('生成失败')
  } finally {
    loading.value = false
  }
}
  } catch (error) {
    ElMessage.error('生成失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.tts-panel {
  margin-bottom: 20px;
}
</style>
