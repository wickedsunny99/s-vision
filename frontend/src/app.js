// Voice input
const startListening = () => {
  const recognition = new window.webkitSpeechRecognition();
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    socket.emit("voice-command", transcript);
  };
  recognition.start();
};
