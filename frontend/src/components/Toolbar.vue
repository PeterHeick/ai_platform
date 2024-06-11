<template>
  <div class="toolbar">
    <div class="button-group">
      <button @click="activeView = 'gdpr'">GDPR</button>
      <button @click="activeView = 'hvidvask'">Hvidvask</button>
      <button @click="activeView = 'otherApp'">Anden App</button>
    </div>
  </div>
  <component :is="activeView" /> 
</template>

<script>
import Gdpr from './Gdpr.vue';
import Hvidvask from './Hvidvask.vue';
import OtherApp from './OtherApp.vue';

export default {
  components: { Gdpr, Hvidvask, OtherApp },
  data() {
    return {
      activeView: 'gdpr' // Start med GDPR som standard
    };
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
