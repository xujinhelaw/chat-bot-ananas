import { createRouter, createWebHistory } from "vue-router";
import ChatView from "@/views/ChatView.vue";
import RagManage from "@/views/RagManage.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: ChatView,
  },
  // 可以添加其他路由
  {
    path: "/rag-manage",
    name: "RagManage",
    component: RagManage,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
