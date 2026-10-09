<template>
  <div class="shell">
    <aside class="rail">
      <div class="brand" @click="router.push('/')">
        <div class="brand-mark"><span>店</span></div>
        <div><strong>门店智媒</strong><small>AI OPERATIONS</small></div>
      </div>

      <nav class="nav">
        <button v-for="item in navigation" :key="item.path" :class="{ active: route.path === item.path }" @click="router.push(item.path)">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
          <i v-if="item.badge">{{ item.badge }}</i>
        </button>
      </nav>

      <div class="rail-foot">
        <div class="service-state"><span :class="['pulse', backend.online ? 'ok' : 'bad']"></span>{{ backend.online ? '本地引擎在线' : '本地引擎离线' }}</div>
        <div class="version">MIT 社区版 · v{{ backend.version || '0.2.0-community.1' }}</div>
      </div>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div>
          <span class="crumb">实体店新媒体AI智能体</span>
          <span class="divider">/</span>
          <strong>{{ currentLabel }}</strong>
        </div>
        <div class="top-actions">
          <button class="license" @click="router.push('/activate')"><el-icon><Key /></el-icon>{{ licenseText }}</button>
          <button class="icon-btn" title="系统设置" @click="router.push('/settings')"><el-icon><Setting /></el-icon></button>
        </div>
      </header>
      <main class="content"><router-view /></main>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from './api'

const route = useRoute()
const router = useRouter()
const backend = reactive({ online: false, version: '' })
const license = reactive({ activated: false, valid: false, remaining_days: 0 })
const navigation = [
  { path: '/', label: '经营台', icon: 'DataBoard' },
  { path: '/persona', label: '人设档案', icon: 'User' },
  { path: '/materials', label: '素材中心', icon: 'FolderOpened' },
  { path: '/mix', label: '剪辑工坊', icon: 'Film' },
  { path: '/batch', label: '批量生产', icon: 'Collection' },
  { path: '/industry', label: '行业模板', icon: 'Grid' },
  { path: '/publish', label: '发布中心', icon: 'Promotion', badge: '需确认' },
]
const currentLabel = computed(() => navigation.find(item => item.path === route.path)?.label || (route.path === '/activate' ? '社区版说明' : '系统设置'))
const licenseText = computed(() => 'MIT 社区版')

async function refreshLicense() {
  try { Object.assign(license, (await api.get('/api/license/status')).data) } catch {}
}

onMounted(async () => {
  try { const { data } = await api.get('/api/health'); backend.online = data.status === 'ok'; backend.version = data.version } catch { backend.online = false }
  await refreshLicense()
  window.addEventListener('storex:license-changed', refreshLicense)
})
onBeforeUnmount(() => window.removeEventListener('storex:license-changed', refreshLicense))
</script>

<style scoped>
.shell { display: grid; grid-template-columns: 232px 1fr; height: 100vh; background: radial-gradient(circle at 75% -10%, rgba(69,196,176,.08), transparent 34%), var(--ink-950); }
.rail { position: relative; display: flex; flex-direction: column; padding: 22px 15px 16px; background: rgba(8,20,33,.96); border-right: 1px solid var(--line); }
.rail::after { content:""; position:absolute; inset:0; pointer-events:none; opacity:.14; background-image: linear-gradient(rgba(255,255,255,.04) 1px, transparent 1px), linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px); background-size:28px 28px; }
.brand, .nav, .rail-foot { position: relative; z-index: 1; }
.brand { display:flex; align-items:center; gap:12px; padding:4px 8px 25px; cursor:pointer; }
.brand-mark { width:39px; height:39px; display:grid; place-items:center; transform:rotate(45deg); border:1px solid rgba(244,185,66,.5); background:rgba(244,185,66,.08); }
.brand-mark span { transform:rotate(-45deg); color:var(--amber); font-family:"STZhongsong",serif; font-size:19px; }
.brand strong { display:block; font-family:"STZhongsong",serif; letter-spacing:.08em; }
.brand small { display:block; margin-top:3px; color:#60788d; font-size:8px; letter-spacing:.18em; }
.nav { display:flex; flex-direction:column; gap:5px; }
.nav button { width:100%; border:0; border-radius:11px; padding:11px 12px; display:grid; grid-template-columns:22px 1fr auto; align-items:center; gap:9px; color:#8fa5b8; background:transparent; text-align:left; cursor:pointer; transition:.18s ease; }
.nav button:hover { color:var(--paper); background:rgba(255,255,255,.035); }
.nav button.active { color:#fff4d3; background:linear-gradient(90deg,rgba(244,185,66,.18),rgba(244,185,66,.045)); box-shadow:inset 2px 0 var(--amber); }
.nav i { font-style:normal; font-size:9px; color:var(--amber); border:1px solid rgba(244,185,66,.25); border-radius:9px; padding:2px 5px; }
.rail-foot { margin-top:auto; padding:13px 9px 2px; border-top:1px solid var(--line); }
.service-state { font-size:11px; color:#9bb0c1; display:flex; align-items:center; gap:7px; }
.pulse { width:7px; height:7px; border-radius:50%; box-shadow:0 0 0 4px rgba(255,107,99,.09); background:var(--danger); }
.pulse.ok { background:var(--teal); box-shadow:0 0 0 4px rgba(69,196,176,.09); }
.version { margin-top:7px; font-size:9px; color:#4f677a; }
.workspace { min-width:0; display:flex; flex-direction:column; }
.topbar { height:60px; min-height:60px; display:flex; align-items:center; justify-content:space-between; padding:0 26px; border-bottom:1px solid var(--line); background:rgba(7,16,27,.74); backdrop-filter:blur(12px); color:#a9bac8; font-size:12px; }
.topbar strong { color:var(--paper); }.divider{margin:0 8px;color:#41596d}.crumb{color:#647c90}
.top-actions { display:flex; gap:9px; align-items:center; }
.license,.icon-btn { border:1px solid var(--line-strong); color:#b9c9d6; background:rgba(16,32,51,.72); border-radius:10px; cursor:pointer; }
.license { display:flex; align-items:center; gap:7px; padding:8px 11px; font-size:11px; }.license:hover{border-color:rgba(244,185,66,.5);color:var(--amber-soft)}
.icon-btn{width:34px;height:34px;display:grid;place-items:center}.icon-btn:hover{color:var(--amber)}
.content { flex:1; overflow:auto; padding:28px; }
@media (max-width: 900px) { .shell{grid-template-columns:76px 1fr}.brand>div:last-child,.nav span,.nav i,.rail-foot{display:none}.brand{justify-content:center}.nav button{grid-template-columns:1fr;place-items:center}.content{padding:20px}.crumb,.divider{display:none} }
</style>
