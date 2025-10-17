import React, { useState } from "react";
import AgenticBotModal from "./AgenticBotModal";
import "./ChatbotWidget.css";

const ChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <>
      <div
        className="chatbot-widget"
        aria-label="Open agentic chatbot"
        title="Open agentic chatbot"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => setIsOpen(true)}
      >
        <div className="bot-icon">🤖</div>
      </div>
      {showTooltip && (
        <div className="bot-tooltip">Feeling lazy? Use me! 🤖</div>
      )}
      {isOpen && <AgenticBotModal close={() => setIsOpen(false)} />}
    </>
  );
};

export default ChatbotWidget;
