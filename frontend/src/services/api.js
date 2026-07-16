import axios from "axios";

// Configurable so the frontend isn't hardcoded to one API deployment.
// Falls back to the current API Gateway URL if the env var isn't set.
const BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://9bgtdei3ob.execute-api.ap-south-1.amazonaws.com/Prod";

export const api = axios.create({
  baseURL: BASE_URL,
});

api.interceptors.request.use((config) => {

  const email = localStorage.getItem("customerEmail");

  if (email) {
    config.headers["x-customer-email"] = email;
  }

  return config;

});