import axios from "axios";

const api = axios.create({ baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000" });

export const detectObjects = (formData) =>
  api.post("/api/v1/detect", formData, { headers: { "Content-Type": "multipart/form-data" } });

export const getModelInfo = () => api.get("/api/v1/model-info");
