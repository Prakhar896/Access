import axios from "axios";

const devMode = true;

const instance = axios.create({
    baseURL: devMode ? `${location.protocol}//${location.hostname}:8000`: location.origin,
})

instance.interceptors.request.use((config) => {
    config.headers["APIKey"] = import.meta.env.VITE_BACKEND_API_KEY
    if (config.method == "post") {
        config.headers["Content-Type"] = "application/json"
    }
    config.withCredentials = true;

    return config;
}, (err) => {
    return Promise.reject(err);
})

instance.interceptors.response.use((config) => {
    return config
}, (err) => {
    return Promise.reject(err)
})

export default instance;