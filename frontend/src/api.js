// frontend/src/api.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000", // backend FastAPI kamu
});

// Tambah token JWT ke setiap request jika ada
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
