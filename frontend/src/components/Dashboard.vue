<template>
  <Toolbar></Toolbar>
  <div class="dashboard-container">
    <!-- Indhold her -->
  </div>
</template>

<script setup lang="ts">
import Toolbar from "./Toolbar.vue";

</script>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}

.dashboard-container {
  display: flex;
  width: 100%;
  min-height: 100vh;
  box-sizing: border-box;
  background-color: #fafafa; /* Tilføj en lys baggrund */
}

.header {
  position: fixed; 
  top: 0;
  left: 0;
  width: 100%;
  height: 20px;
  background-color: #ffffff;
}

.content {
  padding: 20px;
}
</style>
