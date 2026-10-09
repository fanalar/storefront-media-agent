<template>
  <div class="page">
    <div class="page-head"><div><span class="page-kicker">BRAND VOICE</span><h1 class="page-title">老板人设档案</h1><p class="page-note">这里的信息会成为脚本的长期底稿。写真实经历，不写空泛口号。</p></div><el-button type="primary" :loading="saving" @click="save">保存档案</el-button></div>
    <div class="persona-grid">
      <section class="panel panel-pad">
        <div class="form-section"><b>01</b><div><h3>身份与门店</h3><p>顾客首先要知道“你是谁、你做什么”。</p></div></div>
        <el-form :model="form" label-position="top">
          <div class="two"><el-form-item label="老板称呼"><el-input v-model="form.name" maxlength="80" placeholder="例如：张师傅" /></el-form-item><el-form-item label="门店名称"><el-input v-model="form.shop_name" maxlength="120" placeholder="例如：巷口张记面馆" /></el-form-item></div>
          <div class="two"><el-form-item label="所在行业"><el-input v-model="form.industry" maxlength="80" placeholder="餐饮 / 零售 / 本地服务" /></el-form-item><el-form-item label="主要顾客"><el-input v-model="form.audience" maxlength="1000" placeholder="例如：附近写字楼午餐客群" /></el-form-item></div>
          <el-form-item label="创业故事"><el-input v-model="form.story" type="textarea" :rows="5" maxlength="5000" show-word-limit placeholder="从哪一年开始？为什么做这门生意？最难忘的一件事是什么？" /></el-form-item>
          <el-form-item label="说话风格"><el-input v-model="form.speaking_style" maxlength="500" placeholder="例如：朴实、不绕弯、偶尔带一点本地方言" /></el-form-item>
          <el-form-item label="经营理念"><el-input v-model="form.philosophy" type="textarea" :rows="3" maxlength="1000" placeholder="什么事情你宁可少赚也不妥协？" /></el-form-item>
        </el-form>
      </section>
      <aside class="panel preview">
        <span>人设名片预览</span><div class="avatar">{{ (form.name || '店').slice(0,1) }}</div><h2>{{ form.name || '还没有填写老板称呼' }}</h2><strong>{{ form.shop_name || '门店名称' }} · {{ form.industry || '行业' }}</strong><blockquote>“{{ form.philosophy || '把你最坚持的一句话写在这里。' }}”</blockquote><p>{{ form.story || '创业故事会帮助 AI 写出更像你、而不是模板化的内容。' }}</p>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api, { apiError } from '@/api'
const saving = ref(false)
const form = reactive({ name:'',shop_name:'',industry:'',story:'',speaking_style:'',philosophy:'',audience:'',logo_path:'' })
onMounted(async()=>{ try{const data=(await api.get('/api/persona')).data;for(const key of Object.keys(form)){if(data[key]!=null)form[key]=data[key]}}catch(error){ElMessage.error(apiError(error,'人设加载失败'))} })
async function save(){saving.value=true;try{await api.put('/api/persona',form);ElMessage.success('人设档案已保存')}catch(error){ElMessage.error(apiError(error))}finally{saving.value=false}}
</script>

<style scoped>
.persona-grid{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:15px}.form-section{display:flex;gap:14px;padding-bottom:18px;margin-bottom:18px;border-bottom:1px solid var(--line)}.form-section>b{color:var(--amber);font-family:serif;font-size:25px}.form-section h3{margin:0;font-family:"STZhongsong",serif}.form-section p{margin:4px 0 0;color:var(--muted);font-size:11px}.two{display:grid;grid-template-columns:1fr 1fr;gap:15px}.preview{padding:28px;text-align:center;align-self:start}.preview>span{font-size:9px;letter-spacing:.18em;color:var(--teal)}.avatar{width:76px;height:76px;margin:26px auto 17px;display:grid;place-items:center;border-radius:50%;color:#1a1408;background:var(--amber);font-family:"STZhongsong",serif;font-size:30px;box-shadow:0 0 0 8px rgba(244,185,66,.08)}.preview h2{font-family:"STZhongsong",serif;margin:0 0 6px}.preview strong{font-size:11px;color:var(--muted)}blockquote{margin:23px 0;padding:15px;border-block:1px solid var(--line);color:var(--amber-soft);font-family:"STZhongsong",serif;line-height:1.7}.preview p{font-size:11px;line-height:1.8;color:var(--muted);text-align:left}@media(max-width:1000px){.persona-grid{grid-template-columns:1fr}.preview{display:none}}
</style>
