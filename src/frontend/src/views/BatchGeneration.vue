<template>
  <div class="page">
    <div class="page-head"><div><span class="page-kicker">PRODUCTION QUEUE</span><h1 class="page-title">批量生产</h1><p class="page-note">选择多个已保存模板，系统会顺序生成，失败信息会保留在任务记录中。</p></div><el-button @click="clearCompleted">清理已结束任务</el-button></div>
    <section class="panel panel-pad starter">
      <div><label>剪辑模板</label><el-select v-model="selectedTemplates" multiple collapse-tags placeholder="至少选择一个模板"><el-option v-for="item in templates" :key="item.id" :label="item.name" :value="item.id"/></el-select></div>
      <div><label>输出目录</label><div class="file-pick"><el-input v-model="outputDir" readonly placeholder="不选择则使用默认作品目录"/><el-button @click="chooseOutput">选择</el-button></div></div>
      <el-button type="primary" size="large" :loading="starting" @click="start">加入生产队列</el-button>
    </section>
    <section class="panel queue">
      <div class="queue-title"><strong>生产记录</strong><span>{{ activeCount ? `${activeCount} 项进行中` : '当前没有运行中的任务' }}</span></div>
      <div v-if="tasks.length" class="jobs">
        <article v-for="task in tasks" :key="task.id" class="job"><div class="job-id">#{{ task.id }}</div><div class="job-main"><div><strong>{{ statusName(task.status) }}</strong><span>{{ task.completed }} / {{ task.total }} 个作品</span></div><el-progress :percentage="Number(task.progress)" :status="task.status==='failed'?'exception':task.status==='done'?'success':''"/><small v-if="task.error">{{ task.error }}</small><small v-else>{{ formatDate(task.updated_at) }} · {{ task.output_dir || '默认输出目录' }}</small></div><el-button v-if="!['running','pending'].includes(task.status)" text type="danger" @click="remove(task.id)">删除</el-button></article>
      </div>
      <div v-else class="empty-state"><el-icon :size="34"><Collection /></el-icon><p>先在剪辑工坊保存模板，再回来批量生产。</p></div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api, { apiError } from '@/api'
const templates=ref([]);const tasks=ref([]);const selectedTemplates=ref([]);const outputDir=ref('');const starting=ref(false);let timer
const activeCount=computed(()=>tasks.value.filter(item=>['pending','running'].includes(item.status)).length)
async function refresh(){tasks.value=(await api.get('/api/batch/tasks')).data}
async function chooseOutput(){const path=await window.desktop?.selectFolder?.();if(path)outputDir.value=path}
async function start(){if(!selectedTemplates.value.length)return ElMessage.warning('请选择至少一个剪辑模板');starting.value=true;try{await api.post('/api/batch/start',{template_ids:selectedTemplates.value,output_dir:outputDir.value});ElMessage.success('已加入生产队列');await refresh()}catch(error){ElMessage.error(apiError(error))}finally{starting.value=false}}
async function remove(id){try{await api.delete(`/api/batch/tasks/${id}`);await refresh()}catch(error){ElMessage.error(apiError(error))}}
async function clearCompleted(){try{const {data}=await api.delete('/api/batch/completed');ElMessage.success(`已清理 ${data.deleted} 条记录`);await refresh()}catch(error){ElMessage.error(apiError(error))}}
function statusName(value){return({pending:'等待中',running:'正在生成',done:'已完成',failed:'失败',interrupted:'已中断'})[value]||value}function formatDate(value){return value?new Date(value).toLocaleString('zh-CN',{hour12:false}):'—'}
onMounted(async()=>{try{[templates.value]=[(await api.get('/api/mix/templates')).data];await refresh()}catch(error){ElMessage.error(apiError(error))}timer=setInterval(()=>{if(activeCount.value)refresh().catch(()=>{})},2000)});onUnmounted(()=>clearInterval(timer))
</script>

<style scoped>
.starter{display:grid;grid-template-columns:1fr 1.2fr auto;gap:14px;align-items:end;margin-bottom:14px}.starter label{display:block;margin-bottom:7px;color:var(--muted);font-size:10px}.starter .el-select{width:100%}.file-pick{display:flex;gap:7px}.queue{overflow:hidden}.queue-title{height:62px;padding:0 21px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}.queue-title strong{font-size:13px}.queue-title span{color:var(--teal);font-size:10px}.jobs{padding:5px 15px}.job{display:grid;grid-template-columns:58px 1fr auto;gap:15px;align-items:center;padding:17px 5px;border-bottom:1px solid var(--line)}.job-id{color:var(--amber);font-family:serif;font-size:20px}.job-main>div{display:flex;justify-content:space-between;margin-bottom:9px}.job-main strong{font-size:12px}.job-main span,.job-main small{color:var(--muted);font-size:9px}.job-main small{display:block;margin-top:6px}.job-main :deep(.el-progress-bar__outer){background:#0a1521}@media(max-width:950px){.starter{grid-template-columns:1fr}.starter>.el-button{width:100%}}
</style>

