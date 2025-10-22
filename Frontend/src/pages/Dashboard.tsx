import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Mic,
  Send,
  Copy,
  Volume2,
  Share2,
  History,
  Star,
  Sparkles,
  User,
  Settings,
  LogOut,
  FileText,
  Clock,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useSearch } from "@/contexts/SearchContext";
import lawgptLogo from "@/assets/lawgpt-logo.png";

const Dashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { searchResults, setSearchResults, agenticResult, setAgenticResult } = useSearch();
  const [query, setQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [responses, setResponses] = useState({
    opensource: "",
    lawgpt: "",
    proprietary: "",
  });
  const [queryHistory, setQueryHistory] = useState([]);
  const recognitionRef = useRef(null);

  const [userEmail, setUserEmail] = useState("");
  const userInitial = userEmail ? userEmail[0].toUpperCase() : "U";

  // JWT safety/authentication guard and get user email
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }
    
    // Get user email from localStorage or decode from JWT
    const storedEmail = localStorage.getItem("userEmail");
    if (storedEmail) {
      setUserEmail(storedEmail);
    } else {
      // Fallback: try to get from profile API
      fetch("http://localhost:5000/api/profile", {
        headers: { "Authorization": "Bearer " + token }
      })
      .then(res => {
        if (res.ok) {
          return res.json();
        }
        throw new Error("Failed to fetch profile");
      })
      .then(data => {
        if (data.email) {
          setUserEmail(data.email);
          localStorage.setItem("userEmail", data.email);
        }
      })
      .catch(err => {
        console.error("Failed to load user email:", err);
        // Keep the default empty state
      });
    }
  }, [navigate]);

  // Load persisted query history for the logged-in user
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    const loadHistory = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/queries", {
          headers: {
            "Authorization": "Bearer " + token,
          },
        });
        if (!res.ok) {
          console.error("Failed to load query history:", res.status);
          return;
        }
        const items = await res.json();
        const mapped = (items || []).slice(0, 10).map((it: any) => ({
          text: it.query,
          time: new Date(it.timestamp).toLocaleString(),
        }));
        setQueryHistory(mapped);
      } catch (err) {
        console.error("Error loading query history:", err);
      }
    };
    loadHistory();
  }, []);

  // Handle search results from agentic bot
  useEffect(() => {
    if (searchResults) {
      setQuery(searchResults.query);
      setResponses(searchResults.responses);
      setQueryHistory((prev) => [
        { text: searchResults.query, time: "Just now" },
        ...prev.slice(0, 9),
      ]);
      // Clear the search results after processing
      setSearchResults(null);
      toast({
        title: "✨ Search Complete",
        description: "Results from agentic search displayed",
      });
    }
  }, [searchResults, setSearchResults, toast]);

  // Handle other agentic results
  useEffect(() => {
    if (agenticResult) {
      switch (agenticResult.type) {
        case 'profile_update':
          toast({
            title: "✅ Profile Updated",
            description: agenticResult.message,
          });
          break;
        case 'settings_update':
          toast({
            title: "⚙️ Settings Updated",
            description: agenticResult.message,
          });
          break;
        case 'theme_change':
          toast({
            title: "🎨 Theme Changed",
            description: agenticResult.message,
          });
          break;
        case 'help':
          toast({
            title: "ℹ️ Help",
            description: agenticResult.message,
          });
          break;
        case 'error':
          toast({
            title: "❌ Error",
            description: agenticResult.message,
            variant: "destructive",
          });
          break;
        default:
          toast({
            title: "✅ Action Complete",
            description: agenticResult.message,
          });
      }
      // Clear the result after processing
      setAgenticResult(null);
    }
  }, [agenticResult, setAgenticResult, toast]);

  // Enhanced Voice Recognition Handler
  const toggleVoiceInput = () => {
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      toast({
        title: "Voice Not Supported",
        description: "Please use Chrome, Edge, or Safari for voice input.",
        variant: "destructive",
      });
      return;
    }

    const recognition = new (SpeechRecognition as any)();
    recognition.interimResults = true; // Enable interim results for better UX
    recognition.lang = "en-US"; // Better recognition for English
    recognition.continuous = false;
    recognition.maxAlternatives = 3; // Get multiple alternatives

    recognition.onstart = () => {
      setIsListening(true);
      toast({
        title: "🎤 Listening...",
        description: "Speak your legal question clearly",
      });
    };

    recognition.onresult = (event) => {
      let finalTranscript = "";
      let interimTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      // Show interim results for better UX
      if (interimTranscript) {
        setQuery(interimTranscript);
      }

      if (finalTranscript) {
        setQuery(finalTranscript);
        setIsListening(false);
        toast({
          title: "✅ Voice Captured",
          description: "Your question is ready to submit",
        });
        // Auto-submit after voice capture
        setTimeout(() => {
          handleSubmit();
        }, 500);
      }
    };

    recognition.onerror = (event) => {
      setIsListening(false);
      let errorMessage = "Voice recognition error";
      
      switch (event.error) {
        case "no-speech":
          errorMessage = "No speech detected. Please try again.";
          break;
        case "audio-capture":
          errorMessage = "Microphone not accessible. Please check permissions.";
          break;
        case "not-allowed":
          errorMessage = "Microphone permission denied. Please allow microphone access.";
          break;
        case "network":
          errorMessage = "Network error. Please check your connection.";
          break;
        default:
          errorMessage = `Voice error: ${event.error}`;
      }
      
      toast({
        title: "Voice Error",
        description: errorMessage,
        variant: "destructive",
      });
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  // Submit Query
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsProcessing(true);

    setQueryHistory((prev) => [
      { text: query, time: "Just now" },
      ...prev.slice(0, 9),
    ]);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        toast({
          title: "Error",
          description: "Not logged in. Please login first.",
          variant: "destructive",
        });
        setIsProcessing(false);
        return;
      }
      
      const response = await fetch("http://localhost:5000/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ query })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Query failed");
      }
      
      const data = await response.json();
      setResponses({
        opensource: data.opensource,
        lawgpt: data.lawgpt,
        proprietary: data.proprietary,
      });
      setIsProcessing(false);
      toast({
        title: "✨ Analysis Complete",
        description: "All models have provided their insights",
      });
    } catch (err) {
      setIsProcessing(false);
      console.error("Query submission error:", err);
      toast({
        title: "Error",
        description: err.message || "Failed to get model response.",
        variant: "destructive",
      });
    }
  };


  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied!",
      description: "Response copied to clipboard",
    });
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    toast({
      title: "Logged Out",
      description: "You have been signed out successfully",
    });
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-amber-50">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-white/80 backdrop-blur-md shadow-sm">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-3">
              <img src={lawgptLogo} alt="LawGPT" className="w-10 h-10" />
              <div className="flex flex-col">
                <span className="font-bold text-xl text-slate-900">LawGPT</span>
                <span className="text-xs text-amber-600 font-medium">AI Legal Assistant</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="hidden md:flex items-center gap-2 text-slate-600 hover:text-slate-900"
              >
                <History className="w-4 h-4" />
                <span className="text-sm">History</span>
              </Button>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-600 to-amber-500 text-white font-semibold flex items-center justify-center hover:shadow-lg transition-all">
                    {userInitial}
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <div className="px-3 py-2 border-b">
                    <p className="text-sm font-semibold">{userEmail || "Loading..."}</p>
                    <p className="text-xs text-muted-foreground">Free Plan</p>
                  </div>
                  <DropdownMenuItem className="cursor-pointer" onClick={() => navigate("/profile")}
                  >
                    <User className="w-4 h-4 mr-2" />
                    Profile
                  </DropdownMenuItem>
                  <DropdownMenuItem className="cursor-pointer" onClick={() => navigate("/settings")}>
                    <Settings className="w-4 h-4 mr-2" />
                    Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={handleLogout}
                    className="cursor-pointer text-red-600"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 md:px-6 py-8">
        <div className="grid lg:grid-cols-12 gap-6">
          <aside className="hidden lg:block lg:col-span-3">
            <Card className="p-4 sticky top-20">
              <div className="flex items-center gap-2 mb-4">
                <Clock className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-slate-900">Recent Queries</h3>
              </div>
              <div className="space-y-2">
                {queryHistory.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => setQuery(item.text)}
                    className="w-full text-left p-3 rounded-lg hover:bg-slate-50 transition-colors border border-slate-100"
                  >
                    <p className="text-sm font-medium text-slate-700 line-clamp-2">
                      {item.text}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">{item.time}</p>
                  </button>
                ))}
              </div>
            </Card>
          </aside>

          <main className="lg:col-span-9 space-y-6">
            {/* Query Input Card */}
            <Card className="p-6 shadow-lg border-slate-200">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-amber-500" />
                <h2 className="text-lg font-semibold text-slate-900">
                  Ask Your Legal Question
                </h2>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                  <Textarea
                    placeholder="E.g., How do I file a consumer complaint in India? What are my rights under Section 138 of Negotiable Instruments Act?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="min-h-32 text-base resize-none border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                    disabled={isProcessing}
                  />
                  {query && (
                    <div className="absolute bottom-3 right-3 text-xs text-slate-400">
                      {query.length} characters
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={toggleVoiceInput}
                    className={`${isListening
                      ? "bg-red-50 border-red-300 text-red-600 animate-pulse"
                      : "border-slate-300 hover:border-blue-500"
                      }`}
                    disabled={isProcessing}
                  >
                    <Mic className="w-4 h-4 mr-2" />
                    {isListening ? "Listening..." : "Voice"}
                  </Button>

                  <Button
                    type="submit"
                    className="flex-1 bg-gradient-to-r from-blue-600 to-amber-500 hover:from-blue-700 hover:to-amber-600 text-white font-semibold shadow-md"
                    disabled={isProcessing || !query.trim()}
                  >
                    {isProcessing ? (
                      <>
                        <svg
                          className="animate-spin -ml-1 mr-2 h-4 w-4"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          />
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          />
                        </svg>
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4 mr-2" />
                        Get Legal Insights
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </Card>

            {(responses.opensource || responses.lawgpt || responses.proprietary) && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-500" />
                  AI Analysis Results
                </h3>

                <div className="grid md:grid-cols-3 gap-4">
                  {/* Open Source */}
                  <Card className="p-5 hover:shadow-xl transition-shadow border-l-4 border-blue-500">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                          <FileText className="w-4 h-4 text-blue-600" />
                        </div>
                        <h4 className="font-semibold text-slate-900">Open Source</h4>
                      </div>
                      <div className="flex gap-1">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleCopy(responses.opensource)}
                        >
                          <Copy className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="ghost">
                          <Volume2 className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="ghost">
                          <Share2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="prose prose-sm max-w-none text-slate-700">
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">
                        {responses.opensource}
                      </p>
                    </div>
                  </Card>

                  {/* LawGPT - Highlighted */}
                  <Card className="p-5 hover:shadow-xl transition-shadow border-l-4 border-amber-500 bg-gradient-to-br from-amber-50 to-white">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center">
                          <Star className="w-4 h-4 text-amber-600 fill-amber-600" />
                        </div>
                        <h4 className="font-semibold text-slate-900">LawGPT</h4>
                      </div>
                      <div className="flex gap-1">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleCopy(responses.lawgpt)}
                        >
                          <Copy className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="ghost">
                          <Volume2 className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="ghost">
                          <Share2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="prose prose-sm max-w-none text-slate-700">
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">
                        {responses.lawgpt}
                      </p>
                    </div>
                  </Card>

                  {/* Proprietary */}
                  <Card className="p-5 hover:shadow-xl transition-shadow border-l-4 border-green-500">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                          <Sparkles className="w-4 h-4 text-green-600" />
                        </div>
                        <h4 className="font-semibold text-slate-900">Proprietary</h4>
                      </div>
                      <div className="flex gap-1">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleCopy(responses.proprietary)}
                        >
                          <Copy className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="ghost">
                          <Volume2 className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="ghost">
                          <Share2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="prose prose-sm max-w-none text-slate-700">
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">
                        {responses.proprietary}
                      </p>
                    </div>
                  </Card>
                </div>
              </div>
            )}

            {!responses.opensource && !isProcessing && (
              <Card className="p-12 text-center bg-gradient-to-br from-blue-50 to-amber-50 border-dashed border-2">
                <Sparkles className="w-12 h-12 mx-auto mb-4 text-amber-500" />
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  Ready to Help You
                </h3>
                <p className="text-slate-600 max-w-md mx-auto">
                  Ask any legal question related to Indian law and get instant insights
                  from multiple AI models
                </p>
              </Card>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
