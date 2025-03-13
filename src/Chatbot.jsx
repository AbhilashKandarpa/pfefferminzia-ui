import React, { useState } from "react";
import { MessageCircle, User, Bot, Send, PlusCircle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import "./Chatbot.css";

const Chatbot = () => {
  const [chats, setChats] = useState([
    { id: 1, name: "Chat 1", messages: [{ id: 1, text: "Hallo! Wie kann ich Ihnen weiterhelfen?", sender: "bot" }] }
  ]);
  const [currentChatId, setCurrentChatId] = useState(1);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { id: Date.now(), text: input, sender: "user" };
    setIsLoading(true);

    setChats((prevChats) => {
      return prevChats.map((chat) => {
        if (chat.id === currentChatId) {
          return {
            ...chat,
            messages: [...chat.messages, userMessage]
          };
        }
        return chat;
      });
    });

    try {
      // Use environment variable for API URL if available
      const apiUrl = process.env.REACT_APP_API_URL || 'https://pfefferminziatestapp.agreeablebay-86e3278e.germanywestcentral.azurecontainerapps.io';
      const response = await fetch(`${apiUrl}/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ input: input })
      });

      const data = await response.text();
      
      setChats((prevChats) => {
        return prevChats.map((chat) => {
          if (chat.id === currentChatId) {
            return {
              ...chat,
              messages: [...chat.messages,
                { id: Date.now(), text: data, sender: "bot" }
              ]
            };
          }
          return chat;
        });
      });
    } catch (error) {
      console.error('Error:', error);
      // Optionally add error message to chat
      setChats((prevChats) => {
        return prevChats.map((chat) => {
          if (chat.id === currentChatId) {
            return {
              ...chat,
              messages: [...chat.messages,
                { id: Date.now(), text: "Es tut mir leid, es ist ein Fehler aufgetreten.", sender: "bot" }
              ]
            };
          }
          return chat;
        });
      });
    } finally {
      setIsLoading(false);
      setInput("");
    }
  };

  const handleNewChat = () => {
    const newChat = {
      id: chats.length + 1,
      name: `Chat ${chats.length + 1}`,
      messages: [{ id: 1, text: "Hallo! Wie kann ich Ihnen weiterhelfen?", sender: "bot" }]
    };
    setChats([...chats, newChat]);
    setCurrentChatId(newChat.id);
  };

  return (
    <div className="chatbot-container">
      <div className="sidebar">
        <button className="new-chat-button" onClick={handleNewChat}>
          <PlusCircle size={20} /> Neuer Chat
        </button>
        <div className="chat-list">
          {chats.map((chat) => (
            <div 
              key={chat.id} 
              className={`chat-list-item ${chat.id === currentChatId ? "active" : ""}`} 
              onClick={() => setCurrentChatId(chat.id)}
            >
              {chat.name}
            </div>
          ))}
        </div>
      </div>
      <div className="chat-area">
        <div className="chatbot-header">
          <img src="/Pfefferminzia.png" alt="Logo" className="pfefferminzia-logo" />
          <h1>Wissensmanagement</h1>
        </div>
        <motion.div
          className="chatbot-box"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="chatbot-messages">
            {chats.find(chat => chat.id === currentChatId)?.messages.map((msg) => (
              <div key={msg.id} className={`chat-message ${msg.sender === "bot" ? "bot-message" : "user-message"}`}>
                {msg.sender === "bot" ? <Bot size={20} className="bot-icon" /> : null}
                <div className="message-text">{msg.text}</div>
                {msg.sender === "user" ? <User size={20} className="user-icon" /> : null}
              </div>
            ))}
            {isLoading && (
              <div className="chat-message bot-message">
                <Bot size={20} className="bot-icon" />
                <div className="message-text">
                  <Loader2 className="animate-spin" size={20} />
                </div>
              </div>
            )}
          </div>
          <div className="chatbot-input-container">
            <input
              type="text"
              value={input}
              placeholder="Nachricht eingeben"
              className="chatbot-input"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              disabled={isLoading}
            />
            <button 
              className="send-button" 
              onClick={handleSendMessage}
              disabled={isLoading}
            >
              {isLoading ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <Send size={20} className="send-icon" />
              )}
            </button>
          </div>
        </motion.div>
      </div>
      <div className="footer-info">
        <p>Tool by</p>
        <img src="/fairdigital-logo.png" alt="fd-logo" className="footer-logo" />
        <p>&</p>
        <img src="/Alan_logo_weiß.svg" alt="alan" className="footer-logo" />
      </div>
    </div>
  );
};

export default Chatbot;
