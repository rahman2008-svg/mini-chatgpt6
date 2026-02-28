btn.onclick = async () => {
    const message = input.value.trim();
    if (!message) return;
    chatBox.innerHTML += `<div class="message user">You: ${message}</div>`;
    input.value = "";

    try {
        const form = new FormData();
        form.append("message", message);
        form.append("session_id", session_id);

        const res = await fetch("/chat", {
            method: "POST",
            body: form
        });

        if (!res.ok) {
            chatBox.innerHTML += `<div class="message bot">Error: ${res.statusText}</div>`;
            return;
        }

        const data = await res.json();
        session_id = data.session_id;
        chatBox.innerHTML += `<div class="message bot">Bot: ${data.reply}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        chatBox.innerHTML += `<div class="message bot">Error: ${err}</div>`;
    }
};
