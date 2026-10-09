<template>
  <div class="page">
    <div class="page-head"><div><span class="page-kicker">EDITING DESK</span><h1 class="page-title">剪辑工坊</h1><p class="page-note">镜头顺序、停留时长和口播字幕在同一张时间线上完成。</p></div><div class="toolbar"><el-button @click="addMedia">添加素材</el-button><el-button type="primary" :loading="composing" @click="compose">生成成片</el-button></div></div>
    <div class="editor-grid">
      <section class="panel timeline">
        <div class="timeline-head"><div><strong>镜头时间线</strong><span>{{ clips.length }} 个镜头 · 约 {{ totalDuration.toFixed(1) }} 秒</span></div><el-button text @click="clearClips">清空</el-button></div>
        <draggable v-model="clips" item-key="id" handle=".drag" class="clip-list">
          <template #item="{element,index}"><article class="clip"><button class="drag"><el-icon><Rank /></el-icon></button><span class="index">{{ String(index+1).padStart(2,'0') }}</span><div class="clip-main"><strong>{{ element.name }}</strong><small>{{ element.path }}</small><el-input v-model="element.script" placeholder="这一镜的口播或字幕…" /></div><el-input-number v-model="element.duration" :min="0.5" :max="600" :step="0.5" controls-position="right"/><button class="remove" @click="clips.splice(index,1)"><el-icon><Close /></el-icon></button></article></template>
        </draggable>
        <button v-if="!clips.length" class="drop-empty" @click="addMedia"><el-icon><Plus /></el-icon><strong>添加第一组真实镜头</strong><span>支持 MP4、MOV、AVI、MKV、WebM 和常见图片</span></button>
      </section>

      <aside class="side-stack">
        <section class="panel panel-pad"><div class="side-title"><span>成片参数</span><el-icon><Setting /></el-icon></div><el-form label-position="top"><el-form-item label="作品名称"><el-input v-model="outputName" placeholder="例如：周一午餐上新" /></el-form-item><el-form-item label="标题画面"><el-input v-model="options.title_text" maxlength="200" /></el-form-item><div class="two"><el-form-item label="画质"><el-select v-model="options.resolution"><el-option label="竖屏 1080P" value="1080p"/><el-option label="竖屏 720P" value="720p"/></el-select></el-form-item><el-form-item label="字幕字号"><el-input-number v-model="options.subtitle_font_size" :min="18" :max="96"/></el-form-item></div><el-form-item><el-checkbox v-model="options.subtitle_enabled">生成口播字幕</el-checkbox></el-form-item><el-form-item label="背景音乐"><div class="file-pick"><el-input v-model="options.bgm_path" readonly placeholder="可选"/><el-button @click="chooseBgm">选择</el-button></div></el-form-item><el-form-item label="音乐音量"><el-slider v-model="options.bgm_volume" :min="0" :max="1" :step="0.05"/></el-form-item></el-form></section>
        <section class="panel panel-pad"><div class="side-title"><span>剪辑模板</span><el-button text @click="saveTemplate">保存当前</el-button></div><el-select v-model="activeTemplate" placeholder="载入已有模板" style="width:100%" @change="loadTemplate"><el-option v-for="item in templates" :key="item.id" :label="item.name" :value="item.id"/></el-select><el-button v-if="activeTemplate" class="delete-template" text type="danger" @click="deleteTemplate">删除所选模板</el-button></section>
      </aside>
    </div>
    <el-alert v-if="result.message" :title="result.message" :type="result.success?'success':'error'" show-icon :closable="false" class="result"><template #default><el-button v-if="result.success" text @click="openResult">打开成片</el-button></template></el-alert>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import draggable from 'vuedraggable'
import { ElMessage, ElMessageBox } from 'element-plus'
import api, { apiError } from '@/api'
const clips=ref([]);const templates=ref([]);const activeTemplate=ref(null);const outputName=ref('');const composing=ref(false);const result=reactive({success:false,message:'',path:''});const options=reactive({resolution:'1080p',title_text:'',subtitle_enabled:true,subtitle_font_size:48,subtitle_font_color:'#FFFFFF',bgm_path:'',bgm_volume:.25})
const totalDuration=computed(()=>clips.value.reduce((sum,item)=>sum+Number(item.duration||0),0))
function makeClip(path,index){return{id:`${Date.now()}-${index}`,path,name:path.split(/[\\/]/).pop(),duration:5,script:'',role:''}}
async function addMedia(){const paths=await window.desktop?.selectMediaFiles?.();if(paths?.length)clips.value.push(...paths.map(makeClip))}
async function chooseBgm(){const paths=await window.desktop?.selectAudioFile?.();if(paths)options.bgm_path=paths}
function clearClips(){clips.value=[];activeTemplate.value=null}
async function loadTemplates(){templates.value=(await api.get('/api/mix/templates')).data}
function loadTemplate(id){const item=templates.value.find(value=>value.id===id);if(!item)return;clips.value=item.clips.map((clip,index)=>({...makeClip(clip.path,index),...clip}));Object.assign(options,item.options)}
async function saveTemplate(){if(!clips.value.length)return ElMessage.warning('先添加镜头');const {value:name}=await ElMessageBox.prompt('为当前镜头方案起一个名称','保存剪辑模板',{inputPattern:/\S+/,inputErrorMessage:'模板名称不能为空'});try{await api.post('/api/mix/templates',{name,clips:clips.value,options});await loadTemplates();ElMessage.success('模板已保存')}catch(error){ElMessage.error(apiError(error))}}
async function deleteTemplate(){await ElMessageBox.confirm('删除这个模板？素材原文件不会被删除。','删除模板',{type:'warning'});try{await api.delete(`/api/mix/templates/${activeTemplate.value}`);activeTemplate.value=null;await loadTemplates()}catch(error){ElMessage.error(apiError(error))}}
async function compose(){if(!clips.value.length)return ElMessage.warning('至少添加一个镜头');composing.value=true;result.message='';try{const {data}=await api.post('/api/mix/compose',{shots:clips.value,options,output_name:outputName.value});Object.assign(result,{success:true,message:`成片已生成：${data.output_path}`,path:data.output_path});ElMessage.success('视频合成完成')}catch(error){Object.assign(result,{success:false,message:apiError(error,'合成失败'),path:''})}finally{composing.value=false}}
async function openResult(){if(result.path)await window.desktop?.openPath?.(result.path)}
onMounted(async()=>{const selected=JSON.parse(localStorage.getItem('storex:selected-media')||'[]');if(selected.length){clips.value=selected.map(makeClip);localStorage.removeItem('storex:selected-media')}const preset=JSON.parse(localStorage.getItem('storex:industry-preset')||'null');if(preset){options.title_text=preset.title;clips.value=preset.shots.map((shot,index)=>({...makeClip('',index),...shot}));localStorage.removeItem('storex:industry-preset')}try{await loadTemplates()}catch(error){ElMessage.error(apiError(error))}})
</script>

<style scoped>
.editor-grid{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:14px}.timeline{min-height:610px;overflow:hidden}.timeline-head{height:66px;padding:0 20px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}.timeline-head strong,.timeline-head span{display:block}.timeline-head strong{font-size:13px}.timeline-head span{margin-top:3px;color:var(--muted);font-size:9px}.clip-list{padding:13px}.clip{display:grid;grid-template-columns:28px 36px minmax(0,1fr) 120px 28px;gap:10px;align-items:center;padding:12px 10px;border-bottom:1px solid var(--line)}.clip:hover{background:rgba(255,255,255,.018)}.drag,.remove{border:0;color:#526a7e;background:transparent;cursor:pointer}.drag{cursor:grab}.remove:hover{color:var(--danger)}.index{font-family:serif;color:var(--amber);font-size:18px}.clip-main{min-width:0}.clip-main strong,.clip-main small{display:block}.clip-main strong{font-size:11px}.clip-main small{margin:3px 0 8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#50677a;font-size:8px}.drop-empty{width:calc(100% - 26px);height:280px;margin:13px;border:1px dashed var(--line-strong);border-radius:13px;color:var(--muted);background:rgba(7,16,27,.28);cursor:pointer}.drop-empty .el-icon,.drop-empty strong,.drop-empty span{display:block;margin:auto}.drop-empty .el-icon{font-size:27px;color:var(--amber)}.drop-empty strong{margin-top:14px;color:var(--paper)}.drop-empty span{margin-top:7px;font-size:10px}.side-stack{display:flex;flex-direction:column;gap:14px}.side-title{display:flex;align-items:center;justify-content:space-between;margin-bottom:17px;font-size:11px;letter-spacing:.09em;color:var(--muted)}.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}.file-pick{display:flex;width:100%;gap:6px}.result{margin-top:14px}.delete-template{margin-top:9px}@media(max-width:1050px){.editor-grid{grid-template-columns:1fr}.side-stack{display:grid;grid-template-columns:1fr 1fr}}
</style>

