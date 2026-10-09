import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/activate', name: 'Activate', component: () => import('../views/Activate.vue') },
  { path: '/persona', name: 'Persona', component: () => import('../views/Persona.vue') },
  { path: '/materials', name: 'Materials', component: () => import('../views/Materials.vue') },
  { path: '/mix', name: 'Mix', component: () => import('../views/MixEditor.vue') },
  { path: '/batch', name: 'Batch', component: () => import('../views/BatchGeneration.vue') },
  { path: '/industry', name: 'Industry', component: () => import('../views/IndustryTemplates.vue') },
  { path: '/publish', name: 'Publish', component: () => import('../views/Publish.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../views/Settings.vue') },
]

export default createRouter({ history: createWebHashHistory(), routes })
