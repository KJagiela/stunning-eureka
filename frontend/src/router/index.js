import { createRouter, createWebHistory } from 'vue-router'
import JobTinder from "../views/JobTinder.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: JobTinder
    },
  ]
})

export default router
