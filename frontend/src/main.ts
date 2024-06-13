import { createApp } from 'vue'
import './style.css'
import './main.css';
import App from './App.vue'
import router from './router';

console.log('Hello from main.ts');
createApp(App).use(router).mount('#app');