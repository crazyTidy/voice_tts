<template>
  <el-card class="preset-manager">
    <template #header>
      <div style="display: flex; justify-content: space-between; align-items: center">
        <span>音色预设管理</span>
        <el-button type="primary" size="small" @click="dialogVisible = true">新建预设</el-button>
      </div>
    </template>

    <el-table :data="presets" style="width: 100%">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="prompt_text" label="参考文本" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" @click="handleUse(row)">使用</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="新建预设" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="参考文本">
          <el-input v-model="form.promptText" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="音频">
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
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="loading">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listPresets, createPreset, deletePreset, type Preset } from '../api/preset'

const emit = defineEmits(['use-preset'])

const presets = ref<Preset[]>([])
const dialogVisible = ref(false)
const loading = ref(false)
const audioFile = ref<File | null>(null)

const form = ref({
  name: '',
  promptText: ''
})

const loadPresets = async () => {
  try {
    const res = await listPresets()
    presets.value = res.presets
  } catch (error) {
    ElMessage.error('加载预设失败')
  }
}

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

const handleCreate = async () => {
  if (!form.value.name || !audioFile.value) {
    ElMessage.warning('请填写完整信息')
    return
  }

  loading.value = true
  try {
    const audioData = await fileToBase64(audioFile.value)
    await createPreset({
      name: form.value.name,
      prompt_text: form.value.promptText,
      audio_data: audioData
    })
    ElMessage.success('创建成功')
    dialogVisible.value = false
    form.value = { name: '', promptText: '' }
    audioFile.value = null
    loadPresets()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id: string) => {
  try {
    await ElMessageBox.confirm('确认删除该预设？', '提示', { type: 'warning' })
    await deletePreset(id)
    ElMessage.success('删除成功')
    loadPresets()
  } catch (error) {
    // User cancelled
  }
}

const handleUse = (preset: Preset) => {
  emit('use-preset', preset)
}

onMounted(() => {
  loadPresets()
})
</script>

<style scoped>
.preset-manager {
  margin-bottom: 20px;
}
</style>
