import axios from "axios";

const apiKey = typeof import.meta !== "undefined" ? import.meta.env?.VITE_API_KEY : undefined;

const api = axios.create({
  baseURL: "/api",
  timeout: 10000,
  headers: apiKey ? { "X-API-KEY": apiKey } : undefined,
});

export const setAuthToken = (token?: string) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
};

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API error:", {
      message: error?.message,
      url: error?.config?.url,
      method: error?.config?.method,
      status: error?.response?.status,
      data: error?.response?.data,
    });
    return Promise.reject(error);
  }
);

export default api;
