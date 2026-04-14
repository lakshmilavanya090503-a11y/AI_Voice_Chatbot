const BASE_URL = "https://ai-voice-chatbot-zu75.onrender.com";

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

    fetch(`${BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => {
        appendMessage(data.reply, "ai-msg");
        speak(data.reply); 
    })
    .catch(err => console.log(err));
}

function retryMessage() {
    fetch(`${BASE_URL}/retry`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
            const chatBox = document.getElementById("chat-box");
            const messages = chatBox.querySelectorAll("div.ai-msg");

            if (messages.length) {
                chatBox.removeChild(messages[messages.length - 1]);
            }

            appendMessage(data.reply || "No reply", "ai-msg");
            speak(data.reply || "");
        })
        .catch(err => console.log(err));
}

function undoMessage() {
    fetch(`${BASE_URL}/undo`, { method: "POST" })
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
        })
        .catch(err => console.log(err));
}

function clearChat() {
    fetch(`${BASE_URL}/clear`, { method: "POST" })
        .then(() => {
            document.getElementById("chat-box").innerHTML = "";
        })
        .catch(err => console.log(err));
}

function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";

    recognition.onresult = function(event) {
        const speechText = event.results[0][0].transcript;
        document.getElementById("message-input").value = speechText;
        sendMessage();
    };

    recognition.start();
}

function speak(text) {
    if (!text) return;

    if (!window.speechSynthesis) {
        alert("Speech not supported in this browser");
        return;
    }

    window.speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    speech.rate = 1;
    speech.pitch = 1;
    speech.volume = 1;

    function setVoiceAndSpeak() {
        const voices = window.speechSynthesis.getVoices();

        
        const selectedVoice =
            voices.find(v => v.name.includes("Google US English")) || // Chrome female
            voices.find(v => v.name.includes("Microsoft Zira")) ||    // Windows female
            voices.find(v => v.name.includes("Female")) ||            // fallback female
            voices[0]; // final fallback

        speech.voice = selectedVoice;
        window.speechSynthesis.speak(speech);
    }

    let voices = window.speechSynthesis.getVoices();

    if (voices.length === 0) {
        window.speechSynthesis.onvoiceschanged = setVoiceAndSpeak;
    } else {
        setVoiceAndSpeak();
    }
}

function stopSpeaking() {
    window.speechSynthesis.cancel();
}

const PROJECT_URL = "https://ai-voice-chatbot-zu75.onrender.com";

function shareWhatsApp() {
    const text = `Check out my project 🚀: ${PROJECT_URL}`;
    const url = `https://wa.me/?text=${encodeURIComponent(text)}`;
    window.open(url, "_blank");
}

function shareLinkedIn() {
    const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(PROJECT_URL)}`;
    window.open(url, "_blank");
}

function shareInstagram() {
    navigator.clipboard.writeText(PROJECT_URL);
    alert("Link copied! Now paste it on Instagram 🔥");
}
