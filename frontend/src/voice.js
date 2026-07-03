export class VoiceInterface {
  constructor(socket) {
    this.socket = socket;
    this.recognition = new (window.SpeechRecognition ||
      window.webkitSpeechRecognition)();
    this.recognition.continuous = true;
    this.recognition.interimResults = false;

    this.recognition.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript;
      this.socket.emit("voice-command", transcript);
    };
  }

  start() {
    try {
      this.recognition.start();
    } catch (error) {
      console.error("Speech recognition error:", error);
    }
  }
}
