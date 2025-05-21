const chatBtn = document.createElement("div");
chatBtn.id = "chat-button";
chatBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none"
    stroke="currentColor" stroke-width="2" stroke-linecap="round"
    stroke-linejoin="round" class="lucide lucide-message-circle"
    viewBox="0 0 24 24">
    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8
      8.5 8.5 0 0 1-7.6 4.7
      8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7
      a8.38 8.38 0 0 1-.9-3.8
      8.5 8.5 0 0 1 4.7-7.6
      8.38 8.38 0 0 1 3.8-.9h.5
      a8.48 8.48 0 0 1 8 8v.5z"/>
  </svg>
`;
document.body.appendChild(chatBtn);


const chatPanel = document.createElement("div");
chatPanel.id = "chat-panel";
chatPanel.innerHTML = `
  <div id="chat-header">ChatBot</div>
  <div id="chat-messages">
    <div class="message incoming">Hello! How can I assist you?</div>
  </div>
  <div id="chat-input-area">
    <input type="text" id="chat-input" placeholder="Type a message..." />
    <button id="send-btn">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
        fill="none" stroke="currentColor" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"
        class="lucide lucide-send" viewBox="0 0 24 24">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
      </svg>
    </button>
  </div>`;


document.body.appendChild(chatPanel);


chatBtn.addEventListener("click", () => {
  chatPanel.classList.toggle("visible");
});

async function sendMessage(){
    const input = document.getElementById("chat-input");
    const text = input.value.trim()
    if (!text) return;
    
   

    const msgArea = document.getElementById("chat-messages");
    const msg = document.createElement("div");
    msg.className = "message outgoing";
    msg.textContent = text;
    msgArea.appendChild(msg);
    msgArea.scrollTop = msgArea.scrollHeight;
    input.value = "";

    try{
      const response = await fetch('http://localhost:5000/ask',{
        method :"POST",
        headers : {
           "Content-Type": "application/json"},
        body : JSON.stringify({ question:text })
      });
      const result = await response.json();
      const botmsg = document.createElement('div');
      botmsg.className = "message incoming";
      botmsg.textContent = result.answer || result.error || "Error";
      msgArea.appendChild(botmsg);
      msgArea.scrollTop = msgArea.scrollHeight;
    
    }catch(err){
      const errMsg = document.createElement('div');
      errMsg.className = "message incoming"
      errMsg.textContent = "Failed to get response.";
      msgArea.appendChild(errMsg);
    }

}

document.getElementById("send-btn").addEventListener('click', sendMessage);
document.getElementById('chat-input').addEventListener('keypress',e => {
  // console.log("alsdhfjhadfhjsad",e);  
  if (e.key === "Enter") sendMessage();
})

