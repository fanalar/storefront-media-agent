<template>
  <div class="page home">
    <section class="hero panel">
      <div class="hero-copy">
        <span class="eyebrow">LOCAL BUSINESS · CONTENT ENGINE</span>
        <h1>把门店里的烟火气，<br><em>稳定做成内容。</em></h1>
        <p>从老板人设、素材整理到批量成片，一套本地工作台串起每天的新媒体经营。</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/materials')">整理今日素材 <el-icon><Right /></el-icon></el-button>
          <el-button size="large" @click="$router.push('/mix')">进入剪辑工坊</el-button>
        </div>
      </div>
      <div class="day-card">
        <span>今日建议</span>
        <strong>{{ todayTitle }}</strong>
        <p>先用 3 个真实镜头讲清一个卖点，再补一句老板自己的话。</p>
        <div class="shot-line"><i></i><i></i><i></i><i class="muted-line"></i></div>
      </div>
    </section>

    <section class="metrics">
      <article v-for="metric in metrics" :key="metric.label" class="metric panel">
        <div><span>{{ metric.label }}</span><strong>{{ metric.value }}</strong></div>
        <el-icon><component :is="metric.icon" /></el-icon>
      </article>
    </section>

    <section class="work-grid">
      <article class="panel quick-panel">
        <div class="section-title"><div><span>工作路径</span><h2>四步完成一条门店视频</h2></div><small>建议从左到右</small></div>
        <div class="steps">
          <button v-for="(step,index) in steps" :key="step.path" @click="$router.push(step.path)">
            <b>0{{ index + 1 }}</b><el-icon><component :is="step.icon" /></el-icon><strong>{{ step.title }}</strong><span>{{ step.note }}</span>
          </button>
        </div>
      </article>
      <aside class="panel honesty">
        <span class="stamp">发布边界</span>
        <h3>最后一步，由老板确认</h3>
        <p>系统整理视频、标题与话题，并打开对应创作者平台。账号登录与最终发布保留人工确认，避免误发。</p>
        <el-button text @click="$router.push('/publish')">查看发布中心 <el-icon><Right /></el-icon></el-button>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive } from 'vue'
import api from '@/api'

const stats = reactive({ categories: 0, templates: 0, completed: 0, schedules: 0 })
const todayTitle = computed(() => `${new Date().getMonth()+1}月${new Date().getDate()}日 · 拍一条真实顾客问题`)
const metrics = computed(() => [
  { label:'素材分类', value:stats.categories, icon:'FolderOpened' },
  { label:'剪辑模板', value:stats.templates, icon:'Film' },
  { label:'已完成作品', value:stats.completed, icon:'CircleCheck' },
  { label:'待发布计划', value:stats.schedules, icon:'Clock' },
])
const steps = [
  { title:'定人设', note:'把老板和门店说清楚', icon:'User', path:'/persona' },
  { title:'收素材', note:'扫描并归档真实镜头', icon:'FolderOpened', path:'/materials' },
  { title:'做成片', note:'排镜头、字幕和音乐', icon:'Film', path:'/mix' },
  { title:'去发布', note:'准备资料后人工确认', icon:'Promotion', path:'/publish' },
]

onMounted(async () => {
  const calls = await Promise.allSettled([
    api.get('/api/materials/categories'), api.get('/api/mix/templates'), api.get('/api/batch/tasks'), api.get('/api/publish/schedule'),
  ])
  if (calls[0].status === 'fulfilled') stats.categories = calls[0].value.data.length
  if (calls[1].status === 'fulfilled') stats.templates = calls[1].value.data.length
  if (calls[2].status === 'fulfilled') stats.completed = calls[2].value.data.filter(item => item.status === 'done').length
  if (calls[3].status === 'fulfilled') stats.schedules = calls[3].value.data.filter(item => !['published','cancelled'].includes(item.status)).length
})
</script>

<style scoped>
.hero{min-height:300px;padding:42px;display:grid;grid-template-columns:1.35fr .65fr;gap:50px;align-items:center;overflow:hidden;position:relative}.hero::before{content:"";position:absolute;width:360px;height:360px;border:1px solid rgba(244,185,66,.13);border-radius:50%;right:-120px;top:-180px;box-shadow:0 0 0 48px rgba(244,185,66,.025),0 0 0 96px rgba(244,185,66,.02)}
.hero-copy{position:relative;z-index:1}.eyebrow{font-size:10px;letter-spacing:.2em;color:var(--teal)}h1{margin:12px 0 15px;font-family:"STZhongsong","SimSun",serif;font-size:42px;line-height:1.22;font-weight:700}h1 em{color:var(--amber);font-style:normal}.hero-copy p{max-width:620px;color:var(--muted);line-height:1.8}.hero-actions{display:flex;gap:11px;margin-top:25px}
.day-card{position:relative;z-index:1;padding:22px;border-left:1px solid rgba(244,185,66,.4);background:linear-gradient(90deg,rgba(244,185,66,.07),transparent)}.day-card>span{font-size:11px;color:var(--amber);letter-spacing:.15em}.day-card strong{display:block;margin:12px 0 9px;font-family:"STZhongsong",serif;font-size:20px}.day-card p{color:var(--muted);font-size:12px;line-height:1.8}.shot-line{display:flex;gap:6px;margin-top:18px}.shot-line i{width:44px;height:4px;border-radius:4px;background:var(--teal)}.shot-line .muted-line{background:#31485c}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:14px 0}.metric{padding:18px 19px;display:flex;align-items:center;justify-content:space-between}.metric span{display:block;font-size:11px;color:var(--muted)}.metric strong{display:block;margin-top:4px;font-family:"STZhongsong",serif;font-size:27px}.metric>.el-icon{font-size:24px;color:rgba(244,185,66,.62)}
.work-grid{display:grid;grid-template-columns:1fr 300px;gap:14px}.quick-panel{padding:24px}.section-title{display:flex;justify-content:space-between;align-items:flex-end}.section-title span{font-size:10px;color:var(--teal);letter-spacing:.15em}.section-title h2{margin:5px 0 0;font-family:"STZhongsong",serif;font-size:20px}.section-title small{color:#587086}.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-top:20px}.steps button{position:relative;min-height:145px;padding:17px;border:1px solid var(--line);border-radius:13px;color:var(--paper);background:rgba(7,16,27,.44);text-align:left;cursor:pointer;transition:.2s}.steps button:hover{transform:translateY(-3px);border-color:rgba(244,185,66,.4)}.steps b{position:absolute;right:12px;top:9px;color:#334b60;font-family:serif;font-size:22px}.steps .el-icon{display:block;margin:8px 0 16px;color:var(--amber);font-size:23px}.steps strong,.steps span{display:block}.steps strong{font-size:14px}.steps span{margin-top:6px;color:var(--muted);font-size:10px;line-height:1.5}
.honesty{padding:24px}.stamp{display:inline-block;padding:4px 8px;border:1px solid rgba(69,196,176,.35);color:var(--teal);font-size:9px;letter-spacing:.16em}.honesty h3{margin:17px 0 10px;font-family:"STZhongsong",serif;font-size:20px}.honesty p{color:var(--muted);font-size:12px;line-height:1.85}.honesty .el-button{margin-top:10px;color:var(--amber)}
@media(max-width:1100px){.hero{grid-template-columns:1fr}.day-card{display:none}.metrics{grid-template-columns:repeat(2,1fr)}.work-grid{grid-template-columns:1fr}.steps{grid-template-columns:repeat(2,1fr)}}
</style>

