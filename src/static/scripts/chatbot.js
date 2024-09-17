document.addEventListener('DOMContentLoaded', function () {
  const chatbotMessages = document.getElementById('chatbot-messagesM');
  const sendButton = document.getElementById('send-buttonM');
  const promptInput = document.getElementById('user-inputM');
  const typingIndicator = document.getElementById('typing-indicatorM');

  let sessionId = null;

  function createElementWithOptions(tag, options = {}) {
    const element = document.createElement(tag);
    if (options.classes) element.classList.add(...options.classes);
    if (options.text) element.innerText = options.text;
    if (options.attributes) {
      for (let key in options.attributes) {
        element.setAttribute(key, options.attributes[key]);
      }
    }
    return element;
  }

  function addMyMessage(message) {
    console.log('Adding my message:', message);
    const messageBox = createElementWithOptions('div', { classes: ['user-messageM'] });
    const textMessage = createElementWithOptions('div', { classes: ['text-message-my'], text: message });
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const timeElement = createElementWithOptions('div', { classes: ['time-my'], text: time });

    messageBox.appendChild(textMessage);
    messageBox.appendChild(timeElement);
    chatbotMessages.appendChild(messageBox);
    messageBox.scrollIntoView({ behavior: 'smooth' }); 
}

function addGptMessage(message) {
    console.log('Adding GPT message:', message);
    const messageBox = createElementWithOptions('div', { classes: ['bot-messageM'] });
    const textMessage = createElementWithOptions('div', { classes: ['text-message-gpt'], text: message });
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const timeElement = createElementWithOptions('div', { classes: ['time-gpt'], text: time });

    messageBox.appendChild(textMessage);
    messageBox.appendChild(timeElement);
    chatbotMessages.appendChild(messageBox);
    messageBox.scrollIntoView({ behavior: 'smooth' }); 
}


  function showTypingIndicator(show) {
    typingIndicator.style.display = show ? 'block' : 'none';
  }

  sendButton.addEventListener('click', async function () {
    const cveTitleElement = document.querySelector('.card__title');
    const cveCode = cveTitleElement ? cveTitleElement.textContent.trim() : '';
    const userMessage = promptInput.value;
    
    if (userMessage.trim() === '') return;

    addMyMessage(userMessage);
    promptInput.value = '';

    showTypingIndicator(true);

    try {
      const response = await fetch('/openai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, cve_code: cveCode, session_id: sessionId })
      });

      const data = await response.json();
      showTypingIndicator(false);
      addGptMessage(data.reply.reply);

      if (data.session_id) {
        sessionId = data.session_id;
      } else {
        console.warn('No session_id returned from server');
      }

    } catch (error) {
      showTypingIndicator(false);
      console.error('Error:', error);
      addGptMessage('chatGPT와 연결이 되지 않았습니다.');
    }

  });
});
