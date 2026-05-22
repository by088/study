<template>
  <section>
    <h2>管理端最小闭环</h2>
    <div class="ops">
      <button @click="loginAdmin">管理员登录</button>
      <button @click="loadUsers" :disabled="!token">用户列表</button>
      <button @click="loadSeats" :disabled="!token">座位列表</button>
      <button @click="loadParams" :disabled="!token">系统参数</button>
      <button @click="triggerBefore15">提醒任务 T-15</button>
      <button @click="triggerAfter10">提醒任务 T+10</button>
    </div>
    <pre>{{ output }}</pre>
  </section>
</template>

<script setup>
import { ref } from "vue";
import {
  register,
  login,
  listUsers,
  listAdminSeats,
  listParams,
  notifyBefore15,
  notifyAfter10
} from "../api/client";

const token = ref("");
const output = ref("等待操作");

const loginAdmin = async () => {
  try {
    await register({ user_id: "admin001", name: "系统管理员", password: "Pass1234", email: "admin001@example.com" });
  } catch (_) {
    // already exists
  }
  const res = await login({ user_id: "admin001", password: "Pass1234" });
  token.value = res.data.token;
  output.value = "管理员已登录。注意：当前账号默认未绑定admin角色，需要在DB中分配role后才能访问受限管理接口。";
};

const loadUsers = async () => {
  try {
    const res = await listUsers(token.value);
    output.value = JSON.stringify(res.data, null, 2);
  } catch (e) {
    output.value = e.response?.data?.detail || e.message;
  }
};

const loadSeats = async () => {
  try {
    const res = await listAdminSeats(token.value);
    output.value = JSON.stringify(res.data, null, 2);
  } catch (e) {
    output.value = e.response?.data?.detail || e.message;
  }
};

const loadParams = async () => {
  try {
    const res = await listParams(token.value);
    output.value = JSON.stringify(res.data, null, 2);
  } catch (e) {
    output.value = e.response?.data?.detail || e.message;
  }
};

const triggerBefore15 = async () => {
  const res = await notifyBefore15();
  output.value = JSON.stringify(res.data, null, 2);
};

const triggerAfter10 = async () => {
  const res = await notifyAfter10();
  output.value = JSON.stringify(res.data, null, 2);
};
</script>

<style scoped>
.ops {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}
</style>
