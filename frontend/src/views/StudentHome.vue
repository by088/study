<template>
  <section>
    <h2>学生端最小闭环</h2>
    <div class="ops">
      <button @click="runDemo">注册并登录演示账号</button>
      <button @click="loadRooms" :disabled="!token">加载教室与座位</button>
      <button @click="makeReservation" :disabled="!token || !firstRoom || !firstSeat">提交预约</button>
    </div>
    <pre>{{ output }}</pre>
  </section>
</template>

<script setup>
import { ref } from "vue";
import { register, login, listRooms, listSeats, createReservation } from "../api/client";

const token = ref("");
const firstRoom = ref(null);
const firstSeat = ref(null);
const output = ref("等待操作");

const runDemo = async () => {
  try {
    await register({ user_id: "stu1001", name: "演示学生", password: "Pass1234", email: "stu1001@example.com" });
  } catch (_) {
    // user may already exist
  }
  const res = await login({ user_id: "stu1001", password: "Pass1234" });
  token.value = res.data.token;
  output.value = JSON.stringify(res.data, null, 2);
};

const loadRooms = async () => {
  const roomsRes = await listRooms(token.value);
  const rooms = roomsRes.data;
  firstRoom.value = rooms[0];
  if (!firstRoom.value) {
    output.value = "暂无可用教室";
    return;
  }
  const seatsRes = await listSeats(token.value, firstRoom.value.id);
  firstSeat.value = seatsRes.data[0];
  output.value = JSON.stringify({ room: firstRoom.value, firstSeat: firstSeat.value }, null, 2);
};

const makeReservation = async () => {
  const today = new Date().toISOString().slice(0, 10);
  const data = await createReservation(token.value, {
    room_id: firstRoom.value.id,
    seat_id: firstSeat.value.id,
    reserve_date: today,
    start_hour: 20,
    hours: 2
  });
  output.value = JSON.stringify(data.data, null, 2);
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
