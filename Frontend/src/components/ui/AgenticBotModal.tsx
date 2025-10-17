import React, { useState, useRef, useEffect } from "react";
import { Mic, Send, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "./AgenticBotModal.css";

interface AgenticBotModalProps {
  close: () => void;
}

const AgenticBotModal: React.FC<AgenticBotModalProps> = ({ close }) => {
  const [command, setCommand] = useState("");
  const [result, setResult] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.lang = "en-IN";
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setCommand(transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = () => {
        setIsListening(false);
        alert("Could not capture voice");
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const toggleVoice = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      return;
    }
    if (!recognitionRef.current) {
      alert("Voice Not Supported. Please use Chrome, Edge, or Safari.");
      return;
    }
    setIsListening(true);
    recognitionRef.current.start();
  };

  const handleSubmit = async () => {
    if (!command.trim()) return;
    setIsProcessing(true);
    setResult(null);
    try {
      const response = await fetch("http://localhost:5000/api/agentic-command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command }),
      });
      const data = await response.json();
      setResult(data);

      if (data.login?.success) {
        localStorage.setItem("token", data.login.token);
        localStorage.setItem("userEmail", command.match(/email\s*=\s*([\w@.+-]+)/i)?.[1] || "");
        setTimeout(() => {
          navigate("/dashboard");
          close();
        }, 1500);
      }
    } catch (error) {
      alert("Failed to execute command.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="agentic-modal-backdrop" onClick={close}>
      <div className="agentic-modal-window" onClick={e => e.stopPropagation()}>
        <div className="agentic-modal-header">
          <h2 className="agentic-modal-title">🤖 Agentic Command</h2>
          <button
            onClick={close}
            aria-label="Close chat modal"
            title="Close"
            className="agentic-modal-close"
          >
            <X size={24} />
          </button>
        </div>
        <p className="agentic-modal-instructions">
          Try: <span className="agentic-modal-example">login email=your@email.com password=yourpass and search for article 370</span>
        </p>
        <div className="agentic-modal-entry-row">
          <input
            type="text"
            className="agentic-modal-input"
            placeholder="Type or speak your command..."
            value={command}
            onChange={e => setCommand(e.target.value)}
            autoFocus
            onKeyDown={e => e.key === "Enter" && handleSubmit()}
          />
          <button
            onClick={toggleVoice}
            aria-label="Use voice command"
            title="Voice"
            className={`agentic-modal-voice ${isListening ? "voice-listening" : ""}`}
          >
            <Mic size={20} />
          </button>
          <button
            onClick={handleSubmit}
            disabled={isProcessing || !command.trim()}
            aria-label="Send command"
            title="Send"
            className="agentic-modal-send"
          >
            <Send size={20} />
          </button>
        </div>
        {result && (
          <div className="agentic-modal-result">
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
        {isProcessing && (
          <div className="agentic-modal-loader"><span className="loader-spinner">⏳</span></div>
        )}
      </div>
    </div>
  );
};

export default AgenticBotModal;
