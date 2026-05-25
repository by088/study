import axios from "axios";

// 本地开发时直连后端；Docker 部署时通过 nginx 反向代理，用相对路径即可
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8001";

const client = axios.create({
  baseURL: API_BASE,
  timeout: 8000,
});

const authHeaders = (token) => ({ Authorization: `Bearer ${token}` });

export const register = (payload) => client.post("/v1/register", payload);
export const login = (payload) => client.post("/v1/login", payload);
export const getUserInfo = (token) => client.get("/v1/userInfo", { headers: authHeaders(token) });

export const listCampus = (token) => client.get("/v1/campus", { headers: authHeaders(token) });
export const listBuildings = (token, campus_id) =>
  client.get("/v1/building", { headers: authHeaders(token), params: { campus_id } });
export const listRooms = (token, params) =>
  client.get("/v1/studyroom", { headers: authHeaders(token), params });
export const seatStatus = (token, room_id, time_start) =>
  client.get("/v1/studyroom/seatstatus", { headers: authHeaders(token), params: { room_id, time_start } });

export const bookSeat = (token, payload) => client.post("/v1/studyroom/booking", payload, { headers: authHeaders(token) });
export const reservationInvalid = (token) => client.get("/v1/reservations/invalid", { headers: authHeaders(token) });
export const reservationHistory = (token) => client.get("/v1/reservations/info", { headers: authHeaders(token) });
export const cancelReservation = (token, reservation_id) =>
  client.put("/v1/reservations/cancel", null, { headers: authHeaders(token), params: { reservation_id } });
export const signReservation = (token, reservation_id) =>
  client.get("/v1/reservations/sign", { headers: authHeaders(token), params: { reservation_id } });

export const listUsers = (token) => client.get("/v1/admin/users", { headers: authHeaders(token) });
export const createUser = (token, payload) => client.post("/v1/admin/users", payload, { headers: authHeaders(token) });
export const updateUser = (token, userId, payload) =>
  client.patch(`/v1/admin/users/${userId}`, payload, { headers: authHeaders(token) });
export const deleteUser = (token, userId) => client.delete(`/v1/admin/users/${userId}`, { headers: authHeaders(token) });

export const listAdminRooms = (token) => client.get("/v1/admin/rooms", { headers: authHeaders(token) });
export const createAdminRoom = (token, payload) => client.post("/v1/admin/rooms", payload, { headers: authHeaders(token) });
export const updateAdminRoom = (token, roomId, payload) =>
  client.patch(`/v1/admin/rooms/${roomId}`, payload, { headers: authHeaders(token) });
export const deleteAdminRoom = (token, roomId) => client.delete(`/v1/admin/rooms/${roomId}`, { headers: authHeaders(token) });

export const listAdminSeats = (token, roomId) =>
  client.get("/v1/admin/seats", { headers: authHeaders(token), params: roomId ? { room_id: roomId } : {} });
export const createAdminSeat = (token, payload) => client.post("/v1/admin/seats", payload, { headers: authHeaders(token) });
export const updateAdminSeat = (token, seatId, payload) =>
  client.patch(`/v1/admin/seats/${seatId}`, payload, { headers: authHeaders(token) });
export const deleteAdminSeat = (token, seatId) => client.delete(`/v1/admin/seats/${seatId}`, { headers: authHeaders(token) });

export const listAdminReservations = (token) => client.get("/v1/admin/reservations", { headers: authHeaders(token) });
export const createAdminReservation = (token, payload) =>
  client.post("/v1/admin/reservations", payload, { headers: authHeaders(token) });
export const updateAdminReservation = (token, reservationId, payload) =>
  client.patch(`/v1/admin/reservations/${reservationId}`, payload, { headers: authHeaders(token) });
export const deleteAdminReservation = (token, reservationId) =>
  client.delete(`/v1/admin/reservations/${reservationId}`, { headers: authHeaders(token) });

export const listParams = (token) => client.get("/v1/admin/params", { headers: authHeaders(token) });
export const upsertParam = (token, payload) => client.put("/v1/admin/params", payload, { headers: authHeaders(token) });

export const notifyBefore15 = () => client.post("/v1/jobs/notify-before-15");
export const notifyAfter10 = () => client.post("/v1/jobs/notify-after-10");
export const sweepDefaults = () => client.post("/v1/jobs/sweep-defaults");
export const sweepFinished = () => client.post("/v1/jobs/sweep-finished");

export const chatAssistant = (token, message) =>
  client.post("/v1/assistant", { message }, { headers: authHeaders(token) });
