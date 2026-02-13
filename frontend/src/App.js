import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import './App.css';
import { dummyChatResponse, dummyUploadResponse, dummyRetrainGenerator } from './dummyData';

const API_BASE = "";
const USE_DUMMY_DATA = true;

function App() {
  const [view, setView] = useState("landing"); // "landing" | "chat" | "admin"
  const [activeTab, setActiveTab] = useState("chat");
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (file) {
      setUploadedFile(file);
      setView("chat");
      setActiveTab("chat");
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files[0]) handleFileSelect(e.target.files[0]);
  };

  const handleDemoFile = () => {
    setUploadedFile({ name: "demo_document.pdf", size: 245000, demo: true });
    setView("chat");
    setActiveTab("chat");
  };

  const goToLanding = () => {
    setView("landing");
    setUploadedFile(null);
  };

  // Drag and drop
  const handleDragEnter = useCallback((e) => { e.preventDefault(); setIsDragging(true); }, []);
  const handleDragLeave = useCallback((e) => { e.preventDefault(); setIsDragging(false); }, []);
  const handleDragOver = useCallback((e) => { e.preventDefault(); }, []);
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  }, []);

  useEffect(() => {
    window.addEventListener('dragenter', handleDragEnter);
    return () => window.removeEventListener('dragenter', handleDragEnter);
  }, [handleDragEnter]);

  return (
    <div className="app-shell">
      <TopNav activeTab={activeTab} setActiveTab={setActiveTab} view={view} setView={setView} />

      {view === "landing" && (
        <BreadcrumbBar />
      )}

      {view === "landing" && (
        <LandingView
          fileInputRef={fileInputRef}
          handleFileInputChange={handleFileInputChange}
          handleDemoFile={handleDemoFile}
        />
      )}

      {view === "chat" && activeTab === "chat" && (
        <ChatView uploadedFile={uploadedFile} goToLanding={goToLanding} fileInputRef={fileInputRef} handleFileInputChange={handleFileInputChange} />
      )}

      {view === "chat" && activeTab === "admin" && (
        <>
          <TabBar activeTab={activeTab} setActiveTab={setActiveTab} />
          <AdminPanel />
        </>
      )}

      {view === "chat" && activeTab === "chat" && null}

      <input
        type="file"
        ref={fileInputRef}
        className="hidden-file-input"
        accept=".pdf,.docx,.pptx,.txt,.rtf"
        onChange={handleFileInputChange}
      />

      {isDragging && (
        <div className="drag-overlay"
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="drag-overlay-content">
            <h3>📄 Drop your file here</h3>
            <p>PDF, DOCX, PPTX, TXT, or RTF</p>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================
// TOP NAVIGATION BAR
// ============================================
const TopNav = ({ activeTab, setActiveTab, view, setView }) => (
  <nav className="top-nav">
    <div className="nav-left">
      <div className="nav-logo" style={{ cursor: 'pointer' }} onClick={() => setView("landing")}>
        <div className="nav-logo-icon">A</div>
        <span>MKRS AI</span>
      </div>
      <div className="nav-links">
        <button className={`nav-link ${view === 'landing' ? 'active' : ''}`} onClick={() => setView("landing")}>Home</button>
        <button className={`nav-link ${view === 'chat' && activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => { setView("chat"); setActiveTab("chat"); }}>Chat</button>
        <button className={`nav-link ${view === 'chat' && activeTab === 'admin' ? 'active' : ''}`}
          onClick={() => { setView("chat"); setActiveTab("admin"); }}>Admin</button>
        <button className="nav-link">Generative AI</button>
      </div>
    </div>
    <div className="nav-right">
      <button className="btn-free-trial">Get Started</button>
      <button className="btn-sign-in">Sign in</button>
    </div>
  </nav>
);

// ============================================
// BREADCRUMB
// ============================================
const BreadcrumbBar = () => (
  <div className="breadcrumb-bar">
    <a href="#" className="breadcrumb-link" onClick={(e) => e.preventDefault()}>Home</a>
    <span>/</span>
    <a href="#" className="breadcrumb-link" onClick={(e) => e.preventDefault()}>MKRS AI</a>
    <span>/</span>
    AI Chat PDF
  </div>
);

// ============================================
// TAB BAR
// ============================================
const TabBar = ({ activeTab, setActiveTab }) => (
  <div className="tab-bar">
    <button className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab("chat")}>
      <ChatIcon /> Chat
    </button>
    <button className={`tab-btn ${activeTab === 'admin' ? 'active' : ''}`} onClick={() => setActiveTab("admin")}>
      <AdminIcon /> Admin Panel
    </button>
  </div>
);

// ============================================
// LANDING VIEW (Hero)
// ============================================
const LandingView = ({ fileInputRef, handleFileInputChange, handleDemoFile }) => (
  <>
    <section className="hero-section">
      <div className="hero-card">
        <div className="hero-card-inner">
          <div className="hero-brand">
            <div className="hero-brand-icon">A</div>
            <span className="hero-brand-text">MKRS AI Assistant</span>
          </div>

          <div className="hero-content">
            <div className="hero-text-area">
              <h1 className="hero-title">Chat with your PDF</h1>
              <p className="hero-subtitle">
                Get trusted document insights by asking questions with our AI-powered chatbot assistant.
              </p>
              <p className="hero-drop-hint">
                Drag and drop one or more PDF, DOCX, PPTX, TXT, or RTF files.
              </p>
              <div className="hero-actions">
                <button className="btn-select-files" onClick={() => fileInputRef.current?.click()}>
                  <UploadIcon /> Select files
                </button>
                <button className="btn-demo" onClick={handleDemoFile}>
                  Try with a demo file
                </button>
              </div>
            </div>

            <div className="hero-illustration">
              <HeroIllustration />
            </div>
          </div>
        </div>
      </div>
    </section>

    <div className="security-footer">
      <SecurityIcon /> Your file will be securely handled and processed locally.
      By using this service, you agree to the <a href="#">Terms of Use</a> and acknowledge the <a href="#">Privacy Policy</a>.
    </div>
  </>
);

// ============================================
// CHAT VIEW
// ============================================

// Cross-browser SpeechRecognition API
const SpeechRecognitionAPI = window.webkitSpeechRecognition || window.SpeechRecognition;
const STT_SUPPORTED = !!SpeechRecognitionAPI;

const ChatView = ({ uploadedFile, goToLanding, fileInputRef, handleFileInputChange }) => {
  const [messages, setMessages] = useState([
    {
      text: `I've analyzed "${uploadedFile?.name || 'your document'}". I'm ready to answer your questions — ask me anything about this document!`,
      sender: "bot",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));

  // Voice State
  const [speechEnabled, setSpeechEnabled] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [language, setLanguage] = useState('en-US');
  const [sttStatus, setSttStatus] = useState('');
  const [sttError, setSttError] = useState('');
  const [interimText, setInterimText] = useState('');

  const messagesEndRef = useRef(null);
  const synthesisRef = useRef(window.speechSynthesis);
  const recognitionRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const isAutoRestarting = useRef(false);
  // We use a ref to hold the accumulated transcript so closures always see latest value
  const transcriptRef = useRef("");

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-clear STT errors after 4 seconds
  useEffect(() => {
    if (sttError) {
      const timer = setTimeout(() => setSttError(''), 4000);
      return () => clearTimeout(timer);
    }
  }, [sttError]);

  // === Create a NEW SpeechRecognition instance each time we start ===
  // This avoids stale state issues entirely
  const startListening = useCallback(() => {
    if (!STT_SUPPORTED) {
      setSttError('Speech recognition is not supported in this browser. Please use Google Chrome.');
      return;
    }

    // Abort any existing recognition first
    if (recognitionRef.current) {
      try { recognitionRef.current.abort(); } catch (e) { /* ignore */ }
      recognitionRef.current = null;
    }

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = false;    // Single-shot: stops after one sentence
    recognition.interimResults = true; // Show real-time partial text
    recognition.lang = language;
    recognition.maxAlternatives = 1;

    // Store the current input value at the moment we start
    const startingText = input;
    transcriptRef.current = "";

    recognition.onstart = () => {
      console.log('[STT] Started');
      setIsListening(true);
      setSttStatus('listening');
      setSttError('');
    };

    recognition.onspeechstart = () => {
      console.log('[STT] Speech detected');
      setSttStatus('processing');
    };

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          final += result[0].transcript;
        } else {
          interim += result[0].transcript;
        }
      }

      console.log('[STT] onresult — final:', JSON.stringify(final), 'interim:', JSON.stringify(interim));

      // Build the full text: starting text + final + interim
      if (final) {
        transcriptRef.current = final;
      }
      const display = (startingText + ' ' + (transcriptRef.current || interim)).trim();

      // Directly update both the state AND the DOM element for immediate feedback
      setInput(display);
      setInterimText(interim);

      // Also force-set the DOM value in case React batching delays the update
      const inputEl = document.querySelector('.chat-input-field');
      if (inputEl) {
        inputEl.value = display;
      }

      // Clear any previous silence timer
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    };

    recognition.onerror = (event) => {
      console.error('[STT] Error:', event.error);

      if (event.error === 'aborted') return; // Intentional

      if (event.error === 'no-speech') {
        setSttError('No speech was detected. Please click the mic and try speaking closer to it.');
        setIsListening(false);
        setSttStatus('');
        return;
      }

      const msgs = {
        'not-allowed': 'Microphone access was denied. Please allow it in your browser settings (click the lock icon in the address bar).',
        'audio-capture': 'No microphone found. Please plug in a microphone.',
        'network': 'Network error — speech recognition needs internet.',
        'service-not-allowed': 'Speech service unavailable. Please try again.',
      };
      setSttError(msgs[event.error] || 'Speech error: ' + event.error);
      setIsListening(false);
      setSttStatus('');
    };

    recognition.onend = () => {
      console.log('[STT] Ended. Transcript:', JSON.stringify(transcriptRef.current));
      setIsListening(false);
      setSttStatus('');
      setInterimText('');

      // If we got a transcript, make sure the input has it
      if (transcriptRef.current) {
        const finalText = (startingText + ' ' + transcriptRef.current).trim();
        setInput(finalText);
        // Also set DOM directly
        const inputEl = document.querySelector('.chat-input-field');
        if (inputEl) inputEl.value = finalText;
      }

      // Handle TTS auto-restart
      if (isAutoRestarting.current) {
        isAutoRestarting.current = false;
        // Don't auto-restart here — user must click mic
      }
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
      console.log('[STT] start() called');
    } catch (e) {
      console.error('[STT] Failed to start:', e);
      setSttError('Could not start microphone: ' + e.message);
      setIsListening(false);
      setSttStatus('');
    }
  }, [language, input]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch (e) { /* ignore */ }
    }
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    setIsListening(false);
    setSttStatus('');
    setInterimText('');
  }, []);

  const toggleMic = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch (e) { /* ignore */ }
      }
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    };
  }, []);

  // Cleanup synthesis on unmount
  useEffect(() => {
    const synth = synthesisRef.current;
    return () => {
      if (synth) synth.cancel();
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    };
  }, []);

  const speakText = (text) => {
    if (!speechEnabled || !synthesisRef.current) return;
    // Pause recognition while speaking to avoid feedback loop
    if (recognitionRef.current && isListening) {
      isAutoRestarting.current = false;
      recognitionRef.current.stop();
    }
    synthesisRef.current.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const voices = synthesisRef.current.getVoices();
    let preferredVoice = language === 'hi-IN'
      ? voices.find(v => v.lang === "hi-IN")
      : voices.find(v => v.name.includes("Google US English")) || voices.find(v => v.lang === 'en-US');
    if (preferredVoice) utterance.voice = preferredVoice;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onend = () => {
      // After bot finishes speaking, user can click mic to speak again
      console.log('[TTS] Finished speaking');
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
    setMessages((prev) => [...prev, { text: messageText, sender: "bot", sources }]);
  };

  const sendMessage = async (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Stop any speech/recognition before sending
    if (synthesisRef.current) synthesisRef.current.cancel();
    if (isListening && recognitionRef.current) {
      isAutoRestarting.current = false;
      recognitionRef.current.stop();
    }
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

    const userMessage = { text: input, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    const query = input;
    setInput("");
    setInterimText('');
    transcriptRef.current = "";
    setIsLoading(true);

    if (USE_DUMMY_DATA) {
      setTimeout(() => {
        dummyChatResponse.forEach((botMsg) => pushBotMessage(botMsg));
        setIsLoading(false);
      }, 2500);
      return;
    }

    try {
      const response = await axios.post(`${API_BASE}/api/chat`, { message: query, sender: sessionId });
      let messageReceived = false;
      if (response.data && Array.isArray(response.data)) {
        response.data.forEach((botMsg) => {
          if (botMsg.custom || botMsg.text) {
            pushBotMessage(botMsg);
            messageReceived = true;
          }
        });
      }
      if (!messageReceived) {
        setMessages((prev) => [...prev, { text: "No response received. Please try again.", sender: "bot" }]);
      }
    } catch (error) {
      const errorText = error.response?.data?.error || "Connection error. Please check if the backend is running.";
      setMessages((prev) => [...prev, { text: String(errorText), sender: "bot" }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-view">
      {/* Chat Header */}
      <div className="chat-header-bar">
        <div className="chat-file-info">
          <div className="chat-file-icon">PDF</div>
          <div>
            <div className="chat-file-name">{uploadedFile?.name || "Document"}</div>
            <div className="chat-file-meta">
              {uploadedFile?.size ? `${(uploadedFile.size / 1024).toFixed(1)} KB` : 'Ready to chat'}
            </div>
          </div>
        </div>
        <div className="chat-header-actions">
          <button className="chat-header-btn" onClick={() => fileInputRef.current?.click()}>
            <UploadIcon size={14} /> New File
          </button>
          <button className="chat-header-btn" onClick={goToLanding}>
            ✕ Close
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages-area">
        {messages.map((msg, index) => {
          const isUser = msg.sender === "user";
          return (
            <div key={index} className={`message-row ${isUser ? 'message-row-user' : 'message-row-bot'}`}>
              {!isUser ? (
                <div className="bot-message-wrapper">
                  <div className="bot-avatar">AI</div>
                  <div className="message-bubble message-bubble-bot">
                    <p>{msg.text}</p>
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="source-info">
                        <span className="source-tag">Source:</span>
                        <a href={msg.sources[0].url} target="_blank" rel="noopener noreferrer" className="source-link">
                          {msg.sources[0].title} (Page {msg.sources[0].page})
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="message-bubble message-bubble-user">
                  <p>{msg.text}</p>
                </div>
              )}
            </div>
          );
        })}
        {isLoading && (
          <div className="message-row message-row-bot">
            <div className="bot-message-wrapper">
              <div className="bot-avatar">AI</div>
              <div className="message-bubble message-bubble-bot typing-indicator">
                <span className="dot"></span><span className="dot"></span><span className="dot"></span>
              </div>
            </div>
          </div>
        )}
        {/* Speech-to-text status indicator */}
        {(isListening || sttStatus) && !isLoading && (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '8px' }}>
            <span className="listening-badge">
              <span className="pulse-ring"></span>
              {sttStatus === 'starting' && 'Starting microphone...'}
              {sttStatus === 'listening' && 'Listening — speak now...'}
              {sttStatus === 'processing' && 'Hearing you...'}
              {!sttStatus && isListening && 'Listening...'}
            </span>
          </div>
        )}
        {/* STT Error Toast */}
        {sttError && (
          <div className="stt-error-toast">
            ⚠️ {sttError}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <form onSubmit={sendMessage} className="chat-input-row">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? (interimText ? "Hearing you..." : "Listening — speak now...") : "Ask a question about your document..."}
            className="chat-input-field"
            disabled={isLoading}
          />
          <button type="button"
            className={`input-action-btn ${isListening ? 'mic-active' : ''} ${!STT_SUPPORTED ? 'disabled-btn' : ''}`}
            onClick={toggleMic}
            title={STT_SUPPORTED ? (isListening ? 'Stop listening' : 'Start voice input') : 'Speech recognition not supported'}
          >
            <MicIcon />
          </button>
          <button type="button" className={`input-action-btn ${speechEnabled ? 'active' : ''}`}
            onClick={() => setSpeechEnabled(!speechEnabled)} title="Toggle speech">
            {speechEnabled ? <SpeakerOnIcon /> : <SpeakerOffIcon />}
          </button>
          <button type="submit" className="submit-trigger-btn send-btn" disabled={isLoading || !input.trim()} title="Send">
            <SendIcon />
          </button>
        </form>
        <div className="chat-controls-bar">
          <div className="chat-controls-left">
            <button className={`control-chip ${language === 'en-US' ? 'active' : ''}`}
              onClick={() => setLanguage(prev => prev === 'en-US' ? 'hi-IN' : 'en-US')}>
              🌐 {language === 'en-US' ? 'English' : 'Hindi'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================
// ADMIN PANEL
// ============================================
const AdminPanel = () => {
  const [file, setFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadStatus, setUploadStatus] = useState(""); // "success" | "error" | "info"
  const [isUploading, setIsUploading] = useState(false);
  const [logContent, setLogContent] = useState("");
  const [isRetraining, setIsRetraining] = useState(false);
  const adminFileRef = useRef(null);
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [logContent]);

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) { setUploadMessage("Please select a file first."); setUploadStatus("error"); return; }
    setIsUploading(true);
    setUploadMessage("Uploading..."); setUploadStatus("info");

    if (USE_DUMMY_DATA) {
      setTimeout(() => {
        setUploadMessage(`"${dummyUploadResponse.filename}" uploaded successfully.`);
        setUploadStatus("success");
        setFile(null);
        setIsUploading(false);
      }, 1500);
      return;
    }

    const formData = new FormData();
    formData.append("pdf", file);
    try {
      const response = await axios.post(`${API_BASE}/api/admin/upload`, formData);
      setUploadMessage(`"${response.data.filename}" uploaded successfully.`);
      setUploadStatus("success");
      setFile(null);
    } catch (error) {
      setUploadMessage(`Upload failed: ${error.response?.data?.message || "Unknown error"}`);
      setUploadStatus("error");
    } finally { setIsUploading(false); }
  };

  const handleRetrain = async () => {
    if (isRetraining) return;
    setIsRetraining(true);
    setLogContent("> Starting model retraining...\n");

    if (USE_DUMMY_DATA) {
      const generator = dummyRetrainGenerator();
      for await (const chunk of generator) {
        setLogContent(prev => prev + "> " + chunk);
      }
      setIsRetraining(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/admin/retrain`, { method: 'POST' });
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        setLogContent(prev => prev + decoder.decode(value, { stream: true }));
      }
    } catch (error) {
      setLogContent(prev => prev + `\n❌ Error: ${error.message}\n`);
    } finally {
      setIsRetraining(false);
      setLogContent(prev => prev + "> Process complete.\n");
    }
  };

  return (
    <div className="admin-panel">
      <div className="admin-grid">
        {/* Upload Card */}
        <div className="admin-card">
          <div className="admin-card-header">
            <div className="admin-card-icon upload-icon">📁</div>
            <div>
              <div className="admin-card-title">Upload Knowledge Base</div>
              <div className="admin-card-desc">Add PDF documents to the AI knowledge base</div>
            </div>
          </div>

          <form onSubmit={handleFileUpload}>
            <div
              className={`upload-dropzone ${file ? 'has-file' : ''}`}
              onClick={() => adminFileRef.current?.click()}
            >
              <input type="file" ref={adminFileRef} accept=".pdf" style={{ display: 'none' }}
                onChange={(e) => setFile(e.target.files[0])} disabled={isUploading || isRetraining} />
              {file ? (
                <>
                  <div className="dropzone-icon">✅</div>
                  <div className="dropzone-filename">{file.name}</div>
                </>
              ) : (
                <>
                  <div className="dropzone-icon">📄</div>
                  <div className="dropzone-text">Click to select a PDF file or drag and drop</div>
                </>
              )}
            </div>
            <button
              type="submit"
              className="admin-btn admin-btn-upload"
              disabled={isUploading || !file || isRetraining}
            >
              {isUploading ? <><span className="spin">⏳</span> Uploading...</> : <>📤 Upload File</>}
            </button>
          </form>

          {uploadMessage && (
            <div className={`upload-message ${uploadStatus}`}>{uploadMessage}</div>
          )}
        </div>

        {/* Retrain Card */}
        <div className="admin-card">
          <div className="admin-card-header">
            <div className="admin-card-icon retrain-icon">🧠</div>
            <div>
              <div className="admin-card-title">Retrain AI Model</div>
              <div className="admin-card-desc">Rebuild the knowledge base with updated documents</div>
            </div>
          </div>

          <button
            onClick={handleRetrain}
            className="admin-btn admin-btn-retrain"
            disabled={isRetraining}
          >
            {isRetraining ? <><span className="spin">🔄</span> Retraining...</> : <>🚀 Start Retraining</>}
          </button>

          <div className="log-terminal">
            <div className="log-terminal-header">
              <span className="log-terminal-dot red"></span>
              <span className="log-terminal-dot yellow"></span>
              <span className="log-terminal-dot green"></span>
              <span className="log-terminal-title">Terminal Output</span>
            </div>
            <div ref={logRef} className="log-terminal-body">
              {logContent || "> Waiting for command...\n"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================
// SVG ICONS
// ============================================
const UploadIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" y1="3" x2="12" y2="15" />
  </svg>
);

const SendIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13" />
    <polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

const MicIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
    <line x1="12" y1="19" x2="12" y2="23" />
    <line x1="8" y1="23" x2="16" y2="23" />
  </svg>
);

const SpeakerOnIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
  </svg>
);

const SpeakerOffIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
    <line x1="23" y1="9" x2="17" y2="15" />
    <line x1="17" y1="9" x2="23" y2="15" />
  </svg>
);

const ChatIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10z" />
  </svg>
);

const AdminIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    <line x1="3" y1="9" x2="21" y2="9" />
    <line x1="9" y1="21" x2="9" y2="9" />
  </svg>
);

const SecurityIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }}>
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
  </svg>
);

// Hero illustration — abstract chat/AI graphic
const HeroIllustration = () => (
  <svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
    {/* Document */}
    <rect x="60" y="30" width="60" height="80" rx="8" fill="#f3f4f6" stroke="#d1d5db" strokeWidth="1.5" />
    <line x1="72" y1="50" x2="108" y2="50" stroke="#d1d5db" strokeWidth="2" strokeLinecap="round" />
    <line x1="72" y1="60" x2="100" y2="60" stroke="#d1d5db" strokeWidth="2" strokeLinecap="round" />
    <line x1="72" y1="70" x2="105" y2="70" stroke="#d1d5db" strokeWidth="2" strokeLinecap="round" />
    <line x1="72" y1="80" x2="95" y2="80" stroke="#d1d5db" strokeWidth="2" strokeLinecap="round" />

    {/* Chat bubble 1 */}
    <rect x="115" y="20" width="55" height="35" rx="10" fill="#7c3aed" fillOpacity="0.15" stroke="#7c3aed" strokeWidth="1.5" />
    <circle cx="130" cy="37" r="3" fill="#7c3aed" />
    <circle cx="142" cy="37" r="3" fill="#7c3aed" />
    <circle cx="154" cy="37" r="3" fill="#7c3aed" />

    {/* Chat bubble 2 */}
    <rect x="120" y="65" width="60" height="35" rx="10" fill="#1473e6" fillOpacity="0.12" stroke="#1473e6" strokeWidth="1.5" />
    <line x1="132" y1="78" x2="168" y2="78" stroke="#1473e6" strokeWidth="2" strokeLinecap="round" strokeOpacity="0.5" />
    <line x1="132" y1="88" x2="158" y2="88" stroke="#1473e6" strokeWidth="2" strokeLinecap="round" strokeOpacity="0.5" />

    {/* Connection line */}
    <path d="M120 55 C 125 60, 125 62, 120 68" stroke="#ec1c24" strokeWidth="1.5" strokeDasharray="3 3" fill="none" />

    {/* AI sparkle */}
    <circle cx="155" cy="115" r="12" fill="#ec1c24" fillOpacity="0.1" stroke="#ec1c24" strokeWidth="1" />
    <text x="155" y="119" textAnchor="middle" fontSize="10" fill="#ec1c24" fontWeight="bold">AI</text>

    {/* Decorative arc */}
    <path d="M40 120 Q 90 140, 180 110" stroke="#e5e7eb" strokeWidth="1" fill="none" />
  </svg>
);

export default App;