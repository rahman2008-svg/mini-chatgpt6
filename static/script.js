const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
let session_id = "";

sendBtn.addEventListener("click", async () => {
  const message = userInput.value;
  if (!message) return;

  chatBox.innerHTML += `<div class="user-msg">${message}</div>`;

  const formData = new FormData();
  formData.append("message", message);
  formData.append("session_id", session_id);

  const res = await fetch("/chat", {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  session_id = data.session_id;

  chatBox.innerHTML += `<div class="bot-msg">${data.reply}</div>`;
  chatBox.scrollTop = chatBox.scrollHeight;
  userInput.value = "";
});
