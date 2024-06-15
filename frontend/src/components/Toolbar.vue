<template>
  <div class="toolbar">
    <div class="button-group">
      <button @click="setActiveView('gdpr')">GDPR</button>
      <button @click="setActiveView('hvidvask')">Hvidvask</button>
      <button @click="setActiveView('otherApp')">Anden App</button>
    </div>
  </div>
  <component :is="activeView.component" :botType="activeView.botType" />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Chatbot from './Chatbot.vue';
import OtherApp from './OtherApp.vue';

const activeView = ref({
  component: Chatbot,
  botType: 'gdpr' // Start med GDPR som standard
});

const setActiveView = (botType) => {
  if (botType === 'otherApp') {
    activeView.value = { component: OtherApp, botType: null };
  } else {
    activeView.value = { component: Chatbot, botType: botType };
  }
};
</script>

<style scoped>
.toolbar {
  width: 100%;
  background-color: #ffffff;
  padding: 10px 20px;
  font-size: small;
  box-sizing: border-box;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-start;
  align-items: center;
  border-bottom: 1px solid #e1e1e1;
}

.button-group {
  display: flex;
  gap: 10px;
}

.toolbar button {
  padding: 10px 20px;
  margin: 0;
  background-color: #f3f3f3;
  color: #333;
  border: 1px solid #dcdcdc;
  border-radius: 2px;
  cursor: pointer;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  font-size: 14px;
}

.toolbar button:hover {
  background-color: #e1e1e1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
