import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

import PrimeVue from 'primevue/config';
import 'primeicons/primeicons.css'
const app = createApp(App);
app.use(PrimeVue);

import GlobalDataPlugin from '../scripts/DataController';
app.use(GlobalDataPlugin)

app.mount('#app')
