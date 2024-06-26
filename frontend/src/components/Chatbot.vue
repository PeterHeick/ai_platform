<template>
  <h1>GDPR regler</h1>
  <div class="flex mt-6 gap-4">
    <div class="flex-1 border p-4 rounded">
      <div ref="messagesContainer" class="overflow-y-auto h-64">
        <div v-for="(message, index) in messages" :key="index" class="mb-2">
          <div :class="{ 'user-message': message.user === 'User', 'bot-message': message.user === 'Bot' }">
            <strong>{{ message.user }}:</strong> <span v-html="formatMessage(message.text)"></span>
          </div>
        </div>
      </div>
      <textarea v-model="newMessage" placeholder="Stil et spørgsmål..."
        class="w-full px-3 py-2 border rounded mt-2"></textarea>
      <button @click="sendMessage" class="mt-2 px-4 py-2 bg-blue-500 text-white rounded">Send</button>
    </div>
    <div class="documents-container border p-4 rounded">
      <h2 class="text-xl mb-4">Relevante Dokumenter</h2>
      <ul class="document-list">
        <li v-for="(source, index) in docSources" :key="index">
          <a :href="'http://127.0.0.1:8000/get_pdf/' +  encodeURIComponent(source)" target="_blank" class="text-blue-500 document-link">{{ source }}</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, onMounted, nextTick } from 'vue';
import axios from 'axios';

const props = defineProps({
  botType: String
});

const title = ref('');
const newMessage = ref('');
const messages = ref<{ user: string; text: string }[]>([]);
const docSources = ref<string[]>([]); // Tilføjet til at holde unikke kilder
const messagesContainer = ref<HTMLElement | null>(null);
let url = 'http://127.0.0.1:8000/query';

watch(() => props.botType, (newBotType) => {
  if (newBotType === 'gdpr') {
    title.value = 'GDPR regler';
  } else if (newBotType === 'hvidvask') {
    title.value = 'Hvidvask regler';
  }
});

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (newMessage.value.trim()) {
    messages.value.push({ user: 'User', text: newMessage.value });

    try {
      const response = await axios.post(`http://127.0.0.1:8000/query?type=${props.botType}`, {
        query: newMessage.value
      });


      const botResponse = response.data; // Antag at svaret er i data-feltet
      messages.value.push({ user: 'Bot', text: botResponse.answer });
      docSources.value = botResponse.docsource; // Gem dokumentkilderne
      console.log(botResponse);
      console.log(docSources.value);

      await nextTick();
      scrollToBottom();
    } catch (error) {
      console.error('Error sending message:', error);
    }

    newMessage.value = '';
  }
};

const formatMessage = (message: string) => {
  return message.replace(/\n/g, '<br />');
};

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
h1 {
  font-size: 1.5rem;
  font-weight: 500;
  padding: 20px;
}

.flex {
  display: flex;
}

.mt-6 {
  margin-top: 1.5rem;
}

.gap-4 {
  gap: 1rem;
}

.border {
  border: 1px solid #dcdcdc;
}

.p-4 {
  padding: 1rem;
}

.rounded {
  border-radius: 0.25rem;
}

.overflow-y-auto {
  overflow-y: auto;
}

.h-64 {
  height: 16rem;
}

.w-full {
  width: 100%;
}

.px-3 {
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.bg-blue-500 {
  background-color: #007bff;
}

.text-white {
  color: white;
}

.text-xl {
  font-size: 1.25rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.text-blue-500 {
  color: #007bff;
}

.user-message,
.bot-message {
  text-align: left; /* Juster tekst til venstre */
  white-space: pre-wrap;
}

.user-message {
  background-color: #e1f5fe;
  padding: 10px;
  border-radius: 5px;
}

.bot-message {
  background-color: #e8f5e9;
  padding: 10px;
  border-radius: 5px;
}

.flex-1 {
  flex: 1;
}

.documents-container {
  flex-basis: 40%; /* Øg bredden af dokumentcontaineren */
}

.document-list {
  list-style-type: none;
  padding: 0;
}

.document-list li {
  margin-bottom: 10px;
  white-space: nowrap; /* Sørg for, at teksten ikke ombrydes */
  overflow: hidden;
  text-overflow: ellipsis; /* Tilføj ellipsis for lange tekster */
}

.document-link {
  text-decoration: none;
  text-align: left; /* Juster tekst til venstre */
  display: block; /* Sikrer, at linket fylder hele bredden af li-elementet */
}
</style>
