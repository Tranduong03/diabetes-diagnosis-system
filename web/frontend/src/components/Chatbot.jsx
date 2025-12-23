import { useState, useEffect, useRef } from 'react';

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [quickQuestions, setQuickQuestions] = useState([]);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // --- Logic code giữ nguyên ---
  useEffect(() => {
    fetchQuickQuestions();
    setMessages([{
      type: 'bot',
      content: 'Xin chào! 👋 Tôi là trợ lý AI của Hệ thống Chẩn đoán Tiểu đường.\n\nTôi có thể giúp bạn:\n• Tìm hiểu về bệnh tiểu đường\n• Giải đáp thắc mắc về triệu chứng, chẩn đoán\n• Hướng dẫn sử dụng hệ thống\n\nBạn muốn hỏi gì? 😊',
      timestamp: new Date()
    }]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Tự động điều chỉnh chiều cao textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const fetchQuickQuestions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/chatbot/quick-questions');
      const data = await response.json();
      if (data.success) setQuickQuestions(data.questions);
    } catch (error) {
      console.error('Error fetching quick questions:', error);
    }
  };

  const sendMessage = async (messageText = input) => {
    if (!messageText.trim()) return;

    const userMessage = { type: 'user', content: messageText, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/chatbot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageText, session_id: `session_${Date.now()}` })
      });
      const data = await response.json();
      
      setIsTyping(false);
      const botMessage = {
        type: 'bot',
        content: data.answer,
        confidence: data.confidence,
        category: data.category,
        relatedQuestions: data.related_questions,
        suggestions: data.suggestions,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      setIsTyping(false);
      setMessages(prev => [...prev, { type: 'bot', content: 'Xin lỗi, tôi gặp lỗi kết nối. Vui lòng thử lại sau.', timestamp: new Date() }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // --- Render ---
  return (
    <>
      <div className="chatbot-wrapper">
        {/* Toggle Button */}
        <button 
          className={`chatbot-toggle ${isOpen ? 'hidden' : ''}`}
          onClick={() => setIsOpen(true)}
        >
          <span className="icon">💬</span>
        </button>

        {/* Chat Window */}
        <div className={`chatbot-window ${isOpen ? 'open' : ''}`}>
          
          {/* Header */}
          <div className="chatbot-header">
            <div className="header-info">
              <div className="avatar">🩺</div>
              <div>
                <h3>Trợ lý AI</h3>
                <span className="status">Sẵn sàng hỗ trợ</span>
              </div>
            </div>
            <button className="close-btn" onClick={() => setIsOpen(false)}>✕</button>
          </div>

          {/* Messages Area */}
          <div className="chatbot-body">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message-row ${msg.type}`}>
                {msg.type === 'bot' && <div className="msg-avatar">🤖</div>}
                <div className="message-content">
                  <div className="bubble">
                    {msg.content}
                  </div>
                  
                  {/* Related Questions / Suggestions */}
                  {(msg.relatedQuestions?.length > 0 || msg.suggestions?.length > 0) && (
                    <div className="suggestions-list">
                      <p className="suggestion-label">Gợi ý:</p>
                      {[...(msg.relatedQuestions || []), ...(msg.suggestions || [])].map((item, i) => (
                        <button key={i} onClick={() => sendMessage(item)} className="suggestion-chip">
                          {item}
                        </button>
                      ))}
                    </div>
                  )}
                  
                  <span className="timestamp">
                    {msg.timestamp.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="message-row bot">
                <div className="msg-avatar">🤖</div>
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Questions (Footer overlay when empty) */}
          {messages.length <= 1 && quickQuestions.length > 0 && (
            <div className="quick-questions">
              <p>⚡ Câu hỏi phổ biến:</p>
              <div className="chips-container">
                {quickQuestions.slice(0, 4).map((q) => (
                  <button key={q.id} onClick={() => sendMessage(q.question)} className="quick-chip">
                    {q.icon} {q.question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="chatbot-footer">
            <div className="input-group">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Nhập câu hỏi..."
                rows={1}
              />
              <button onClick={() => sendMessage()} disabled={!input.trim()}>
                ➤
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* --- CSS STYLES --- */}
      <style>{`
        /* Wrapper & Toggle */
        .chatbot-wrapper {
          position: fixed;
          bottom: 24px;
          right: 24px;
          z-index: 9999;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        .chatbot-toggle {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          color: white;
          border: none;
          font-size: 28px;
          cursor: pointer;
          box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
          transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .chatbot-toggle:hover {
          transform: scale(1.1);
        }

        .chatbot-toggle.hidden {
          display: none;
        }

        /* Main Window */
        .chatbot-window {
          width: 380px;
          height: 600px;
          background: #fff;
          border-radius: 16px;
          box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
          display: flex;
          flex-direction: column;
          overflow: hidden;
          opacity: 0;
          transform: translateY(20px) scale(0.95);
          pointer-events: none;
          transition: all 0.3s ease;
          position: absolute;
          bottom: 0;
          right: 0;
        }

        .chatbot-window.open {
          opacity: 1;
          transform: translateY(0) scale(1);
          pointer-events: auto;
        }

        /* Header */
        .chatbot-header {
          background: linear-gradient(135deg, #3b82f6, #1d4ed8);
          padding: 16px;
          color: white;
          display: flex;
          justify-content: space-between;
          align-items: center;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .header-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .header-info .avatar {
          background: rgba(255,255,255,0.2);
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
        }

        .header-info h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
        }

        .header-info .status {
          font-size: 12px;
          opacity: 0.9;
          display: block;
        }

        .close-btn {
          background: none;
          border: none;
          color: white;
          font-size: 20px;
          cursor: pointer;
          opacity: 0.8;
          padding: 4px;
        }
        .close-btn:hover { opacity: 1; }

        /* Chat Body */
        .chatbot-body {
          flex: 1;
          background-color: #f9fafb;
          padding: 16px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        /* Scrollbar styling */
        .chatbot-body::-webkit-scrollbar {
          width: 6px;
        }
        .chatbot-body::-webkit-scrollbar-thumb {
          background-color: #d1d5db;
          border-radius: 3px;
        }

        /* Messages */
        .message-row {
          display: flex;
          gap: 8px;
          max-width: 85%;
          animation: fadeIn 0.3s ease;
        }
        
        .message-row.user {
          align-self: flex-end;
          flex-direction: row-reverse;
        }

        .message-row.bot {
          align-self: flex-start;
        }

        .msg-avatar {
          width: 28px;
          height: 28px;
          background: #e0e7ff;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
          flex-shrink: 0;
        }

        .bubble {
          padding: 10px 14px;
          border-radius: 14px;
          font-size: 14px;
          line-height: 1.5;
          word-wrap: break-word;
          white-space: pre-wrap;
          box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }

        .message-row.user .bubble {
          background: #3b82f6;
          color: white;
          border-bottom-right-radius: 2px;
        }

        .message-row.bot .bubble {
          background: white;
          color: #1f2937;
          border-top-left-radius: 2px;
          border: 1px solid #e5e7eb;
        }

        .timestamp {
          font-size: 10px;
          color: #9ca3af;
          margin-top: 4px;
          display: block;
          text-align: right;
        }
        .message-row.bot .timestamp { text-align: left; }

        /* Suggestions & Chips */
        .suggestions-list {
          margin-top: 8px;
          background: white;
          padding: 10px;
          border-radius: 8px;
          border: 1px solid #e5e7eb;
        }
        
        .suggestion-label {
          margin: 0 0 6px 0;
          font-size: 11px;
          font-weight: 700;
          color: #6b7280;
          text-transform: uppercase;
        }

        .suggestion-chip {
          display: block;
          width: 100%;
          text-align: left;
          background: #f3f4f6;
          border: none;
          padding: 8px 12px;
          margin-bottom: 4px;
          border-radius: 6px;
          font-size: 13px;
          color: #374151;
          cursor: pointer;
          transition: background 0.2s;
        }
        .suggestion-chip:hover {
          background: #e5e7eb;
          color: #111827;
        }

        /* Quick Questions Footer */
        .quick-questions {
          padding: 12px 16px;
          background: white;
          border-top: 1px solid #f3f4f6;
        }
        .quick-questions p {
          margin: 0 0 8px 0;
          font-size: 12px;
          font-weight: 600;
          color: #6b7280;
        }
        .chips-container {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }
        .quick-chip {
          background: #eff6ff;
          border: 1px solid #bfdbfe;
          color: #2563eb;
          padding: 6px 12px;
          border-radius: 99px;
          font-size: 12px;
          cursor: pointer;
          transition: all 0.2s;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          max-width: 100%;
        }
        .quick-chip:hover {
          background: #dbeafe;
        }

        /* Footer Input - ĐÃ CHỈNH SỬA */
        .chatbot-footer {
          padding: 12px 16px;
          background: white;
          border-top: 1px solid #e5e7eb;
          position: relative;
          z-index: 10;
        }

        .input-group {
          display: flex;
          gap: 8px;
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 24px;
          padding: 8px 8px 8px 16px;
          align-items: flex-end;
          transition: all 0.2s;
          min-height: 48px;
        }

        .input-group:focus-within {
          border-color: #3b82f6;
          background: white;
          box-shadow: 0 0 0 2px rgba(59,130,246,0.1);
        }

        /* TEXTAREA - ĐÃ TỐI ƯU */
        .input-group textarea {
          flex: 1;
          border: none;
          background: transparent;
          resize: none;
          outline: none;
          font-size: 14px;
          color: #111827;
          font-weight: 400;
          min-height: 20px;
          max-height: 120px;
          padding: 0;
          line-height: 20px;
          font-family: inherit;
          overflow-y: auto;
          box-sizing: border-box;
          /* Quan trọng: Tự động co giãn */
          height: auto;
          transition: height 0.2s ease;
        }

        .input-group textarea::placeholder {
          color: #9ca3af;
          font-weight: 400;
        }

        /* Scrollbar cho textarea khi nhiều dòng */
        .input-group textarea::-webkit-scrollbar {
          width: 4px;
        }
        .input-group textarea::-webkit-scrollbar-thumb {
          background-color: #cbd5e1;
          border-radius: 2px;
        }

        /* Nút gửi */
        .input-group button {
          width: 36px;
          height: 36px;
          border: none;
          border-radius: 50%;
          background: #3b82f6;
          color: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          transition: all 0.2s;
          flex-shrink: 0;
          margin-bottom: 2px;
        }

        .input-group button:disabled {
          background: #d1d5db;
          cursor: not-allowed;
          transform: none !important;
        }
        
        .input-group button:not(:disabled):hover {
          background: #2563eb;
          transform: scale(1.05);
        }

        /* Typing Animation */
        .typing-indicator {
          background: #fff;
          padding: 12px;
          border-radius: 14px;
          border-top-left-radius: 2px;
          border: 1px solid #e5e7eb;
          display: flex;
          gap: 4px;
          width: fit-content;
        }
        .typing-indicator span {
          width: 6px;
          height: 6px;
          background: #9ca3af;
          border-radius: 50%;
          animation: bounce 1.4s infinite ease-in-out both;
        }
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        /* Responsive cho mobile */
        @media (max-width: 480px) {
          .chatbot-window {
            width: 100vw;
            height: 100vh;
            border-radius: 0;
            bottom: 0;
            right: 0;
          }
          
          .chatbot-toggle {
            bottom: 20px;
            right: 20px;
          }
        }
      `}</style>
    </>
  );
}