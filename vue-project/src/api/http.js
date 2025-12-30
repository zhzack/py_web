import axios from "axios";

const http = axios.create({
    baseURL: "/api", // 关键：走 Vite proxy
    timeout: 10000,
});

export default http;
