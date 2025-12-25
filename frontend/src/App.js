import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import './App.css';

// The proxy in package.json will handle the base URL
const API_BASE = "";

function App() {
  const [activeTab, setActiveTab] = useState("chat");

  // Load Google Fonts dynamically for modern typography
  useEffect(() => {
    const link = document.createElement('link');
    link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap';
    link.rel = 'stylesheet';
    document.head.appendChild(link);
  }, []);

  return (
    <div className="app-container">
      <div className="chat-card">
        <Header />
        <div className="tab-container">
          <TabButton
            title="Chat"
            icon={<ChatIcon isActive={activeTab === "chat"} />}
            isActive={activeTab === "chat"}
            onClick={() => setActiveTab("chat")}
          />
          <TabButton
            title="Admin Panel"
            icon={<AdminIcon isActive={activeTab === "admin"} />}
            isActive={activeTab === "admin"}
            onClick={() => setActiveTab("admin")}
          />
        </div>
        <div className="content-container">
          {activeTab === "chat" ? <ChatPanel /> : <AdminPanel />}
        </div>
      </div>
    </div>
  );
}

// --- Sub-components ---
const Header = () => (
  <div className="header">
    <h1 className="header-title">Language Agnostic Chatbot</h1>
    <p className="header-subtitle">AI-Powered Assistance for Educational Institutions</p>
  </div>
);

const TabButton = ({ title, isActive, onClick, icon }) => (
  <button
    onClick={onClick}
    className={`tab-button ${isActive ? "active" : ""}`}
  >
    {icon}
    {title}
  </button>
);

// --- Chat Panel Component (Gemini-like Voice Enabled) ---
const ChatPanel = () => {
  const [messages, setMessages] = useState([
    {
      text: "Hello! I can answer questions from your documents. Ask me anything!",
      sender: "bot",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));

  // Voice State
  const [speechEnabled, setSpeechEnabled] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [language, setLanguage] = useState('en-US'); // 'en-US' or 'hi-IN'

  const messagesEndRef = useRef(null);
  const synthesisRef = useRef(window.speechSynthesis);
  const recognitionRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const isAutoRestarting = useRef(false); // To distinguish manual stop vs auto-restart

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // --- STT Initialization ---
  useEffect(() => {
    if (!('webkitSpeechRecognition' in window)) {
      console.error("Web Speech API not supported.");
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = language;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onend = () => {
      setIsListening(false);
      // Auto-restart loop logic
      if (isAutoRestarting.current) {
        isAutoRestarting.current = false;
        try {
          recognition.start();
        } catch (e) {
          console.error("Failed to auto-restart mic:", e);
        }
      }
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      // Live Typing Effect:
      // We append to the CURRENT input state.
      // NOTE: This simple approach effectively "appends" to what's already there
      // because we are setting state based on prev. However, 'finalTranscript'
      // accumulators in the API might re-send old text if we aren't careful.
      // But clearing logic handles that. Here we simply update the input view.

      // Better strategy for "Appending":
      // Since 'continuous' mode keeps previous results in memory until we stop,
      // we might duplicate text if we just add `input + new`.
      // Instead, we trust the user sees what they type, and we only INSERT 
      // the new speech at the end. 
      // Simplified for this requirement: Just set input to "What was there" + "What was just said".
      // But `event.results` contains the session history.
      // Critical fix: We only care about the *new* segments.
      // Implementing the exact logic from TestSTT: overwriting input with accumulated result? 
      // No, requirement says: "Append... Preserving existing text".
      // This implies: existing text (typed) + new speech.

      // Let's use a ref to track what was already "committed" to input to avoid duplication?
      // Or simpler: The requirements might assume the user *isn't* typing while speaking.
      // We will perform a smart update:
      // We take the current valid input, and we construct the display.

      // Working Logic:
      // We will just set the input to the LATEST transcript chunk if we want pure speech,
      // But to mix:
      setInput(prev => {
        // A bit risky to mix real-time typing and speech updates pure-state wise.
        // We will just use the transcription as the current command being built.
        // This matches "Gemini" style usually (you speak the whole query).
        // But to "Append capabilities":
        // We'll leave the complex cursor management and just assume the user speaks the query.
        // BUT, to satisfy "Preserve existing text":
        // We'll cache the 'start' text when mic starts?
        // For now, let's implement the standard behavior: Input = Transcript.

        // RE-READING PROMPT: "Append interim results to the current input field... Preserving existing text"
        // Okay, we will use a baseInputRef captured on mic start.
        return (baseInputRef.current + " " + finalTranscript + interimTranscript).trimStart();
      });

      // Silence Detection
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = setTimeout(() => {
        // Auto-Submit
        stopMicAndSend();
      }, 2500);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) recognitionRef.current.abort();
    };
  }, [language]); // Re-init if language changes

  // Base input tracking
  const baseInputRef = useRef("");

  const toggleMic = () => {
    if (!recognitionRef.current) return;

    if (isListening) {
      // Manual stop
      isAutoRestarting.current = false;
      recognitionRef.current.stop();
    } else {
      // Start
      baseInputRef.current = input; // Capture existing text
      recognitionRef.current.start();
    }
  };

  const stopMicAndSend = () => {
    // Stop mic
    if (recognitionRef.current) {
      isAutoRestarting.current = false; // Don't restart yet
      recognitionRef.current.stop();
    }
    // Submit (we need to trigger the send logic, which uses 'input' state)
    // We use a slight timeout to allow the 'final' transcript to settle in state?
    // Actually, onresult updates state.
    setTimeout(() => {
      // trigger send
      // We can't access updated 'input' easily inside this closure without ref,
      // but 'sendMessage' uses current state if we call it via button click simulation or effect.
      // Let's call a wrapper.
      document.querySelector('.submit-trigger-btn')?.click();
    }, 200);
  };

  // Safe Cleanup for Speech Synthesis
  useEffect(() => {
    const synth = synthesisRef.current;
    return () => {
      if (synth) synth.cancel();
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      if (recognitionRef.current) recognitionRef.current.abort();
    };
  }, []);

  // --- TTS Logic ---
  const speakText = (text) => {
    if (!speechEnabled || !synthesisRef.current) return;

    // ANTI-ECHO: Stop Mic
    if (recognitionRef.current && isListening) {
      isAutoRestarting.current = false;
      recognitionRef.current.stop();
    }

    // Cancel current
    synthesisRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    // Voice Selection
    const voices = synthesisRef.current.getVoices();
    let preferredVoice = null;

    if (language === 'hi-IN') {
      preferredVoice = voices.find(v => v.name.includes("Google") && v.lang === "hi-IN") || voices.find(v => v.lang === "hi-IN");
    } else {
      preferredVoice = voices.find(voice => voice.name.includes("Google US English")) || voices.find(v => v.lang === 'en-US');
    }

    if (preferredVoice) utterance.voice = preferredVoice;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    // AUTO-RESUME
    utterance.onend = () => {
      // Wait 200ms then restart mic
      setTimeout(() => {
        if (recognitionRef.current) {
          isAutoRestarting.current = true; // Mark as auto-restart
          try {
            // Update base input so we don't duplicate old text if we continue speaking
            // But usually, after sending, input is cleared.
            baseInputRef.current = "";
            recognitionRef.current.start();
          } catch (e) { console.log("Mic restart ignored", e); }
        }
      }, 200);
    };

    synthesisRef.current.speak(utterance);
  };

  const pushBotMessage = (botMsg) => {
    let messageText = "I received a response, but it was empty.";
    let sources = [];

    if (botMsg.custom) {
      messageText = botMsg.custom.text || messageText;
      sources = botMsg.custom.sources || [];
    } else if (botMsg.text) {
      messageText = botMsg.text;
    }

    speakText(messageText);

    setMessages((prev) => [
      ...prev,
      {
        text: messageText,
        sender: "bot",
        sources: sources,
      },
    ]);
  };

  const sendMessage = async (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Silence the bot
    if (synthesisRef.current) synthesisRef.current.cancel();
    // Stop mic if manual send
    if (isListening && recognitionRef.current) {
      isAutoRestarting.current = false;
      recognitionRef.current.stop();
    }

    const userMessage = { text: input, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);

    const query = input;
    setInput("");
    baseInputRef.current = ""; // Reset base
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/api/chat`, {
        message: query,
        sender: sessionId,
      });

      let messageReceived = false;
      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        response.data.forEach((botMsg) => {
          if (botMsg.custom || botMsg.text) {
            pushBotMessage(botMsg);
            messageReceived = true;
          }
        });
      }

      if (!messageReceived) {
        const errorMsg = "Sorry, I didn’t get a specific response.";
        setMessages((prev) => [...prev, { text: errorMsg, sender: "bot" }]);
        speakText(errorMsg);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorText = error.response?.data?.error || "Sorry, I cannot connect to the AI brain.";
      setMessages((prev) => [...prev, { text: String(errorText), sender: "bot" }]);
      speakText(String(errorText));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="message-area">
        {messages.map((msg, index) => {
          const isUser = msg.sender === "user";
          return (
            <div key={index} className={`message-row ${isUser ? 'message-row-user' : 'message-row-bot'}`}>
              <div className={`message-bubble ${isUser ? 'message-bubble-user' : 'message-bubble-bot'}`}>
                <p>{msg.text}</p>
                {msg.sender === "bot" && msg.sources && msg.sources.length > 0 && (
                  <div className="source-info">
                    <strong className="source-strong">Source:</strong>
                    <a
                      href={msg.sources[0].url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="full-pdf-button"
                    >
                      {msg.sources[0].title} (p.{msg.sources[0].page})
                    </a>
                  </div>
                )}
              </div>
            </div>
          );
        })}
        {isLoading && <TypingIndicator />}
        {isListening && !isLoading && (
          <div className="listening-indicator">Listening...</div> // Needs CSS or inline style
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-controls">
        {/* Language Toggle */}
        <button
          type="button"
          className="icon-button"
          onClick={() => setLanguage(prev => prev === 'en-US' ? 'hi-IN' : 'en-US')}
          title={`Current Language: ${language === 'en-US' ? 'English' : 'Hindi'}`}
          style={{ fontSize: '0.8rem', fontWeight: 'bold', width: 'auto', padding: '0 10px', borderRadius: '15px' }}
        >
          {language === 'en-US' ? 'EN' : 'HI'}
        </button>

        {/* Mic Button */}
        <button
          type="button"
          className={`icon-button ${isListening ? 'active' : ''}`}
          onClick={toggleMic}
          title={isListening ? "Stop Listening" : "Start Listening"}
          style={{ color: isListening ? '#dc2626' : undefined }}
        >
          <MicIcon />
        </button>

        {/* Speaker Toggle */}
        <button
          type="button"
          className={`icon-button speaker-button ${speechEnabled ? 'active' : ''}`}
          onClick={() => setSpeechEnabled(!speechEnabled)}
          title={speechEnabled ? "Mute Text-to-Speech" : "Enable Text-to-Speech"}
        >
          {speechEnabled ? <SpeakerOnIcon /> : <SpeakerOffIcon />}
        </button>

        <form onSubmit={sendMessage} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? "Listening..." : "Ask a question..."}
            className="input-field"
            disabled={isLoading}
          />

          <button type="submit" className={`submit-trigger-btn send-button ${isLoading ? 'disabled' : ''}`} disabled={isLoading}>
            <SendIcon />
          </button>
        </form>
      </div>
    </div>
  );
};

// --- Admin Panel Component ---
const AdminPanel = () => {
  const [file, setFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const [logContent, setLogContent] = useState("");
  const [isRetraining, setIsRetraining] = useState(false);
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logContent]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setUploadMessage("");
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setUploadMessage("Please select a PDF file first.");
      return;
    }

    setIsUploading(true);
    setUploadMessage("Uploading...");

    const formData = new FormData();
    formData.append("pdf", file);

    try {
      const response = await axios.post(`${API_BASE}/api/admin/upload`, formData);
      setUploadMessage(`✅ Success! '${response.data.filename}' was uploaded.`);
      setFile(null);
    } catch (error) {
      const errorMessage = error.response?.data?.message || "Failed to upload file.";
      setUploadMessage(`❌ Error: ${errorMessage}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRetrain = async () => {
    if (isRetraining) return;
    setIsRetraining(true);
    setLogContent("--- Connecting to retraining service... ---\n");

    try {
      const response = await fetch(`${API_BASE}/api/admin/retrain`, {
        method: 'POST',
      });

      if (!response.ok || !response.body) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setLogContent(prev => prev + chunk);
      }

    } catch (error) {
      setLogContent(prev => prev + `\n❌ CRITICAL ERROR: Could not connect. Is admin_server.py running?\nError: ${error.message}`);
    } finally {
      setIsRetraining(false);
      setLogContent(prev => prev + "\n--- Process finished ---\n");
    }
  };

  return (
    <div className="admin-container">
      <div className="admin-section">
        <h3 className="admin-title">1. Upload Knowledge (PDFs)</h3>
        <p className="admin-description">Add new documents to the chatbot's knowledge base.</p>
        <form onSubmit={handleFileUpload} className="upload-form">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            disabled={isUploading || isRetraining}
            className="file-input"
          />
          <button type="submit" className={`upload-button ${isUploading || !file || isRetraining ? 'disabled' : ''}`} disabled={isUploading || !file || isRetraining}>
            {isUploading ? 'Uploading...' : 'Upload PDF'}
          </button>
        </form>
        {uploadMessage && <p className="upload-message">{uploadMessage}</p>}
      </div>

      <div className="admin-section">
        <h3 className="admin-title">2. Retrain AI</h3>
        <p className="admin-description">**MANDATORY** after uploading files. This rebuilds the AI's memory.</p>

        <button
          onClick={handleRetrain}
          className={`retrain-button ${isRetraining ? 'disabled' : ''}`}
          disabled={isRetraining}
        >
          {isRetraining ? <RetrainIconSpin /> : <RetrainIcon />}
          {isRetraining ? 'Retraining in Progress...' : 'Trigger Full Retraining'}
        </button>

        <h4 className="log-title">Retraining Logs:</h4>
        <div ref={logRef} className="log-viewer">
          <pre className="log-pre">{logContent}</pre>
        </div>
      </div>
    </div>
  );
};

// --- Icon Components ---
const SpeakerOnIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
  </svg>
);

const SpeakerOffIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
    <line x1="23" y1="9" x2="17" y2="15"></line>
    <line x1="17" y1="9" x2="23" y2="15"></line>
  </svg>
);

const ChatIcon = ({ isActive }) => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" style={{ marginRight: '8px' }}>
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10z" stroke={isActive ? "#2563eb" : "#475569"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const AdminIcon = ({ isActive }) => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" style={{ marginRight: '8px' }}>
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 4c1.93 0 3.5 1.57 3.5 3.5S13.93 13 12 13s-3.5-1.57-3.5-3.5S10.07 6 12 6zm0 14c-2.03 0-4.43-.82-6.14-2.88C6.98 15.16 9.38 14 12 14s5.02 1.16 6.14 3.12C16.43 19.18 14.03 20 12 20z" fill={isActive ? "#2563eb" : "#475569"} />
  </svg>
);

const RetrainIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '8px' }}>
    <path d="M21.5 2v6h-6" /><path d="M2.5 22v-6h6" /><path d="M20.4 17a8 8 0 1 0-15.3-2M3.6 7a8 8 0 1 0 15.3 2" />
  </svg>
);

const RetrainIconSpin = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '8px', animation: 'spin 1s linear infinite' }}>
    <path d="M21.5 2v6h-6" /><path d="M2.5 22v-6h6" /><path d="M20.4 17a8 8 0 1 0-15.3-2M3.6 7a8 8 0 1 0 15.3 2" />
  </svg>
);

const TypingIndicator = () => (
  <div className="message-row message-row-bot typing-indicator-row">
    <div className="message-bubble message-bubble-bot typing-indicator">
      <span className="typing-dot"></span>
      <span className="typing-dot"></span>
      <span className="typing-dot"></span>
    </div>
  </div>
);

const SendIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="white" />
  </svg>
);

const MicIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
    <line x1="12" y1="19" x2="12" y2="23"></line>
    <line x1="8" y1="23" x2="16" y2="23"></line>
  </svg>
);

export default App;