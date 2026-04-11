const API_URL = "http://127.0.0.1:5000/chat";

function appendMessage(text, className) {
    const chatBox = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.className = className;
    msg.innerText = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById("message-input");
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, "user-msg");
    input.value = "";

    fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => {
    const reply = data.reply || "No reply";
    appendMessage(reply, "ai-msg");
    speak(reply); // 🔊 AI speaks here
})
    .catch(err => appendMessage("Error: " + err, "ai-msg"));
}

function retryMessage() {
    fetch("http://127.0.0.1:5000/retry", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            // remove last AI message
            const chatBox = document.getElementById("chat-box");
            const messages = chatBox.querySelectorAll("div.ai-msg");
            if (messages.length) chatBox.removeChild(messages[messages.length - 1]);
            appendMessage(data.reply || "No reply", "ai-msg");
        });
}

function undoMessage() {
    fetch("http://127.0.0.1:5000/undo", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.status === "ok") {
                const chatBox = document.getElementById("chat-box");
                const messages = chatBox.querySelectorAll("div");
                if (messages.length >= 2) {
                    chatBox.removeChild(messages[messages.length - 1]);
                    chatBox.removeChild(messages[messages.length - 1]);
                }
            }
        });
}

function clearChat() {
    fetch("http://127.0.0.1:5000/clear", { method: "POST" })
        .then(() => {
            document.getElementById("chat-box").innerHTML = "";
        });
}

function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

    recognition.lang = "en-US";

    recognition.onresult = function(event) {
        const speechText = event.results[0][0].transcript;
        document.getElementById("message-input").value = speechText;
        sendMessage(); // auto send
    };

    recognition.start();
}
function speak(text) {
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    window.speechSynthesis.speak(speech);
}
function speak(text) {
    window.speechSynthesis.cancel(); // stop previous speech
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    window.speechSynthesis.speak(speech);
}
