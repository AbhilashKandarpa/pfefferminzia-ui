import React, { useState } from "react";
import { MessageCircle, User, Bot, Send, PlusCircle, Loader2, RefreshCw } from "lucide-react";
import { motion } from "framer-motion";
import "./Chatbot.css";

const Chatbot = () => {
  const [chats, setChats] = useState([
    { id: 1, name: "Chat 1", messages: [{ id: 1, text: "Hallo, ich bin das Wissensmanagement von Pfefferminzia.", sender: "bot" }] }
  ]);
  const [currentChatId, setCurrentChatId] = useState(1);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [updateStatus, setUpdateStatus] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);

  const handleUpdateKnowledgeBase = async () => {
    setIsUpdating(true);
    try {
      const response = await fetch('http://localhost:8000/update_wb', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.text();
      setUpdateStatus(result);
      
      setTimeout(() => setUpdateStatus(null), 5000);

    } catch (error) {
      console.error('Error:', error);
      setUpdateStatus('Fehler beim Aktualisieren der Wissensdatenbank');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { id: Date.now(), text: input, sender: "user" };
    setIsLoading(true);

    try {
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

        const currentChat = chats.find(chat => chat.id === currentChatId);
        const endpoint = currentChat.messages.length > 1 ? "continue_chat" : "start_chat";
        const url = `http://localhost:8000/${endpoint}`;

        console.log("Sending request to:", url);

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({ input: input })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        let botResponse = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const text = new TextDecoder().decode(value);
            botResponse += text;

            setChats((prevChats) => {
                return prevChats.map((chat) => {
                    if (chat.id === currentChatId) {
                        return {
                            ...chat,
                            messages: [...chat.messages.filter(msg => msg.sender !== 'bot-stream'),
                                { id: chat.messages.length + 2, text: botResponse, sender: "bot" }
                            ]
                        };
                    }
                    return chat;
                });
            });
        }
    } catch (error) {
        console.error('Error:', error);
        setChats((prevChats) => {
            return prevChats.map((chat) => {
                if (chat.id === currentChatId) {
                    return {
                        ...chat,
                        messages: [...chat.messages,
                            { 
                                id: Date.now(),
                                text: "Error: Could not connect to server. Please ensure the server is running.",
                                sender: "bot"
                            }
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
      messages: [{ id: 1, text: "Hallo, ich bin das Wissensmanagement von Pfefferminzia.", sender: "bot" }]
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
        <button 
          className="update-kb-button" 
          onClick={handleUpdateKnowledgeBase}
          disabled={isUpdating}
        >
          <RefreshCw size={20} className={isUpdating ? 'animate-spin' : ''} />
          Wissensdatenbank aktualisieren
        </button>
        {updateStatus && (
          <div className="update-status">
            {updateStatus}
          </div>
        )}
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
      </div>
    </div>
  );
};

export default Chatbot;