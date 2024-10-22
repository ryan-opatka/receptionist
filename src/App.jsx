import { useState } from 'react';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([{ text: 'Where are you going?', isBot: true }]);

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
    } catch (error) {
      console.error('Error fetching from backend:', error);
    }

    // Clear the input field
    setInput('');
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Receptionist</h1>
      <div style={{ marginBottom: '10px' }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ textAlign: msg.isBot ? 'left' : 'right' }}>
            <p>{msg.text}</p>
          </div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
        style={{ width: '80%', padding: '10px' }}
      />
      <button onClick={handleSendMessage} style={{ padding: '10px 20px' }}>
        Send
      </button>
    </div>
  );
}

export default App;
