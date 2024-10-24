import { useState, useEffect, useRef } from 'react';
import './App.css';

// Helper function to parse text and convert URLs to clickable links
const formatMessageText = (text) => {
  return text.split('\n').map((line, i) => {
    if (line.includes('URL:')) {
      const [label, url] = line.split('URL:').map(part => part.trim());
      return (
        <p key={i}>
          {label && `${label} `}
          <a 
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="message-link"
          >
            {url}
          </a>
        </p>
      );
    }
    return <p key={i}>{line}</p>;
  });
};

function App() {
  // State management
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([{ 
    text: 'Welcome to the Northwestern University Library Information System!\n\nI can help you with directions or information about the library. How can I assist you?', 
    isBot: true 
  }]);
  const [currentMapImage, setCurrentMapImage] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages update
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle message submission
  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    // Add user message to chat
    const userMessage = { text: input, isBot: false };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input,
          chat_history: chatHistory
        }),
      });

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Add bot response to chat
      const botMessage = { text: data.response, isBot: true };
      setMessages((prevMessages) => [...prevMessages, botMessage]);

      // Update chat history with intent
      if (data.intent) {
        setChatHistory((prevHistory) => [
          ...prevHistory,
          {
            question: input,
            answer: data.response,
            intent: data.intent
          }
        ]);
      }

      // Handle map image if provided
      if (data.map_image) {
        setCurrentMapImage(data.map_image);
        setMessages((prevMessages) => [
          ...prevMessages,
          { 
            text: "Click 'View Map' below to see the location.", 
            isBot: true,
            hasMap: true 
          }
        ]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: 'Sorry, there was an error processing your request. Please try again.', isBot: true }
      ]);
    } finally {
      setIsLoading(false);
      setInput('');
    }
  };

  // Handle enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSendMessage();
    }
  };

  // Handle map view button click
  const handleViewMap = () => {
    if (currentMapImage) {
      setIsModalOpen(true);
    }
  };

  return (
    <div className="app-container">
      <h1>Northwestern University Library Assistant</h1>
      
      <div className="chat-fullscreen">
        <div className="messages-container">
          {messages.map((msg, index) => (
            <div 
              key={index} 
              className={`message ${msg.isBot ? 'bot-message' : 'user-message'}`}
            >
              {msg.isBot ? (
                <>
                  {formatMessageText(msg.text)}
                  {msg.hasMap && (
                    <button 
                      className="view-map-button"
                      onClick={handleViewMap}
                    >
                      View Map
                    </button>
                  )}
                </>
              ) : (
                <p>{msg.text}</p>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="message bot-message">
              <p className="typing-indicator">Thinking...</p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about directions or library information..."
            className="chat-input"
            disabled={isLoading}
          />
          <button 
            onClick={handleSendMessage} 
            className={`send-button ${isLoading ? 'disabled' : ''}`}
            disabled={isLoading}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>

      {/* Map Modal */}
      {isModalOpen && currentMapImage && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button 
              className="modal-close" 
              onClick={() => setIsModalOpen(false)}
              aria-label="Close map"
            >
              ×
            </button>
            <img
              src={`data:image/png;base64,${currentMapImage}`}
              alt="Map visualization"
              className="modal-image"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;