import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PlayView from '../views/PlayView.vue'
import ImageUploadView from '../views/ImageUploadView.vue'
import MyStatsView from '../views/MyStatsView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/play/:filename', name: 'play', component: PlayView },
  { path: '/upload-image/:audioFilename', name: 'upload-image', component: ImageUploadView },
  { path: '/mine', name: 'mine', component: MyStatsView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
