<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded shadow-md w-96">
      <h2 class="text-2xl mb-6 text-center">Log ind</h2>
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label for="username" class="block text-gray-700">Brugernavn</label>
          <input type="text" id="username" v-model="username" class="w-full px-3 py-2 border rounded" required />
        </div>
        <div class="mb-6">
          <label for="password" class="block text-gray-700">Kodeord</label>
          <input type="password" id="password" v-model="password" class="w-full px-3 py-2 border rounded" required />
        </div>
        <button type="submit" class="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600">Log ind</button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const username = ref('');
const password = ref('');
const router = useRouter();

axios.defaults.withCredentials = true;
const handleLogin = async () => {
  try {
    const response = await axios.post('http://localhost:5000/login', {
      username: username.value,
      password: password.value,
    });
    
    if (response.status === 200) {
      // Login successful, redirect to dashboard
      router.push('/dashboard');
    } else {
      alert('Forkert brugernavn eller kodeord');
    }
  } catch (error) {
    alert('Fejl ved login');
    console.error(error);
  }
};
</script>
