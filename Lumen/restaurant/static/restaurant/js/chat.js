document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chat-box');
    if (!chatBox) return;

    chatBox.scrollTop = chatBox.scrollHeight;

    const pollUrl = chatBox.dataset.pollUrl;
    if (!pollUrl) return; 

    setInterval(() => {
        fetch(pollUrl)
            .then(res => res.json())
            .then(data => {
                chatBox.innerHTML = '';
                data.messages.forEach(m => {
                    const div = document.createElement('div');
                    div.className = 'mb-2';
                    div.innerHTML = `<span class="badge bg-secondary">${m.sender__username}</span><div>${m.text}</div>`;
                    chatBox.appendChild(div);
                });
                chatBox.scrollTop = chatBox.scrollHeight;
            });
    }, 5000);
});