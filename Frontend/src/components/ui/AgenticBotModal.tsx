import React, { useState, useRef, useEffect } from "react";
import { Mic, Send, X, Sparkles, Bot, Loader2, CheckCircle, AlertCircle, Lightbulb, Zap } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "./button";
import { Textarea } from "./textarea";
import { Card } from "./card";
import { Badge } from "./badge";
import { useToast } from "@/hooks/use-toast";
import "./AgenticBotModal.css";

interface AgenticBotModalProps {
  close: () => void;
  onSearchResults?: (results: any) => void;
  onAgenticResult?: (result: any) => void;
}

const AgenticBotModal: React.FC<AgenticBotModalProps> = ({ close, onSearchResults, onAgenticResult }) => {
  const [command, setCommand] = useState("");
  const [result, setResult] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [streamingResponse, setStreamingResponse] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const recognitionRef = useRef<any>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  // Command suggestions
  const suggestions = [
    { text: "Search for Article 370", icon: "🔍", category: "Search" },
    { text: "Sign up with random details", icon: "👤", category: "Auth" },
    { text: "Change theme to dark", icon: "🌙", category: "Settings" },
    { text: "Open profile and update bio", icon: "📝", category: "Profile" },
    { text: "Show my query history", icon: "📊", category: "History" },
    { text: "Help me with available commands", icon: "❓", category: "Help" },
  ];

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
      setIsListening(false);
      return;
    }
    if (!recognitionRef.current) {
      toast({
        title: "Voice Not Supported",
        description: "Please use Chrome, Edge, or Safari for voice input.",
        variant: "destructive",
      });
      return;
    }
    setIsListening(true);
    recognitionRef.current.start();
    toast({
      title: "🎤 Listening...",
      description: "Speak your command clearly",
    });
  };

  const handleSuggestionClick = (suggestion: string) => {
    setCommand(suggestion);
    setShowSuggestions(false);
  };

  const handleCommandChange = (value: string) => {
    setCommand(value);
    setShowSuggestions(value.length > 0);
  };

  const handleSubmit = async () => {
    if (!command.trim()) return;
    setIsProcessing(true);
    setResult(null);
    try {
      const response = await fetch("http://localhost:5000/api/agentic-command", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("token")}`,  // send JWT if present
        },
        body: JSON.stringify({ command })
      });

      const data = await response.json();
      setResult(data);

      // Process all results and handle different types of actions
      let hasSearchResults = false;
      let searchQuery = "";
      let searchResponses = {};
      let hasNavigation = false;
      let hasProfileUpdate = false;
      let hasSettingsUpdate = false;
      let hasThemeChange = false;
      let hasHelp = false;
      let hasError = false;
      let errorMessage = "";

      // The new backend returns multiple steps in an array at data.results
      // Loop through them and apply relevant actions
      if (Array.isArray(data.results)) {
        data.results.forEach(result => {
          // Handle authentication
          if (
            (result.tool === "login" || result.tool === "signup" || result.tool === "signup_with_random") &&
            result.success && result.result?.token
          ) {
            localStorage.setItem("token", result.result.token);
            localStorage.setItem("userEmail", result.result.user_email);
            // Always route to dashboard after login or signup!
            setTimeout(() => {
              navigate("/dashboard");
              close();
            }, 1500);
          }

          // Handle search results
          if (result.tool === "search" && result.success && result.result?.results) {
            hasSearchResults = true;
            searchQuery = result.result.query || command;
            searchResponses = result.result.results;
          }

          // Handle navigation
          if (result.result?.navigate) {
            hasNavigation = true;
            setTimeout(() => {
              navigate(`/${result.result.navigate}`);
              close();
            }, 1500);
          }

          // Handle profile updates
          if (result.tool === "update_profile" || result.tool === "update_profile_field") {
            hasProfileUpdate = true;
          }

          // Handle settings updates
          if (result.tool === "update_setting" || result.tool === "update_notification_setting") {
            hasSettingsUpdate = true;
          }

          // Handle theme changes
          if (result.tool === "update_theme") {
            hasThemeChange = true;
          }

          // Handle help
          if (result.tool === "help") {
            hasHelp = true;
          }

          // Handle errors
          if (!result.success && result.error) {
            hasError = true;
            errorMessage = result.error;
          }
        });
      }

      // Handle different result types
      if (hasSearchResults && onSearchResults) {
        onSearchResults({
          query: searchQuery,
          responses: searchResponses
        });
        close();
        return;
      }

      if (hasNavigation) {
        // Navigation is handled above with setTimeout
        return;
      }

      if (hasProfileUpdate || hasSettingsUpdate || hasThemeChange || hasHelp) {
        // Pass result to context for handling
        if (onAgenticResult) {
          onAgenticResult({
            type: hasProfileUpdate ? 'profile_update' :
              hasSettingsUpdate ? 'settings_update' :
                hasThemeChange ? 'theme_change' : 'help',
            data: data,
            message: data.results?.[0]?.result?.message || "Action completed successfully"
          });
        }
        close();
        return;
      }

      if (hasError) {
        if (onAgenticResult) {
          onAgenticResult({
            type: 'error',
            data: data,
            message: errorMessage
          });
        }
        close();
        return;
      }
    } catch (error) {
      alert("Failed to execute command.");
    } finally {
      setIsProcessing(false);
    }
  };


  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={close}>
      <div 
        className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden animate-in fade-in-0 zoom-in-95 duration-300"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-amber-500 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <Bot className="w-7 h-7" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">AI Assistant</h2>
                <p className="text-blue-100 text-sm">Powered by LawGPT Agentic System</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={close}
              className="text-white hover:bg-white/20 rounded-xl"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Command Input */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Sparkles className="w-4 h-4 text-amber-500" />
              <span>What would you like me to help you with?</span>
            </div>
            
            <div className="relative">
              <Textarea
                placeholder="Try: 'Search for Article 370' or 'Sign up and change theme to dark'..."
                value={command}
                onChange={(e) => handleCommandChange(e.target.value)}
                className="min-h-24 text-base resize-none pr-20"
                onFocus={() => setShowSuggestions(true)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
                disabled={isProcessing}
              />
              
              {/* Action Buttons */}
              <div className="absolute bottom-3 right-3 flex gap-2">
                <Button
                  size="sm"
                  variant={isListening ? "destructive" : "outline"}
                  onClick={toggleVoice}
                  disabled={isProcessing}
                  className={`rounded-lg ${isListening ? "animate-pulse" : ""}`}
                >
                  <Mic className="w-4 h-4" />
                </Button>
                <Button
                  size="sm"
                  onClick={handleSubmit}
                  disabled={isProcessing || !command.trim()}
                  className="rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  {isProcessing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>

            {/* Command Suggestions */}
            {showSuggestions && (
              <Card className="p-4 border-dashed border-2 border-gray-200">
                <div className="flex items-center gap-2 mb-3">
                  <Lightbulb className="w-4 h-4 text-amber-500" />
                  <span className="text-sm font-medium text-gray-700">Try these commands:</span>
                </div>
                <div className="grid grid-cols-1 gap-2">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion.text)}
                      className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 text-left transition-colors group"
                    >
                      <span className="text-lg">{suggestion.icon}</span>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 group-hover:text-blue-600">
                          {suggestion.text}
                        </div>
                        <Badge variant="secondary" className="text-xs">
                          {suggestion.category}
                        </Badge>
                      </div>
                    </button>
                  ))}
                </div>
              </Card>
            )}
          </div>

          {/* Status Indicators */}
          {isListening && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-red-700">Listening... Speak your command</span>
            </div>
          )}

          {isProcessing && (
            <div className="flex items-center gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
              <div>
                <div className="text-sm font-medium text-blue-900">Processing your command...</div>
                <div className="text-xs text-blue-600">This may take a few moments</div>
              </div>
            </div>
          )}

          {/* Streaming Response */}
          {isStreaming && streamingResponse && (
            <Card className="p-4 bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
              <div className="flex items-start gap-3">
                <Zap className="w-5 h-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-green-900 mb-2">Response:</div>
                  <div className="text-sm text-gray-700 whitespace-pre-wrap">
                    {streamingResponse}
                    <span className="inline-block w-2 h-4 bg-green-500 animate-pulse ml-1"></span>
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* Results */}
          {result && !isStreaming && (
            <Card className="p-4 bg-gray-50 border-gray-200">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900 mb-2">Command executed successfully!</div>
                  <div className="text-xs text-gray-600 bg-white p-3 rounded border overflow-auto max-h-40">
                    <pre className="whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* Quick Tips */}
          <div className="bg-gradient-to-r from-amber-50 to-orange-50 p-4 rounded-lg border border-amber-200">
            <div className="flex items-start gap-3">
              <Lightbulb className="w-5 h-5 text-amber-600 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-amber-900 mb-2">💡 Pro Tips:</div>
                <ul className="text-xs text-amber-800 space-y-1">
                  <li>• Use natural language: "Search for Article 370"</li>
                  <li>• Chain commands: "Sign up and search for consumer rights"</li>
                  <li>• Voice commands work with the microphone button</li>
                  <li>• Try the suggestions above for quick start</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgenticBotModal;
