import React, { useState, useEffect } from "react";
import AgenticBotModal from "./AgenticBotModal";
import { Bot, Sparkles, Zap, MessageCircle } from "lucide-react";

interface ChatbotWidgetProps {
  onSearchResults?: (results: any) => void;
  onAgenticResult?: (result: any) => void;
}

const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({ onSearchResults, onAgenticResult }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const [isPulsing, setIsPulsing] = useState(false);

  // Add pulsing animation on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsPulsing(true);
      setTimeout(() => setIsPulsing(false), 2000);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      {/* Floating Action Button */}
      <div className="fixed bottom-6 right-6 z-40">
        {/* Tooltip */}
        {showTooltip && (
          <div className="absolute bottom-full right-0 mb-4 mr-2 animate-in fade-in-0 slide-in-from-bottom-2 duration-200">
            <div className="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-medium shadow-lg relative">
              <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span>AI Assistant</span>
              </div>
              <div className="text-xs text-gray-300 mt-1">Try: "Search for Article 370"</div>
            </div>
          </div>
        )}

        {/* Main Button */}
        <button
          onClick={() => setIsOpen(true)}
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          className={`
            group relative w-16 h-16 bg-gradient-to-br from-blue-600 via-purple-600 to-amber-500 
            rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 
            hover:scale-110 active:scale-95 flex items-center justify-center
            ${isPulsing ? 'animate-pulse' : ''}
          `}
          aria-label="Open AI Assistant"
        >
          {/* Animated Background Ring */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-blue-600 via-purple-600 to-amber-500 animate-ping opacity-20"></div>
          
          {/* Icon Container */}
          <div className="relative z-10 flex items-center justify-center">
            <Bot className="w-8 h-8 text-white group-hover:scale-110 transition-transform duration-200" />
          </div>

          {/* Notification Badge */}
          <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center animate-bounce">
            <span className="text-xs text-white font-bold">AI</span>
          </div>

          {/* Hover Effect */}
          <div className="absolute inset-0 rounded-full bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-200"></div>
        </button>

        {/* Floating Particles Effect */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-2 left-2 w-1 h-1 bg-amber-400 rounded-full animate-ping delay-100"></div>
          <div className="absolute top-4 right-3 w-1 h-1 bg-blue-400 rounded-full animate-ping delay-200"></div>
          <div className="absolute bottom-3 left-3 w-1 h-1 bg-purple-400 rounded-full animate-ping delay-300"></div>
        </div>
      </div>

      {/* Modal */}
      {isOpen && (
        <AgenticBotModal 
          close={() => setIsOpen(false)} 
          onSearchResults={onSearchResults} 
          onAgenticResult={onAgenticResult} 
        />
      )}
    </>
  );
};

export default ChatbotWidget;
