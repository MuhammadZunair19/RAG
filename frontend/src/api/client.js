import axios from "axios";

const client = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default client;

export const auth = {
  login: (email, password) => client.post("/auth/login", { email, password }),
  register: (data) => client.post("/auth/register", data),
  me: () => client.get("/auth/me"),
};

export const chat = {
  send: (question) => client.post("/chat/", { question }),
  history: (limit = 50) => client.get("/chat/history", { params: { limit } }),
};

export const documents = {
  list: () => client.get("/documents/"),
  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return client.post("/documents/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};
