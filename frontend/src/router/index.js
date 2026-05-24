import { createRouter, createWebHistory } from "vue-router";
import StudentHome from "../views/StudentHome.vue";
import AdminHome from "../views/AdminHome.vue";

const routes = [
  { path: "/", component: StudentHome },
  { path: "/admin", component: AdminHome }
];

export default createRouter({
  history: createWebHistory(),
  routes
});
