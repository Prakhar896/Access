import axios from "axios";

const instance = axios.create({
    baseURL: import.meta.env.VITE_BACKEND_URL,
})

instance.interceptors.request.use((config) => {
    config.headers["APIKey"] = import.meta.env.VITE_BACKEND_API_KEY
    if (config.method == "post") {
        config.headers["Content-Type"] = "application/json"
    }

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