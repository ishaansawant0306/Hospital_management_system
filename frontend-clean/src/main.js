import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import '@fortawesome/fontawesome-free/css/all.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import axios from 'axios';
axios.defaults.baseURL = 'http://localhost:5000';



createApp(App).use(router).mount('#app')

