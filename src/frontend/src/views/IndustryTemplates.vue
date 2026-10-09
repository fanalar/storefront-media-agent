<template>
  <div class="page"><div class="page-head"><div><span class="page-kicker">INDUSTRY PLAYBOOK</span><h1 class="page-title">行业模板</h1><p class="page-note">模板提供镜头结构和表达提示，不替门店编造事实。</p></div><el-input v-model="query" prefix-icon="Search" placeholder="搜索行业或场景" clearable style="width:260px"/></div>
    <div class="template-grid"><article v-for="item in filtered" :key="item.id" class="panel template-card"><div class="card-top"><span>{{ item.code }}</span><i>{{ item.scene }}</i></div><h2>{{ item.name }}</h2><p>{{ item.description }}</p><div class="shot-tags"><span v-for="shot in item.shots" :key="shot.role">{{ shot.role }}</span></div><button @click="use(item)">用这套结构开拍 <el-icon><Right /></el-icon></button></article></div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';import { useRouter } from 'vue-router';const router=useRouter();const query=ref('')
const templates=[
 {id:'food',code:'01',name:'餐饮门店',scene:'新品 / 后厨 / 老板口播',description:'从真实制作过程切入，用食材、手艺和顾客反馈建立信任。',title:'今天这份招牌菜，为什么要多花两小时',shots:[{role:'门头',duration:3,script:'这是我们每天开门前的第一件事。'},{role:'食材',duration:5,script:'今天用到的食材，先给大家看清楚。'},{role:'制作',duration:8,script:'这一步慢不得，也是味道的关键。'},{role:'老板',duration:6,script:'我们坚持这样做，是因为……'}]},
 {id:'clean',code:'02',name:'家政清洁',scene:'前后对比 / 工具 / 细节',description:'用可验证的前后变化呈现专业度，避免夸大承诺。',title:'这个卫生死角，大多数人都会漏掉',shots:[{role:'问题现场',duration:4,script:'先看清今天要解决的问题。'},{role:'工具',duration:4,script:'不同材质要用不同工具。'},{role:'过程',duration:8,script:'真正费时间的是这些细节。'},{role:'结果',duration:5,script:'完成后的效果，大家自己判断。'}]},
 {id:'dental',code:'03',name:'口腔门诊',scene:'科普 / 环境 / 医师',description:'以合规科普和就诊流程为主，不使用疗效保证或患者隐私。',title:'第一次看牙，先别急着做决定',shots:[{role:'接诊区',duration:4,script:'第一次来，通常先了解基础情况。'},{role:'设备',duration:5,script:'检查的目的，是把问题看清楚。'},{role:'医师科普',duration:10,script:'不同情况处理方式不同，需要当面判断。'}]},
 {id:'retail',code:'04',name:'零售门店',scene:'到货 / 选品 / 搭配',description:'把选品逻辑和使用场景讲清，让产品不再只是货架陈列。',title:'这批新品，我们为什么只留下这三款',shots:[{role:'到货',duration:4,script:'今天刚到的一批新品。'},{role:'对比',duration:8,script:'我们留下这三款，主要看这几点。'},{role:'场景',duration:6,script:'如果你是这种需求，可以优先看这一款。'}]},
 {id:'beauty',code:'05',name:'美容美发',scene:'设计 / 过程 / 养护',description:'突出审美判断与服务过程，所有效果展示注明个体差异。',title:'做造型之前，我们为什么先问这三个问题',shots:[{role:'沟通',duration:6,script:'先了解日常习惯，才能决定方向。'},{role:'设计',duration:6,script:'这个方案重点处理的是比例。'},{role:'过程',duration:7,script:'过程中我们会随时确认。'}]},
 {id:'auto',code:'06',name:'汽车服务',scene:'检测 / 施工 / 交付',description:'用检测依据和施工细节建立透明感，减少顾客信息差。',title:'保养项目不是越多越好',shots:[{role:'车况',duration:4,script:'先看实际车况，再决定做哪些项目。'},{role:'检测',duration:7,script:'这项数据说明的是……'},{role:'施工',duration:7,script:'需要处理的部分，我们现场给你看。'}]},
]
const filtered=computed(()=>{const key=query.value.trim();return key?templates.filter(item=>`${item.name}${item.scene}${item.description}`.includes(key)):templates})
function use(item){localStorage.setItem('storex:industry-preset',JSON.stringify({title:item.title,shots:item.shots.map(shot=>({...shot,path:'',name:`待选择：${shot.role}`,id:`preset-${item.id}-${shot.role}`}))}));router.push('/mix')}
</script>

<style scoped>
.template-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.template-card{padding:22px;position:relative;overflow:hidden}.template-card::after{content:"";position:absolute;right:-35px;bottom:-35px;width:100px;height:100px;border:1px solid rgba(244,185,66,.09);transform:rotate(45deg)}.card-top{display:flex;justify-content:space-between;align-items:center}.card-top span{font-family:serif;font-size:25px;color:var(--amber)}.card-top i{font-style:normal;color:var(--teal);font-size:9px}.template-card h2{margin:19px 0 8px;font-family:"STZhongsong",serif}.template-card p{min-height:58px;color:var(--muted);font-size:11px;line-height:1.7}.shot-tags{display:flex;flex-wrap:wrap;gap:5px;margin:15px 0}.shot-tags span{padding:4px 7px;border-radius:6px;background:rgba(255,255,255,.04);color:#8197aa;font-size:9px}.template-card button{position:relative;z-index:1;margin-top:9px;padding:0;border:0;color:var(--amber);background:none;cursor:pointer;font-size:11px}.template-card button:hover{color:var(--amber-soft)}@media(max-width:1100px){.template-grid{grid-template-columns:repeat(2,1fr)}}
</style>

