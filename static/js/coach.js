async function sendCoachMsg() {
    const input = document.getElementById('coachInput');
    const win = document.getElementById('chatWindow');
    const msg = input.value.trim();
    if (!msg) return;
    const userBox = document.createElement('div');
    userBox.className = 'msg user';
    userBox.textContent = 'You: ' + msg;
    win.appendChild(userBox);
    input.value = '';
    const loading = document.createElement('div');
    loading.className = 'msg assistant';
    loading.textContent = 'HeartAI is thinking...';
    win.appendChild(loading);
    win.scrollTop = win.scrollHeight;
    try {
        const res = await fetch('/api/coach', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:msg})});
        const data = await res.json();
        loading.textContent = data.reply || 'No response received.';
        if (!data.ok) loading.style.color = '#c0392b';
    } catch (e) {
        loading.textContent = 'Unable to connect to AI coach. Check the Flask server and Gemini API key.';
        loading.style.color = '#c0392b';
    }
    win.scrollTop = win.scrollHeight;
}
