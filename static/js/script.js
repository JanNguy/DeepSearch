document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const baseUrlInput = document.getElementById('baseUrlInput');
    const sendBtn = document.getElementById('sendBtn');
    const messagesContainer = document.getElementById('messagesContainer');

    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        sendBtn.disabled = !this.value.trim();
    });

    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        const base_url = baseUrlInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        userInput.value = '';
        userInput.style.height = 'auto';
        sendBtn.disabled = true;
        scrollToBottom();

        addMessage("...", 'bot');
        scrollToBottom();

        const botDiv = messagesContainer.querySelector('.bot-message:last-child .message-text');
        botDiv.textContent = "[Traitement en cours…]";

        try {
            const responseText = await getRealResponse(message, base_url);
            botDiv.textContent = responseText;
            scrollToBottom();
        } catch (err) {
            botDiv.textContent = "Erreur technique : " + err;
        }
    });

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');

        const avatar = document.createElement('span');
        avatar.style.marginRight = "7px";
        avatar.innerHTML = sender === 'user' ? "🧑" : "🤖";

        const msg = document.createElement('span');
        msg.className = "message-text";
        msg.textContent = text;

        div.appendChild(avatar);
        div.appendChild(msg);

        messagesContainer.appendChild(div);
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async function getRealResponse(userMessage, base_url) {
        try {
            // 1. /api/search
            let searchRes = await fetch('/api/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ base_url, query: userMessage })
            });
            let searchJson = await searchRes.json();
            if (!searchRes.ok) throw (searchJson.error || "Erreur sur /api/search");

            // 2. /api/analyze
            let analyzeRes = await fetch('/api/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ query: userMessage })
            });
            let analyzeJson = await analyzeRes.json();
            if (!analyzeRes.ok) throw (analyzeJson.error || "Erreur sur /api/analyze");

            return analyzeJson.response;
        } catch (err) {
            return "Erreur réseau ou serveur : " + err;
        }
    }
});
