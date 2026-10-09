<template>
  <div class="page">
    <div class="page-head"><div><span class="page-kicker">ASSET LIBRARY</span><h1 class="page-title">素材中心</h1><p class="page-note">素材始终保留在原目录，系统只读取路径，不搬运原文件。</p></div><div class="toolbar"><el-checkbox v-model="recursive">包含子目录</el-checkbox><el-button type="primary" @click="chooseFolder">选择素材文件夹</el-button></div></div>

    <section class="panel library">
      <aside class="categories">
        <div class="cat-head"><span>素材分类</span><el-button text @click="categoryDialog=true"><el-icon><Plus /></el-icon></el-button></div>
        <button :class="{active:!activeCategory}" @click="activeCategory=null;files=[]"><span>临时浏览</span></button>
        <button v-for="item in categories" :key="item.id" :class="{active:activeCategory?.id===item.id}" @click="openCategory(item)"><span>{{ item.name }}</span><small>{{ shortPath(item.root_dir) }}</small><el-icon @click.stop="removeCategory(item)"><Delete /></el-icon></button>
      </aside>

      <div class="asset-area">
        <div class="asset-toolbar"><div><strong>{{ activeCategory?.name || '当前目录' }}</strong><span>{{ currentDir || '尚未选择目录' }}</span></div><div class="toolbar"><el-button :disabled="!selected.length" @click="sendToMix">送入剪辑工坊（{{ selected.length }}）</el-button><el-button :loading="loading" :disabled="!currentDir" @click="scan">重新扫描</el-button></div></div>
        <div v-if="files.length" class="asset-grid">
          <article v-for="item in files" :key="item.path" :class="['asset', {selected:selected.includes(item.path)}]" @click="toggle(item.path)" @dblclick="showPreview(item)">
            <div class="thumb"><el-icon><VideoCamera v-if="item.type==='video'"/><Picture v-else/></el-icon><span>{{ item.type==='video'?'视频':'图片' }}</span><i v-if="selected.includes(item.path)"><el-icon><Check /></el-icon></i></div>
            <strong>{{ item.name }}</strong><small>{{ size(item.size) }}</small>
          </article>
        </div>
        <div v-else class="empty-state"><el-icon :size="36"><FolderOpened /></el-icon><p>选择一个素材文件夹，建立今天的镜头清单。</p></div>
      </div>
    </section>

    <el-dialog v-model="categoryDialog" title="保存为素材分类" width="430px"><el-form label-position="top"><el-form-item label="分类名称"><el-input v-model="newCategory" placeholder="例如：门店环境" /></el-form-item><el-form-item label="目录"><el-input v-model="currentDir" readonly /><el-button text @click="chooseFolder(false)">重新选择</el-button></el-form-item></el-form><template #footer><el-button @click="categoryDialog=false">取消</el-button><el-button type="primary" @click="saveCategory">保存分类</el-button></template></el-dialog>
    <el-dialog v-model="preview.visible" :title="preview.item?.name" width="760px" destroy-on-close><video v-if="preview.item?.type==='video'" :src="preview.url" controls autoplay class="preview-media"/><img v-else :src="preview.url" class="preview-media"/></el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api, { apiError } from '@/api'
const router=useRouter();const categories=ref([]);const activeCategory=ref(null);const currentDir=ref('');const files=ref([]);const selected=ref([]);const recursive=ref(false);const loading=ref(false);const categoryDialog=ref(false);const newCategory=ref('');const preview=reactive({visible:false,item:null,url:''})
async function loadCategories(){categories.value=(await api.get('/api/materials/categories')).data}
async function chooseFolder(scanAfter=true){const path=await window.desktop?.selectFolder?.();if(path){currentDir.value=path;activeCategory.value=null;if(scanAfter)await scan()}}
async function scan(){loading.value=true;selected.value=[];try{const {data}=await api.get('/api/materials/scan',{params:{root_dir:currentDir.value,recursive:recursive.value}});files.value=data.files;if(data.truncated)ElMessage.warning('素材较多，仅显示前1000项')}catch(error){ElMessage.error(apiError(error,'扫描失败'))}finally{loading.value=false}}
async function openCategory(item){activeCategory.value=item;currentDir.value=item.root_dir;await scan()}
function toggle(path){selected.value=selected.value.includes(path)?selected.value.filter(value=>value!==path):[...selected.value,path]}
async function showPreview(item){preview.item=item;preview.url=await window.desktop?.fileUrl?.(item.path) || '';preview.visible=Boolean(preview.url);if(!preview.url)ElMessage.warning('请在桌面应用中预览本地素材')}
async function saveCategory(){if(!newCategory.value.trim()||!currentDir.value)return ElMessage.warning('请填写名称并选择目录');try{await api.post('/api/materials/category',{name:newCategory.value,root_dir:currentDir.value});await loadCategories();categoryDialog.value=false;newCategory.value='';ElMessage.success('分类已保存')}catch(error){ElMessage.error(apiError(error))}}
async function removeCategory(item){await ElMessageBox.confirm(`删除分类“${item.name}”？原素材不会被删除。`,'删除分类',{type:'warning'});try{await api.delete(`/api/materials/category/${item.id}`);if(activeCategory.value?.id===item.id){activeCategory.value=null;files.value=[]}await loadCategories()}catch(error){ElMessage.error(apiError(error))}}
function sendToMix(){localStorage.setItem('storex:selected-media',JSON.stringify(selected.value));router.push('/mix')}
function shortPath(value){return value.length>24?'…'+value.slice(-23):value}function size(bytes){if(bytes<1024*1024)return `${(bytes/1024).toFixed(0)} KB`;return `${(bytes/1024/1024).toFixed(1)} MB`}
onMounted(()=>loadCategories().catch(error=>ElMessage.error(apiError(error))))
</script>

<style scoped>
.library{min-height:610px;display:grid;grid-template-columns:220px 1fr;overflow:hidden}.categories{padding:18px 12px;border-right:1px solid var(--line);background:rgba(7,16,27,.34)}.cat-head{display:flex;align-items:center;justify-content:space-between;padding:0 8px 12px;color:var(--muted);font-size:10px;letter-spacing:.13em}.categories>button{position:relative;width:100%;display:flex;flex-direction:column;gap:3px;padding:10px 28px 10px 11px;border:0;border-radius:9px;color:#a8b9c7;background:transparent;text-align:left;cursor:pointer}.categories>button:hover,.categories>button.active{color:var(--paper);background:rgba(244,185,66,.09)}.categories>button.active{box-shadow:inset 2px 0 var(--amber)}.categories small{max-width:150px;overflow:hidden;color:#536b80;font-size:9px}.categories>button>.el-icon{position:absolute;right:9px;top:13px;opacity:0}.categories>button:hover>.el-icon{opacity:1;color:var(--danger)}.asset-area{min-width:0}.asset-toolbar{display:flex;align-items:center;justify-content:space-between;padding:16px 19px;border-bottom:1px solid var(--line)}.asset-toolbar strong,.asset-toolbar span{display:block}.asset-toolbar strong{font-size:13px}.asset-toolbar span{margin-top:3px;color:#60788c;font-size:9px}.asset-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;padding:16px;max-height:550px;overflow:auto}.asset{padding:9px;border:1px solid var(--line);border-radius:11px;background:rgba(7,16,27,.45);cursor:pointer}.asset.selected{border-color:rgba(244,185,66,.65);box-shadow:0 0 0 2px rgba(244,185,66,.08)}.thumb{position:relative;height:100px;display:grid;place-items:center;border-radius:8px;background:linear-gradient(145deg,#13283c,#0a1420);color:#6d8498;font-size:28px}.thumb>span{position:absolute;left:7px;bottom:6px;padding:2px 5px;border-radius:5px;background:rgba(0,0,0,.45);font-size:8px}.thumb>i{position:absolute;right:7px;top:7px;width:20px;height:20px;display:grid;place-items:center;border-radius:50%;color:#171307;background:var(--amber);font-size:11px}.asset>strong{display:block;margin:9px 2px 3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px}.asset>small{margin-left:2px;color:#60788c;font-size:9px}.preview-media{display:block;width:100%;max-height:65vh;object-fit:contain;background:#050a10}@media(max-width:950px){.library{grid-template-columns:1fr}.categories{display:none}}
</style>

