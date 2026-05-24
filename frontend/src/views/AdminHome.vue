<template>
  <section class="admin-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">Operations Console</span>
        <h2>运营管理台</h2>
      </div>
      <div class="admin-state" :class="{ muted: !token }">
        <span>{{ admin.user_id }}</span>
        <strong>{{ token ? "已授权" : "未登录" }}</strong>
      </div>
    </header>

    <section class="login-band">
      <label>
        <span>管理员账号</span>
        <input v-model="admin.user_id" placeholder="admin001" />
      </label>
      <label>
        <span>密码</span>
        <input v-model="admin.password" type="password" placeholder="Pass1234" />
      </label>
      <button class="btn primary" @click="loginAdmin">登录</button>
    </section>

    <section v-if="token" class="ops-grid">
      <div class="metric">
        <span>用户操作</span>
        <strong>{{ counters.users }}</strong>
      </div>
      <div class="metric">
        <span>房间操作</span>
        <strong>{{ counters.rooms }}</strong>
      </div>
      <div class="metric">
        <span>座位操作</span>
        <strong>{{ counters.seats }}</strong>
      </div>
      <div class="metric">
        <span>预约操作</span>
        <strong>{{ counters.reservations }}</strong>
      </div>
    </section>

    <section v-if="token" class="module-grid">
      <div class="panel user-panel">
        <div class="panel-head">
          <h3>用户</h3>
          <button class="btn ghost" @click="loadUsers">查询</button>
        </div>
        <div class="form-grid">
          <label><span>用户ID</span><input v-model="newUser.id" placeholder="stu3001" /></label>
          <label><span>姓名</span><input v-model="newUser.name" placeholder="新用户" /></label>
          <label><span>密码</span><input v-model="newUser.password" placeholder="Pass1234" /></label>
          <label><span>邮箱</span><input v-model="newUser.email" placeholder="user@example.com" /></label>
          <label><span>院系</span><input v-model="newUser.department" placeholder="计算机科学与技术学院" /></label>
        </div>
        <button class="btn primary full" @click="createUserAction">新增用户</button>
      </div>

      <div class="panel room-panel">
        <div class="panel-head">
          <h3>房间</h3>
          <button class="btn ghost" @click="loadRooms">查询</button>
        </div>
        <div class="form-grid compact">
          <label><span>校区</span><input v-model="newRoom.campus" /></label>
          <label><span>楼栋</span><input v-model="newRoom.building" /></label>
          <label><span>房间名</span><input v-model="newRoom.name" /></label>
          <label><span>所属院系</span><input v-model="newRoom.department" placeholder="留空=全校开放" /></label>
          <label class="check"><input v-model="newRoom.open_to_all" type="checkbox" />全校开放</label>
        </div>
        <button class="btn primary full" @click="createRoomAction">新增房间</button>
      </div>

      <div class="panel seat-panel">
        <div class="panel-head">
          <h3>座位</h3>
          <button class="btn ghost" @click="loadSeats">查询</button>
        </div>
        <div class="form-grid compact">
          <label><span>房间ID</span><input v-model.number="newSeat.room_id" type="number" /></label>
          <label><span>座位号</span><input v-model="newSeat.seat_code" /></label>
          <label class="check"><input v-model="newSeat.has_power" type="checkbox" />可充电</label>
          <label class="check"><input v-model="newSeat.by_window" type="checkbox" />靠窗</label>
        </div>
        <button class="btn primary full" @click="createSeatAction">新增座位</button>
      </div>

      <div class="panel reservation-panel">
        <div class="panel-head">
          <h3>预约</h3>
          <button class="btn ghost" @click="loadReservations">查询</button>
        </div>
        <div class="form-grid reservation-grid">
          <label><span>用户ID</span><input v-model="newReservation.user_id" placeholder="stu3001" /></label>
          <label><span>房间ID</span><input v-model.number="newReservation.room_id" type="number" /></label>
          <label><span>座位ID</span><input v-model.number="newReservation.seat_id" type="number" /></label>
          <label><span>日期</span><input v-model="newReservation.reserve_date" /></label>
          <label><span>开始</span><input v-model.number="newReservation.start_hour" type="number" /></label>
          <label><span>时长</span><input v-model.number="newReservation.hours" type="number" /></label>
        </div>
        <button class="btn primary full" @click="createReservationAction">新增预约</button>
      </div>

      <div class="panel task-panel">
        <div class="panel-head">
          <h3>参数与任务</h3>
          <button class="btn ghost" @click="loadParams">参数</button>
        </div>
        <div class="param-row">
          <label><span>参数名</span><input v-model="param.key" /></label>
          <label><span>参数值</span><input v-model="param.value" /></label>
          <button class="btn secondary" @click="upsertParamAction">更新</button>
        </div>
        <div class="task-grid">
          <button class="task" @click="doBefore15"><span>T-15</span><strong>预约前提醒</strong></button>
          <button class="task" @click="doAfter10"><span>T+10</span><strong>签到后提醒</strong></button>
          <button class="task warning" @click="doSweepDefaults"><span>违约</span><strong>清扫待签到</strong></button>
          <button class="task done" @click="doSweepFinished"><span>结束</span><strong>完成预约</strong></button>
        </div>
      </div>

      <div class="panel result-panel">
        <div class="panel-head">
          <h3>最近结果</h3>
          <span class="chip">{{ lastAction }}</span>
        </div>
        <pre>{{ output }}</pre>
      </div>
    </section>
  </section>
</template>

<script setup>
import { ref } from "vue";
import {
  login,
  listUsers,
  createUser,
  listAdminRooms,
  createAdminRoom,
  listAdminSeats,
  createAdminSeat,
  listAdminReservations,
  createAdminReservation,
  listParams,
  upsertParam,
  notifyBefore15,
  notifyAfter10,
  sweepDefaults,
  sweepFinished,
} from "../api/client";

const token = ref("");
const output = ref("就绪");
const lastAction = ref("待操作");
const counters = ref({ users: 0, rooms: 0, seats: 0, reservations: 0 });
const admin = ref({ user_id: "admin001", password: "Pass1234" });
const newUser = ref({ id: "", name: "", password: "Pass1234", email: "", department: "" });
const newRoom = ref({ campus: "主校区", building: "教学楼A", name: "A-201", department: "", open_to_all: true, opens_at: "07:00", closes_at: "22:00", enabled: true });
const newSeat = ref({ room_id: 1, seat_code: "1", has_power: false, by_window: false });
const newReservation = ref({ user_id: "", room_id: 1, seat_id: 1, reserve_date: new Date().toISOString().slice(0, 10), start_hour: 20, hours: 2, status: "pending" });
const param = ref({ key: "max_reservation_hours", value: "4" });

const record = (name, data) => {
  lastAction.value = name;
  output.value = JSON.stringify(data, null, 2);
};

const safe = async (name, fn) => {
  try {
    await fn();
  } catch (e) {
    record(name, e.response?.data || e.message);
  }
};

const loginAdmin = () => safe("管理员登录", async () => {
  const res = await login(admin.value);
  token.value = res.data.token;
  record("管理员登录", res.data);
});

const loadUsers = () => safe("查询用户", async () => {
  const res = await listUsers(token.value);
  counters.value.users = Array.isArray(res.data) ? res.data.length : counters.value.users;
  record("查询用户", res.data);
});

const createUserAction = () => safe("新增用户", async () => {
  const res = await createUser(token.value, newUser.value);
  record("新增用户", res.data);
});

const loadRooms = () => safe("查询房间", async () => {
  const res = await listAdminRooms(token.value);
  counters.value.rooms = Array.isArray(res.data) ? res.data.length : counters.value.rooms;
  record("查询房间", res.data);
});

const createRoomAction = () => safe("新增房间", async () => {
  const res = await createAdminRoom(token.value, newRoom.value);
  record("新增房间", res.data);
});

const loadSeats = () => safe("查询座位", async () => {
  const res = await listAdminSeats(token.value, newSeat.value.room_id || undefined);
  counters.value.seats = Array.isArray(res.data) ? res.data.length : counters.value.seats;
  record("查询座位", res.data);
});

const createSeatAction = () => safe("新增座位", async () => {
  const res = await createAdminSeat(token.value, newSeat.value);
  record("新增座位", res.data);
});

const loadReservations = () => safe("查询预约", async () => {
  const res = await listAdminReservations(token.value);
  counters.value.reservations = Array.isArray(res.data) ? res.data.length : counters.value.reservations;
  record("查询预约", res.data);
});

const createReservationAction = () => safe("新增预约", async () => {
  const res = await createAdminReservation(token.value, newReservation.value);
  record("新增预约", res.data);
});

const loadParams = () => safe("查询参数", async () => {
  const res = await listParams(token.value);
  record("查询参数", res.data);
});

const upsertParamAction = () => safe("更新参数", async () => {
  const res = await upsertParam(token.value, param.value);
  record("更新参数", res.data);
});

const doBefore15 = () => safe("T-15提醒", async () => {
  const res = await notifyBefore15();
  record("T-15提醒", res.data);
});

const doAfter10 = () => safe("T+10提醒", async () => {
  const res = await notifyAfter10();
  record("T+10提醒", res.data);
});

const doSweepDefaults = () => safe("违约清扫", async () => {
  const res = await sweepDefaults();
  record("违约清扫", res.data);
});

const doSweepFinished = () => safe("结束清扫", async () => {
  const res = await sweepFinished();
  record("结束清扫", res.data);
});
</script>

<style scoped>
.admin-page {
  display: grid;
  gap: 18px;
}

.page-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: end;
}

.eyebrow {
  color: #8a5b18;
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
}

h2,
h3 {
  margin: 0;
}

h2 {
  font-size: 28px;
}

.admin-state,
.login-band,
.metric,
.panel {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #d8dee8;
  border-radius: 8px;
  box-shadow: 0 10px 24px rgba(23, 32, 51, 0.06);
}

.admin-state {
  min-width: 170px;
  padding: 12px 14px;
  display: grid;
  gap: 4px;
  text-align: right;
}

.admin-state.muted {
  color: #6b7280;
}

.login-band {
  display: grid;
  grid-template-columns: minmax(160px, 1fr) minmax(160px, 1fr) auto;
  gap: 12px;
  align-items: end;
  padding: 16px;
}

.ops-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.metric {
  padding: 14px;
  display: grid;
  gap: 8px;
}

.metric span,
label span {
  color: #64748b;
  font-size: 13px;
}

.metric strong {
  font-size: 22px;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 16px;
  align-items: start;
}

.panel {
  padding: 16px;
}

.user-panel,
.room-panel,
.seat-panel {
  grid-column: span 4;
}

.reservation-panel,
.task-panel,
.result-panel {
  grid-column: span 6;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.form-grid {
  display: grid;
  gap: 10px;
}

.form-grid.compact {
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
}

.reservation-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

label {
  display: grid;
  gap: 6px;
  font-weight: 700;
}

label.check {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 38px;
  color: #334155;
}

input {
  min-height: 38px;
  border: 1px solid #c8d0db;
  border-radius: 8px;
  padding: 8px 10px;
  color: #172033;
  background: #fff;
}

.btn {
  min-height: 38px;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 8px 12px;
  font-weight: 800;
}

.btn.full {
  width: 100%;
  margin-top: 12px;
}

.primary {
  background: #265c53;
  color: #fff;
}

.secondary {
  background: #f6e7c7;
  color: #5a3b0e;
  border-color: #e1b45f;
}

.ghost {
  background: #f4f7fb;
  color: #334155;
  border-color: #d8dee8;
}

.param-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 10px;
  align-items: end;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-top: 14px;
}

.task {
  min-height: 76px;
  border: 1px solid #d8dee8;
  border-radius: 8px;
  background: #f8fafc;
  color: #172033;
  display: grid;
  place-items: center;
  gap: 4px;
}

.task span {
  color: #265c53;
  font-weight: 900;
}

.task.warning span {
  color: #be5437;
}

.task.done span {
  color: #5a3b0e;
}

.chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  border-radius: 999px;
  background: #edf4f2;
  color: #265c53;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 800;
}

.result-panel pre {
  max-height: 370px;
  overflow: auto;
  margin: 0;
  padding: 12px;
  border-radius: 8px;
  background: #172033;
  color: #e6f4ef;
  white-space: pre-wrap;
}

@media (max-width: 1100px) {
  .user-panel,
  .room-panel,
  .seat-panel,
  .reservation-panel,
  .task-panel,
  .result-panel {
    grid-column: span 12;
  }
}

@media (max-width: 760px) {
  .page-head {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-state {
    text-align: left;
  }

  .login-band,
  .ops-grid,
  .form-grid.compact,
  .reservation-grid,
  .param-row,
  .task-grid {
    grid-template-columns: 1fr;
  }
}
</style>
