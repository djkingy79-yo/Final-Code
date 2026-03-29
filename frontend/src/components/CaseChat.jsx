import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { MessageCircle, Send, X, ChevronDown } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { API } from "../App";

const CaseChat = ({ caseId, user }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const [sending, setSending] = useState(false);
  const [typingUsers, setTypingUsers] = useState({});
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const pollRef = useRef(null);

  const token = localStorage.getItem("session_token");
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (caseId) {
      fetchMessages();
      connectWebSocket();
      // Polling fallback every 10s
      pollRef.current = setInterval(fetchMessages, 10000);
    }
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [caseId]);

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      setUnread(0);
    }
  }, [messages, isOpen]);

  const fetchMessages = async () => {
    try {
      const res = await axios.get(`${API}/cases/${caseId}/messages`, { headers });
      setMessages(res.data || []);
    } catch (e) {
      console.error("Failed to fetch messages:", e);
    }
  };

  const connectWebSocket = () => {
    try {
      const wsUrl = API.replace("https://", "wss://").replace("http://", "ws://");
      const ws = new WebSocket(`${wsUrl}/cases/${caseId}/chat/ws?session_token=${token}`);
      ws.onopen = () => console.log("Chat WS connected");
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "new_message") {
          setMessages((prev) => [...prev, data.payload]);
          if (!isOpen) setUnread((prev) => prev + 1);
        } else if (data.type === "typing") {
          const { user_id, name, is_typing } = data.payload;
          setTypingUsers((prev) => {
            const next = { ...prev };
            if (is_typing) {
              next[user_id] = name;
            } else {
              delete next[user_id];
            }
            return next;
          });
        }
      };
      ws.onclose = () => {
        setTimeout(() => {
          if (caseId) connectWebSocket();
        }, 5000);
      };
      wsRef.current = ws;
    } catch (e) {
      console.error("WebSocket connection failed:", e);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || sending) return;
    setSending(true);
    // Stop typing indicator
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "typing", is_typing: false }));
    }
    try {
      await axios.post(`${API}/cases/${caseId}/messages`, { content: newMessage.trim() }, { headers });
      setNewMessage("");
      fetchMessages();
    } catch (e) {
      console.error("Failed to send:", e);
    } finally {
      setSending(false);
    }
  };

  const handleInputChange = (e) => {
    setNewMessage(e.target.value);
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "typing", is_typing: e.target.value.length > 0 }));
    }
  };

  const typingNames = Object.values(typingUsers).filter((name) => name !== user?.name);

  const formatTime = (ts) => {
    const d = new Date(ts);
    return d.toLocaleTimeString("en-AU", { hour: "2-digit", minute: "2-digit" });
  };

  const formatDate = (ts) => {
    const d = new Date(ts);
    const today = new Date();
    if (d.toDateString() === today.toDateString()) return "Today";
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    if (d.toDateString() === yesterday.toDateString()) return "Yesterday";
    return d.toLocaleDateString("en-AU", { day: "numeric", month: "short" });
  };

  // Group messages by date
  const groupedMessages = messages.reduce((acc, msg) => {
    const dateKey = formatDate(msg.created_at);
    if (!acc[dateKey]) acc[dateKey] = [];
    acc[dateKey].push(msg);
    return acc;
  }, {});

  return (
    <>
      {/* Chat Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => { setIsOpen(true); setUnread(0); }}
          className="fixed bottom-24 right-6 z-40 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-3.5 shadow-lg transition-all"
          data-testid="chat-toggle-btn"
        >
          <MessageCircle className="w-6 h-6" />
          {unread > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
              {unread}
            </span>
          )}
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-40 w-80 sm:w-96 bg-white border border-slate-200 rounded-2xl shadow-2xl flex flex-col" style={{ height: "480px" }} data-testid="chat-panel">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-blue-600 text-white rounded-t-2xl">
            <div className="flex items-center gap-2">
              <MessageCircle className="w-5 h-5" />
              <span className="font-semibold text-sm">Case Discussion</span>
            </div>
            <div className="flex items-center gap-1">
              <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-blue-700 rounded" data-testid="chat-minimise-btn">
                <ChevronDown className="w-4 h-4" />
              </button>
              <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-blue-700 rounded" data-testid="chat-close-btn">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1" data-testid="chat-messages">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full text-slate-400 text-sm">
                No messages yet. Start the conversation.
              </div>
            ) : (
              Object.entries(groupedMessages).map(([date, msgs]) => (
                <div key={date}>
                  <div className="text-center my-2">
                    <span className="text-xs text-slate-400 bg-slate-100 px-3 py-0.5 rounded-full">{date}</span>
                  </div>
                  {msgs.map((msg) => {
                    const isMe = msg.user_id === user?.user_id;
                    return (
                      <div key={msg.message_id} className={`flex flex-col mb-1.5 ${isMe ? "items-end" : "items-start"}`}>
                        {!isMe && (
                          <span className="text-xs text-slate-500 mb-0.5 ml-1">{msg.author_name}</span>
                        )}
                        <div className={`max-w-[75%] px-3 py-2 rounded-2xl text-sm ${isMe ? "bg-blue-600 text-white rounded-br-md" : "bg-slate-100 text-slate-800 rounded-bl-md"}`}>
                          {msg.content}
                        </div>
                        <span className="text-[10px] text-slate-400 mt-0.5 mx-1">{formatTime(msg.created_at)}</span>
                      </div>
                    );
                  })}
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Typing Indicator */}
          {typingNames.length > 0 && (
            <div className="px-3 py-1.5 text-xs text-slate-500 italic">
              {typingNames.join(", ")} {typingNames.length === 1 ? "is" : "are"} typing...
            </div>
          )}

          {/* Input */}
          <form onSubmit={handleSend} className="flex items-center gap-2 px-3 py-2 border-t border-slate-200" data-testid="chat-input-form">
            <Input
              value={newMessage}
              onChange={handleInputChange}
              placeholder="Type a message..."
              className="flex-1 text-sm"
              data-testid="chat-message-input"
            />
            <Button type="submit" size="sm" disabled={!newMessage.trim() || sending} className="bg-blue-600 hover:bg-blue-700 text-white px-3" data-testid="chat-send-btn">
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      )}
    </>
  );
};

export default CaseChat;
