import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PlayView from '../views/PlayView.vue'
import ImageUploadView from '../views/ImageUploadView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/play/:filename', name: 'play', component: PlayView },
  { path: '/upload-image/:audioFilename', name: 'upload-image', component: ImageUploadView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
