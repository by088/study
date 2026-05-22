import axios from "axios";

const client = axios.create({
  baseURL: "http://localhost:8001",
  timeout: 8000
});

export const register = (payload) => client.post("/v1/auth/register", payload);
export const login = (payload) => client.post("/v1/auth/login", payload);
export const getMe = (token) => client.get("/v1/auth/me", { headers: { Authorization: `Bearer ${token}` } });

export const validateSlot = (payload) => client.post("/v1/bookings/validate", payload);
export const listStories = () => client.get("/v1/stories");
export const listRooms = (token) => client.get("/v1/rooms", { headers: { Authorization: `Bearer ${token}` } });
export const listSeats = (token, roomId) => client.get(`/v1/rooms/${roomId}/seats`, { headers: { Authorization: `Bearer ${token}` } });

export const createReservation = (token, payload) => client.post("/v1/reservations", payload, { headers: { Authorization: `Bearer ${token}` } });
export const myReservations = (token) => client.get("/v1/reservations/mine", { headers: { Authorization: `Bearer ${token}` } });

export const listUsers = (token) => client.get("/v1/admin/users", { headers: { Authorization: `Bearer ${token}` } });
export const listAdminSeats = (token, roomId) => client.get("/v1/admin/seats", { headers: { Authorization: `Bearer ${token}` }, params: roomId ? { room_id: roomId } : {} });
export const listParams = (token) => client.get("/v1/admin/params", { headers: { Authorization: `Bearer ${token}` } });
export const notifyBefore15 = () => client.post("/v1/jobs/notify-before-15");
export const notifyAfter10 = () => client.post("/v1/jobs/notify-after-10");
