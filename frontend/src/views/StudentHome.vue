<template>
  <section class="student-page">
    <!-- ====== Toast 消息提示 ====== -->
    <transition-group name="toast-fade" tag="div" class="toast-container">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="t.type">
        {{ t.msg }}
      </div>
    </transition-group>

    <header class="page-head">
      <div>
        <span class="eyebrow">Student Console</span>
        <h2>学生预约工作台</h2>
      </div>
      <div class="profile-strip" :class="{ muted: !profile }">
        <span>{{ profile ? profile.user_name : "未登录" }}</span>
        <small v-if="profile && profile.department">{{ profile.department }}</small>
        <strong>{{ profile ? `${profile.credits} 信用分` : "请先登录" }}</strong>
      </div>
    </header>

    <section class="auth-panel">
      <div class="field-grid">
        <label>
          <span>学号</span>
          <input v-model="form.user_id" placeholder="stu2001" />
        </label>
        <label>
          <span>姓名</span>
          <input v-model="form.name" placeholder="演示学生" />
        </label>
        <label>
          <span>邮箱</span>
          <input v-model="form.email" placeholder="stu2001@example.com" />
        </label>
        <label>
          <span>院系</span>
          <input v-model="form.department" placeholder="计算机科学与技术学院" />
        </label>
        <label>
          <span>密码</span>
          <input v-model="form.password" type="password" placeholder="Pass1234" />
        </label>
      </div>
      <div class="action-row">
        <button class="btn secondary" @click="doRegister">注册</button>
        <button class="btn primary" @click="doLogin">登录并加载数据</button>
      </div>
    </section>

    <section v-if="token" class="summary-grid">
      <div class="metric">
        <span>当前校区</span>
        <strong>{{ selectedCampus || "未选择" }}</strong>
      </div>
      <div class="metric">
        <span>可选房间</span>
        <strong>{{ rooms.length }}</strong>
      </div>
      <div class="metric">
        <span>当前预约</span>
        <strong>{{ currentReservations.length || "无" }}</strong>
      </div>
      <div class="metric">
        <span>历史记录</span>
        <strong>{{ history.length }}</strong>
      </div>
    </section>

    <!-- ====== 步骤流程引导 ====== -->
    <nav v-if="token" class="step-bar">
      <div class="step" :class="{ active: currentStep === 1, done: currentStep > 1 }">
        <span class="step-num">1</span>
        <span class="step-label">选择房间</span>
      </div>
      <div class="step-line" :class="{ filled: currentStep > 1 }"></div>
      <div class="step" :class="{ active: currentStep === 2, done: currentStep > 2 }">
        <span class="step-num">2</span>
        <span class="step-label">选择时间</span>
      </div>
      <div class="step-line" :class="{ filled: currentStep > 2 }"></div>
      <div class="step" :class="{ active: currentStep === 3, done: currentStep > 3 }">
        <span class="step-num">3</span>
        <span class="step-label">点击座位</span>
      </div>
      <div class="step-line" :class="{ filled: currentStep > 3 }"></div>
      <div class="step" :class="{ active: currentStep === 4 }">
        <span class="step-num">4</span>
        <span class="step-label">提交预约</span>
      </div>
    </nav>

    <section v-if="token" class="work-grid">
      <div class="panel catalog-panel">
        <div class="panel-head">
          <h3>
            <span class="step-badge">1</span>
            空间筛选
          </h3>
          <button class="btn ghost" @click="loadRooms">刷新</button>
        </div>

        <div class="select-row">
          <label>
            <span>校区</span>
            <select v-model="selectedCampus" @change="loadBuildings">
              <option value="">全部校区</option>
              <option v-for="c in campus" :key="c.campus_id" :value="c.campus_id">
                {{ c.campus_name }}
              </option>
            </select>
          </label>
          <label>
            <span>楼栋</span>
            <select v-model="selectedBuilding" @change="loadRooms">
              <option value="">全部楼栋</option>
              <option v-for="b in buildings" :key="b.building_id" :value="b.building_id">
                {{ b.building_name }}
              </option>
            </select>
          </label>
        </div>

        <div class="room-list">
          <button
            v-for="r in rooms"
            :key="r.room_id"
            class="room-item"
            :class="{ active: selectedRoom?.room_id === r.room_id }"
            @click="selectRoom(r)"
          >
            <span>
              <strong>{{ r.room_name }}</strong>
              <small>ID {{ r.room_id }}</small>
            </span>
            <span class="room-meta">
              {{ r.number_of_seats }} 座 / {{ r.have_charge }} 电源
              <em v-if="r.department && !r.open_to_all" class="dept-tag">{{ r.department }}</em>
            </span>
          </button>
          <div v-if="!rooms.length" class="empty">暂无房间数据</div>
        </div>
      </div>

      <div class="panel booking-panel">
        <div class="panel-head">
          <h3>
            <span class="step-badge">2-4</span>
            座位预约
          </h3>
          <span class="chip">{{ selectedRoom ? selectedRoom.room_name : "请先选择房间" }}</span>
        </div>

        <!-- 时间与时长选择 -->
        <div class="booking-form">
          <label>
            <span>开始小时</span>
            <input v-model.number="reserve.time_start" type="number" min="7" max="22" @change="onTimeChange" />
          </label>
          <label>
            <span>预约时长</span>
            <select v-model.number="reserve.reservation_hours">
              <option :value="1">1 小时</option>
              <option :value="2">2 小时</option>
              <option :value="3">3 小时</option>
              <option :value="4">4 小时</option>
            </select>
          </label>
          <label>
            <span>已选座位</span>
            <div class="selected-seat-display">
              <strong v-if="reserve.seat_number">{{ reserve.seat_number }} 号座位</strong>
              <span v-else class="hint">请在下方座位图中点击选择</span>
            </div>
          </label>
        </div>

        <div class="action-row">
          <button class="btn secondary" :disabled="!selectedRoom" @click="loadSeatStatus">
            查看座位状态
          </button>
          <button
            class="btn primary"
            :disabled="!selectedRoom || !reserve.seat_number"
            @click="book"
          >
            提交预约
          </button>
          <span v-if="!reserve.seat_number && seatCells.length" class="hint-inline">
            请先在座位图中点选一个座位
          </span>
        </div>

        <!-- 座位图 - 可点击选座 -->
        <div class="seat-board">
          <div
            v-for="seat in seatCells"
            :key="seat.index"
            class="seat"
            :class="[
              seat.kind,
              { power: seat.power, selected: String(reserve.seat_number) === String(seat.index), clickable: seat.kind !== 'blocked' }
            ]"
            :title="seat.title"
            @click="pickSeat(seat)"
          >
            <span>{{ seat.index }}</span>
            <small>{{ seat.label }}</small>
          </div>
          <div v-if="!seatCells.length" class="empty">
            {{ selectedRoom ? '点击「查看座位状态」加载座位图' : '请先在左侧选择房间' }}
          </div>
        </div>

        <div class="legend">
          <span><i class="available"></i>可预约</span>
          <span><i class="limited"></i>时长受限</span>
          <span><i class="blocked"></i>不可预约</span>
          <span><i class="power-dot"></i>可充电</span>
          <span><i class="selected-dot"></i>已选中</span>
        </div>
      </div>

      <div class="panel reservation-panel">
        <div class="panel-head">
          <h3>当前预约 <small v-if="currentReservations.length" class="count-badge">{{ currentReservations.length }}</small></h3>
          <button class="btn ghost" @click="loadInvalid">刷新</button>
        </div>

        <div v-if="currentReservations.length" class="reservation-list">
          <div
            v-for="r in currentReservations"
            :key="r.reservation_id"
            class="reservation-ticket"
            :class="{ 'active-ticket': r.reservation_status === '1' }"
          >
            <strong>{{ r.room_name }}</strong>
            <span>座位 {{ r.seat_number }}</span>
            <span>{{ r.date }} {{ r.reservation_time }}（{{ r.reservation_hours }}小时）</span>
            <span v-if="r.reservation_status === '0'" class="status-pill pending-pill">待签到</span>
            <span v-else class="status-pill active-pill">已签到 · 使用中</span>
            <div v-if="r.reservation_status === '0'" class="action-row">
              <button class="btn primary" @click="sign(r.reservation_id)">签到</button>
              <button class="btn danger" @click="cancel(r.reservation_id)">取消</button>
            </div>
          </div>
        </div>
        <div v-else class="empty">暂无进行中的预约</div>
      </div>

      <div class="panel history-panel">
        <div class="panel-head">
          <h3>历史记录</h3>
          <button class="btn ghost" @click="loadHistory">刷新</button>
        </div>
        <div class="table-wrap">
          <table v-if="history.length">
            <thead>
              <tr>
                <th>ID</th>
                <th>房间</th>
                <th>座位</th>
                <th>时间</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="h in history" :key="h.reservation_id">
                <td>{{ h.reservation_id }}</td>
                <td>{{ h.room_name }}</td>
                <td>{{ h.seat_number }}</td>
                <td>{{ h.date }} {{ h.reservation_time }}</td>
                <td><span class="status-pill">{{ renderStatus(h.reservation_status) }}</span></td>
              </tr>
            </tbody>
          </table>
          <div v-else class="empty">暂无历史记录</div>
        </div>
      </div>
    </section>

    <section class="panel log-panel">
      <div class="panel-head">
        <h3>接口返回</h3>
      </div>
      <pre>{{ output }}</pre>
    </section>

    <!-- 智能助手浮窗 -->
    <div class="chat-fab" @click="chatOpen = !chatOpen" title="智能助手">
      <span v-if="!chatOpen">💬</span>
      <span v-else>✕</span>
    </div>

    <transition name="chat-slide">
      <div v-if="chatOpen" class="chat-window">
        <div class="chat-header">
          <strong>智能助手</strong>
          <small>自然语言查座位、查预约</small>
        </div>
        <div class="chat-body" ref="chatBody">
          <div
            v-for="(msg, i) in chatMessages"
            :key="i"
            class="chat-bubble"
            :class="msg.role"
          >
            <pre class="chat-text">{{ msg.text }}</pre>
          </div>
          <div v-if="chatLoading" class="chat-bubble assistant">
            <span class="chat-text typing">思考中...</span>
          </div>
        </div>
        <div class="chat-input-row">
          <input
            v-model="chatInput"
            placeholder="试试：今天晚上还有空座吗？"
            @keydown.enter="sendChat"
          />
          <button class="btn primary" @click="sendChat" :disabled="!chatInput.trim() || chatLoading">
            发送
          </button>
        </div>
        <div class="chat-quick">
          <button @click="quickChat('今天晚上还有空座吗')">有空座吗</button>
          <button @click="quickChat('帮我找靠窗的座位')">靠窗座位</button>
          <button @click="quickChat('我今天定了哪里的座位')">我的预约</button>
          <button @click="quickChat('我的信用分多少')">信用分</button>
          <button @click="quickChat('帮助')">帮助</button>
        </div>
      </div>
    </transition>
  </section>
</template>

<script setup>
import { computed, ref, nextTick } from "vue";
import {
  register,
  login,
  getUserInfo,
  listCampus,
  listBuildings,
  listRooms,
  seatStatus,
  bookSeat,
  reservationInvalid,
  reservationHistory,
  cancelReservation,
  signReservation,
  chatAssistant,
} from "../api/client";

// ---- Toast 消息提示系统 ----
const toasts = ref([]);
let toastId = 0;
const showToast = (msg, type = "info", duration = 3000) => {
  const id = ++toastId;
  toasts.value.push({ id, msg, type });
  setTimeout(() => {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }, duration);
};

const token = ref("");
const output = ref("就绪");
const form = ref({ user_id: "stu2001", name: "演示学生", email: "stu2001@example.com", department: "计算机科学与技术学院", password: "Pass1234" });
const profile = ref(null);
const campus = ref([]);
const buildings = ref([]);
const rooms = ref([]);
const selectedCampus = ref("");
const selectedBuilding = ref("");
const selectedRoom = ref(null);
const reserve = ref({ time_start: 20, seat_number: "", reservation_hours: 2 });
const seatStatusText = ref("");
const invalidReservation = ref(null);
const activeReservation = ref(null);
const currentReservations = ref([]);
const history = ref([]);

// ---- 步骤引导计算 ----
const currentStep = computed(() => {
  if (!selectedRoom.value) return 1;
  if (!seatCells.value.length) return 2;
  if (!reserve.value.seat_number) return 3;
  return 4;
});

const renderStatus = (s) => ({ "0": "未生效", "1": "已生效", "2": "已取消", "3": "已违约", "4": "已结束" }[s] || s);

const seatCells = computed(() => {
  const labels = { a: "无", b: "1h", c: "2h", d: "3h", e: "4h" };
  return [...seatStatusText.value].map((ch, idx) => {
    const lower = ch.toLowerCase();
    const hours = labels[lower] || "-";
    const kind = lower === "a" ? "blocked" : lower === "e" ? "available" : "limited";
    return {
      index: idx + 1,
      kind,
      power: ch !== lower,
      label: hours,
      title: `座位 ${idx + 1} / ${ch !== lower ? "可充电" : "普通"} / ${hours}`,
    };
  });
});

// ---- 座位点击选座 ----
const pickSeat = (seat) => {
  if (seat.kind === "blocked") {
    showToast("该座位不可预约", "error");
    return;
  }
  reserve.value.seat_number = String(seat.index);
  showToast(`已选中 ${seat.index} 号座位${seat.power ? "（可充电）" : ""}`, "success");
};

// 时间变更时自动刷新座位图
const onTimeChange = () => {
  if (selectedRoom.value) {
    loadSeatStatus();
  }
};

const safe = async (fn) => {
  try {
    await fn();
  } catch (e) {
    const errMsg = e.response?.data?.detail || e.response?.data?.message || e.message || "操作失败";
    showToast(errMsg, "error");
    output.value = JSON.stringify(e.response?.data || e.message, null, 2);
  }
};

const doRegister = () => safe(async () => {
  const res = await register(form.value);
  output.value = JSON.stringify(res.data, null, 2);
  if (res.data.success === false) {
    showToast(res.data.message || "注册失败，该学号可能已存在", "error");
  } else {
    showToast("注册成功！请点击「登录并加载数据」", "success");
  }
});

const doLogin = () => safe(async () => {
  const res = await login({ user_id: form.value.user_id, password: form.value.password });
  token.value = res.data.token;
  await loadProfile();
  await loadCampus();
  await loadRooms();
  await loadInvalid();
  await loadHistory();
  output.value = JSON.stringify(res.data, null, 2);
  showToast(`登录成功！欢迎 ${profile.value?.user_name || form.value.name}`, "success");
});

const loadProfile = async () => {
  const res = await getUserInfo(token.value);
  profile.value = res.data.data;
};

const loadCampus = async () => {
  const res = await listCampus(token.value);
  campus.value = res.data.data;
};

const loadBuildings = () => safe(async () => {
  const res = await listBuildings(token.value, selectedCampus.value);
  buildings.value = res.data.data;
  selectedBuilding.value = "";
  await loadRooms();
});

const loadRooms = () => safe(async () => {
  const res = await listRooms(token.value, {
    campus_id: selectedCampus.value || undefined,
    building_id: selectedBuilding.value || undefined,
    is_available: true,
  });
  rooms.value = res.data.data;
});

const selectRoom = (room) => {
  selectedRoom.value = room;
  reserve.value.seat_number = "";
  seatStatusText.value = "";
  showToast(`已选择「${room.room_name}」，请设置时间后查看座位`, "info");
};

const loadSeatStatus = () => safe(async () => {
  const res = await seatStatus(token.value, selectedRoom.value.room_id, reserve.value.time_start);
  seatStatusText.value = res.data.data;
  reserve.value.seat_number = "";
  output.value = JSON.stringify(res.data, null, 2);
  showToast("座位状态已加载，点击绿色/黄色座位选择", "info");
});

const bookingErrors = {
  400: "参数错误或座位不存在",
  401: "信用分不足，无法预约",
  402: "该座位在所选时间段已被占用",
  403: "预约时长超出限制或超出关闭时间",
  405: "今天已有一个未完成的预约，请先取消或签到后再预约",
  406: "所选时间不在自习室开放时间范围内",
  407: "该自习室仅对指定院系学生开放",
};

const book = () => safe(async () => {
  if (!reserve.value.seat_number) {
    showToast("请先在座位图中点选一个座位", "error");
    return;
  }
  const res = await bookSeat(token.value, {
    room_id: selectedRoom.value.room_id,
    seat_number: reserve.value.seat_number,
    reservation_time: reserve.value.time_start,
    reservation_hours: reserve.value.reservation_hours,
  });
  output.value = JSON.stringify(res.data, null, 2);
  if (res.data.success !== false) {
    showToast(`预约成功！${selectedRoom.value.room_name} ${reserve.value.seat_number}号座位`, "success", 4000);
  } else {
    const errMsg = res.data.message || bookingErrors[res.data.code] || `预约失败（错误码 ${res.data.code}）`;
    showToast(errMsg, "error", 4000);
  }
  await loadInvalid();
  await loadHistory();
  await loadSeatStatus();
});

const loadInvalid = () => safe(async () => {
  const res = await reservationInvalid(token.value);
  invalidReservation.value = res.data.success ? res.data.data : null;
  // 收集所有进行中的预约（待签到 + 已签到）
  const histRes = await reservationHistory(token.value);
  const allRecords = histRes.data.data || [];
  currentReservations.value = allRecords.filter(
    (r) => r.reservation_status === "0" || r.reservation_status === "1"
  );
  activeReservation.value = allRecords.find((r) => r.reservation_status === "1") || null;
});

const cancel = (id) => safe(async () => {
  const res = await cancelReservation(token.value, id);
  output.value = JSON.stringify(res.data, null, 2);
  if (res.data.success === false) {
    showToast("取消失败：该预约状态不允许取消", "error");
  } else {
    showToast("预约已取消", "info");
  }
  await loadInvalid();
  await loadHistory();
  await loadProfile();
});

const sign = (id) => safe(async () => {
  const res = await signReservation(token.value, id);
  output.value = JSON.stringify(res.data, null, 2);
  if (res.data.success === false) {
    showToast(res.data.message || "签到失败", "error");
  } else {
    showToast("签到成功！", "success");
  }
  await loadInvalid();
  await loadHistory();
});

const loadHistory = () => safe(async () => {
  const res = await reservationHistory(token.value);
  history.value = res.data.data || [];
});

// ---- 智能助手 ----
const chatOpen = ref(false);
const chatInput = ref("");
const chatLoading = ref(false);
const chatBody = ref(null);
const chatMessages = ref([
  { role: "assistant", text: "你好！我是自习室智能助手，有什么可以帮你的？\n\n试试问我：\"今天晚上还有空座吗\"" },
]);

const scrollChatBottom = () => {
  nextTick(() => {
    if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight;
  });
};

const sendChat = async () => {
  const msg = chatInput.value.trim();
  if (!msg || chatLoading.value) return;
  if (!token.value) {
    chatMessages.value.push({ role: "user", text: msg });
    chatMessages.value.push({ role: "assistant", text: "请先登录后再使用智能助手。" });
    chatInput.value = "";
    scrollChatBottom();
    return;
  }

  chatMessages.value.push({ role: "user", text: msg });
  chatInput.value = "";
  chatLoading.value = true;
  scrollChatBottom();

  try {
    const res = await chatAssistant(token.value, msg);
    chatMessages.value.push({ role: "assistant", text: res.data.reply });
    // 如果是取消操作，刷新预约数据
    if (res.data.intent === "cancel") {
      await loadInvalid();
      await loadHistory();
    }
  } catch (e) {
    chatMessages.value.push({
      role: "assistant",
      text: "抱歉，出了点问题：" + (e.response?.data?.detail || e.message),
    });
  }
  chatLoading.value = false;
  scrollChatBottom();
};

const quickChat = (text) => {
  chatInput.value = text;
  sendChat();
};
</script>

<style scoped>
.student-page {
  display: grid;
  gap: 18px;
}

/* ====== Toast 消息提示 ====== */
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast {
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
  pointer-events: auto;
  max-width: 400px;
}

.toast.success {
  background: #265c53;
}

.toast.error {
  background: #be5437;
}

.toast.info {
  background: #334155;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.3s ease;
}

.toast-fade-enter-from {
  opacity: 0;
  transform: translateX(40px);
}

.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* ====== 步骤流程引导 ====== */
.step-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #d8dee8;
  border-radius: 8px;
  box-shadow: 0 10px 24px rgba(23, 32, 51, 0.06);
}

.step {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 20px;
  background: #f4f7fb;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 700;
  transition: all 0.25s ease;
}

.step.active {
  background: #265c53;
  color: #fff;
  box-shadow: 0 2px 8px rgba(38, 92, 83, 0.3);
}

.step.done {
  background: #edf4f2;
  color: #265c53;
}

.step-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: currentColor;
  color: #fff;
  font-size: 12px;
  font-weight: 900;
}

.step.active .step-num {
  background: #fff;
  color: #265c53;
}

.step.done .step-num {
  background: #265c53;
  color: #fff;
}

.step-line {
  width: 40px;
  height: 2px;
  background: #d8dee8;
  margin: 0 4px;
  transition: background 0.25s;
}

.step-line.filled {
  background: #265c53;
}

.step-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  border-radius: 6px;
  background: #265c53;
  color: #fff;
  font-size: 11px;
  font-weight: 900;
  margin-right: 8px;
  padding: 0 6px;
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

.profile-strip,
.metric,
.panel,
.auth-panel {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #d8dee8;
  border-radius: 8px;
  box-shadow: 0 10px 24px rgba(23, 32, 51, 0.06);
}

.profile-strip {
  min-width: 190px;
  padding: 12px 14px;
  display: grid;
  gap: 4px;
  text-align: right;
}

.profile-strip.muted {
  color: #6b7280;
}

.auth-panel,
.panel {
  padding: 16px;
}

.field-grid,
.booking-form,
.select-row {
  display: grid;
  gap: 12px;
}

.field-grid {
  grid-template-columns: repeat(5, minmax(110px, 1fr));
}

.booking-form,
.select-row {
  grid-template-columns: repeat(3, minmax(110px, 1fr));
}

label {
  display: grid;
  gap: 6px;
  color: #5f6b7a;
  font-size: 13px;
  font-weight: 700;
}

input,
select {
  min-height: 38px;
  border: 1px solid #c8d0db;
  border-radius: 8px;
  padding: 8px 10px;
  color: #172033;
  background: #fff;
}

/* 已选座位展示 */
.selected-seat-display {
  min-height: 38px;
  border: 1px solid #c8d0db;
  border-radius: 8px;
  padding: 8px 10px;
  background: #fff;
  display: flex;
  align-items: center;
}

.selected-seat-display strong {
  color: #265c53;
  font-size: 15px;
}

.selected-seat-display .hint {
  color: #94a3b8;
  font-size: 12px;
  font-weight: 400;
}

.hint-inline {
  color: #94a3b8;
  font-size: 12px;
  font-weight: 400;
  align-self: center;
}

.action-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 12px;
  align-items: center;
}

.btn {
  min-height: 38px;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 8px 12px;
  font-weight: 800;
  cursor: pointer;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.48;
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

.danger {
  background: #be5437;
  color: #fff;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.metric {
  padding: 14px;
  display: grid;
  gap: 8px;
}

.metric span {
  color: #64748b;
  font-size: 13px;
}

.metric strong {
  font-size: 20px;
}

.work-grid {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.catalog-panel,
.reservation-panel {
  grid-column: 1;
}

.booking-panel,
.history-panel {
  grid-column: 2;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.panel-head h3 {
  display: flex;
  align-items: center;
}

.chip,
.status-pill {
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

.room-list {
  display: grid;
  gap: 8px;
  margin-top: 14px;
}

.room-item {
  width: 100%;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  border: 1px solid #d8dee8;
  border-radius: 8px;
  background: #fff;
  padding: 12px;
  color: #172033;
  text-align: left;
  cursor: pointer;
}

.room-item.active {
  border-color: #265c53;
  background: #edf4f2;
}

.room-item span:first-child {
  display: grid;
  gap: 3px;
}

.room-item small,
.room-meta {
  color: #6b7280;
}

.dept-tag {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 7px;
  border-radius: 4px;
  background: #f6e7c7;
  color: #8a5b18;
  font-size: 11px;
  font-style: normal;
  font-weight: 700;
}

.seat-board {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(72px, 1fr));
  gap: 10px;
  min-height: 144px;
}

.seat {
  position: relative;
  min-height: 62px;
  border-radius: 8px;
  border: 1px solid #d8dee8;
  display: grid;
  place-items: center;
  background: #fff;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.seat.clickable {
  cursor: pointer;
}

.seat.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(38, 92, 83, 0.2);
}

.seat.selected {
  border-color: #265c53 !important;
  background: #265c53 !important;
  color: #fff !important;
  box-shadow: 0 0 0 3px rgba(38, 92, 83, 0.25);
}

.seat.selected small {
  color: rgba(255, 255, 255, 0.8) !important;
}

.seat span {
  font-weight: 900;
}

.seat small {
  color: #64748b;
}

.seat.available {
  border-color: #68a678;
  background: #eef8f0;
}

.seat.limited {
  border-color: #e1b45f;
  background: #fff8e8;
}

.seat.blocked {
  border-color: #d7aaa0;
  background: #fff1ed;
  color: #8f3f28;
  cursor: not-allowed;
}

.seat.power::after {
  content: "";
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #265c53;
}

.seat.selected.power::after {
  background: #fff;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
  color: #64748b;
  font-size: 13px;
}

.legend span {
  display: inline-flex;
  gap: 6px;
  align-items: center;
}

.legend i {
  width: 10px;
  height: 10px;
  border-radius: 3px;
}

.legend .available {
  background: #68a678;
}

.legend .limited {
  background: #e1b45f;
}

.legend .blocked {
  background: #be5437;
}

.legend .power-dot {
  border-radius: 50%;
  background: #265c53;
}

.legend .selected-dot {
  background: #265c53;
  border-radius: 3px;
}

.reservation-list {
  display: grid;
  gap: 10px;
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  background: #265c53;
  color: #fff;
  font-size: 11px;
  font-weight: 900;
  margin-left: 6px;
  padding: 0 6px;
}

.reservation-ticket {
  display: grid;
  gap: 8px;
  padding: 14px;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px dashed #c8d0db;
}

.reservation-ticket.active-ticket {
  border-color: #265c53;
  background: #edf4f2;
}

.pending-pill {
  background: #f6e7c7 !important;
  color: #8a5b18 !important;
}

.active-pill {
  background: #265c53 !important;
  color: #fff !important;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 10px;
  border-bottom: 1px solid #e6ebf2;
  text-align: left;
  white-space: nowrap;
}

th {
  color: #64748b;
  font-size: 12px;
}

.empty {
  display: grid;
  place-items: center;
  min-height: 92px;
  color: #7a8797;
  border: 1px dashed #c8d0db;
  border-radius: 8px;
  font-size: 13px;
}

.log-panel pre {
  max-height: 220px;
  overflow: auto;
  margin: 0;
  padding: 12px;
  border-radius: 8px;
  background: #172033;
  color: #e6f4ef;
  white-space: pre-wrap;
}

@media (max-width: 980px) {
  .field-grid,
  .summary-grid,
  .work-grid {
    grid-template-columns: 1fr;
  }

  .catalog-panel,
  .reservation-panel,
  .booking-panel,
  .history-panel {
    grid-column: auto;
  }

  .step-bar {
    flex-wrap: wrap;
    gap: 4px;
  }
}

@media (max-width: 640px) {
  .page-head {
    align-items: stretch;
    flex-direction: column;
  }

  .profile-strip {
    text-align: left;
  }

  .booking-form,
  .select-row {
    grid-template-columns: 1fr;
  }

  .step-label {
    display: none;
  }
}

/* ---- 智能助手浮窗 ---- */
.chat-fab {
  position: fixed;
  bottom: 28px;
  right: 28px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #265c53;
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 22px;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0,0,0,0.22);
  z-index: 1000;
  transition: transform 0.2s;
}
.chat-fab:hover { transform: scale(1.1); }

.chat-window {
  position: fixed;
  bottom: 92px;
  right: 28px;
  width: 380px;
  max-height: 520px;
  background: #fff;
  border: 1px solid #d8dee8;
  border-radius: 14px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.18);
  display: flex;
  flex-direction: column;
  z-index: 999;
  overflow: hidden;
}

.chat-header {
  padding: 14px 16px;
  background: #265c53;
  color: #fff;
  display: grid;
  gap: 2px;
}
.chat-header small { opacity: 0.75; font-size: 12px; }

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  min-height: 180px;
  background: #f8fafb;
}

.chat-bubble {
  max-width: 88%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13.5px;
  line-height: 1.55;
}
.chat-bubble.user {
  align-self: flex-end;
  background: #265c53;
  color: #fff;
  border-bottom-right-radius: 4px;
}
.chat-bubble.assistant {
  align-self: flex-start;
  background: #edf4f2;
  color: #172033;
  border-bottom-left-radius: 4px;
}

.chat-text {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: inherit;
}
.chat-text.typing {
  color: #64748b;
  font-style: italic;
}

.chat-input-row {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid #e6ebf2;
  background: #fff;
}
.chat-input-row input {
  flex: 1;
  min-height: 36px;
  border: 1px solid #c8d0db;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
}
.chat-input-row .btn {
  min-height: 36px;
  font-size: 13px;
  padding: 6px 14px;
}

.chat-quick {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px 12px 12px;
  background: #fff;
}
.chat-quick button {
  border: 1px solid #c8d0db;
  border-radius: 16px;
  background: #f4f7fb;
  color: #334155;
  padding: 4px 12px;
  font-size: 12px;
  cursor: pointer;
  font-weight: 600;
}
.chat-quick button:hover {
  background: #edf4f2;
  border-color: #265c53;
}

/* 过渡动画 */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.25s ease;
}
.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
</style>
