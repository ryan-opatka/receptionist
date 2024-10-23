import { useState } from 'react';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([{ text: 'Where are you going?', isBot: true }]);
  const [currentMapImage, setCurrentMapImage] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    const userMessage = { text: input, isBot: false };
    setMessages((prevMessages) => [...prevMessages, userMessage]);

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();
      console.log('Backend response:', data);

      const botMessage = { text: data.response, isBot: true };
      setMessages((prevMessages) => [...prevMessages, botMessage]);

      if (data.map_image) {
        setCurrentMapImage(data.map_image);
      }
    } catch (error) {
      console.error('Error fetching from backend:', error);
    }

    setInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="app-container">
      <h1>Receptionist</h1>
      
      <div className="main-content">
        <div className="chat-map-container">
          <div className="chat-container">
            <div className="messages-container">
              {messages.map((msg, index) => (
                <div 
                  key={index} 
                  className={`message ${msg.isBot ? 'bot-message' : 'user-message'}`}
                >
                  <p>{msg.text}</p>
                </div>
              ))}
            </div>
            
            <div className="input-container">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="chat-input"
              />
              <button onClick={handleSendMessage} className="send-button">
                Send
              </button>
            </div>
          </div>

          <div className="map-container">
            {currentMapImage && (
              <img
                src={`data:image/png;base64,${currentMapImage}`}
                alt="Map visualization"
                className="map-image"
                onClick={() => setIsModalOpen(true)}
              />
            )}
          </div>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && currentMapImage && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button 
              className="modal-close" 
              onClick={() => setIsModalOpen(false)}
            >
              ×
            </button>
            <img
              src={`data:image/png;base64,${currentMapImage}`}
              alt="Map visualization (large)"
              className="modal-image"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;