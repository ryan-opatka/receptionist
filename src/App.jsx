import { useState } from 'react';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([{ text: 'Where are you going?', isBot: true }]);
  const [currentMapImage, setCurrentMapImage] = useState('');

  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    // Add user's message to the chat
    const userMessage = { text: input, isBot: false };
    setMessages((prevMessages) => [...prevMessages, userMessage]);

    try {
      // Send user input to the backend
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();
      console.log('Backend response:', data);  // Debugging log

      // Add the bot's response to the chat
      const botMessage = { text: data.response, isBot: true };
      setMessages((prevMessages) => [...prevMessages, botMessage]);

      // Update the map image if one is provided
      if (data.map_image) {
        setCurrentMapImage(data.map_image);
      }
    } catch (error) {
      console.error('Error fetching from backend:', error);
    }

    // Clear the input field
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
        {/* Chat and Map Container */}
        <div className="chat-map-container">
          {/* Chat Messages */}
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
            
            {/* Input Area */}
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

          {/* Map Visualization */}
          <div className="map-container">
            {currentMapImage && (
              <img
                src={`data:image/png;base64,${currentMapImage}`}
                alt="Map visualization"
                className="map-image"
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;