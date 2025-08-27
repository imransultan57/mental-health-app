document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const queryInput = document.getElementById("query");
    const chatBox = document.getElementById("chat-box");

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const query = queryInput.value.trim();
        if (!query) return;

        appendMessage("You", query);
        queryInput.value = "";

        fetch(`/chat_api/?query=${encodeURIComponent(query)}`)
            .then((response) => response.json())
            .then((data) => {
                appendMessage("Jarvis", data.response);
            })
            .catch((err) => {
                appendMessage("Jarvis", "⚠️ Something went wrong!");
                console.error(err);
            });
    });

    function appendMessage(sender, message) {
        const p = document.createElement("p");
        p.innerHTML = `<b>${sender}:</b> ${message}`;
        chatBox.appendChild(p);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});

// 🎤 Voice Recognition
let recognition; 
let listening = false; // toggle state

function startListening() {
    if (listening) {
        recognition.stop();
        listening = false;
        console.log("Stopped listening...");
        return;
    }

    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.continuous = true;  // keep listening
    recognition.interimResults = false; // only final results
    recognition.maxAlternatives = 1;

    recognition.onstart = function() {
        listening = true;
        console.log("Listening...");
    };

    recognition.onresult = function(event) {
        const transcript = event.results[event.results.length - 1][0].transcript;
        queryInput.value = transcript;
        form.dispatchEvent(new Event("submit")); // auto-submit
    };

    recognition.onerror = function(event) {
        console.error("Recognition error:", event.error);
        alert("Error: " + event.error);
        listening = false;
    };

    recognition.onend = function() {
        console.log("Recognition ended.");
        listening = false;
    };

    recognition.start();
}
