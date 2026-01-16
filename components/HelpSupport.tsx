
import React, { useState, useRef, useEffect } from 'react';
import { GoogleGenAI, Chat } from "@google/genai";

interface Message {
  role: 'user' | 'model';
  text: string;
  time: string;
}

const HelpSupport: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isChatOpen, setIsChatOpen] = useState(true);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'model', text: 'Hi there! 👋 Welcome to CommerceAI support. How can we help you with your store today?', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const chatInstance = useRef<Chat | null>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping, isMinimized]);

  const scrollToBottom = () => {
    if (!isMinimized) {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleAction = (label: string) => {
    alert(`Help Center Action: ${label}`);
  };

  const getChat = () => {
    if (!chatInstance.current) {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });
      chatInstance.current = ai.chats.create({
        model: 'gemini-3-flash-preview',
        config: {
          systemInstruction: 'You are Sarah, a friendly and expert customer support agent for CommerceAI. CommerceAI is an advanced e-commerce dashboard that helps users generate product copy, images, and videos. You are helpful, professional, and slightly enthusiastic. Keep answers concise and relevant to e-commerce and AI tools.'
        }
      });
    }
    return chatInstance.current;
  };

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      role: 'user',
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const chat = getChat();
      const response = await chat.sendMessage({ message: text });
      
      const aiMessage: Message = {
        role: 'model',
        text: response.text || "I'm sorry, I couldn't process that. Please try again.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [...prev, { role: 'model', text: "Sorry, I'm having trouble connecting. Is there anything else I can help with?", time: 'Now' }]);
    } finally {
      setIsTyping(false);
    }
  };

  const popularArticles = [
    { title: "How to export images in 4K resolution", icon: "description" },
    { title: "Connecting to Shopify via API", icon: "api" },
    { title: "Troubleshooting generation errors", icon: "bug_report" }
  ];

  const categories = [
    { title: "Getting Started", desc: "Everything you need to set up your store.", icon: "rocket_launch" },
    { title: "Billing & Plans", desc: "Manage subscriptions and payment methods.", icon: "credit_card" },
    { title: "AI Tools Guide", desc: "Learn how to prompt and generate assets.", icon: "psychology" }
  ];

  return (
    <div className="flex-1 flex flex-col h-full bg-background-light dark:bg-background-dark font-display overflow-hidden relative transition-colors">
      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto sidebar-scroll pb-32">
        <div className="layout-container flex flex-col items-center py-10 px-6 md:px-12 w-full">
          <div className="max-w-5xl w-full flex flex-col gap-8">
            {/* Page Header */}
            <div className="flex flex-col gap-4 animate-fade-in-up">
              <h1 className="text-slate-900 dark:text-white text-4xl md:text-5xl font-black leading-tight tracking-tight">Help Center</h1>
              <p className="text-slate-500 dark:text-slate-400 text-lg font-normal leading-relaxed max-w-2xl">Search our knowledge base for answers, browse popular topics, or get in touch with our support team.</p>
            </div>

            {/* Search Bar */}
            <div className="w-full animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
              <div className="relative flex items-center w-full group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <span className="material-symbols-outlined text-primary text-[28px]">search</span>
                </div>
                <input 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAction(`Searching for: ${searchQuery}`)}
                  className="w-full h-14 pl-14 pr-32 rounded-xl bg-white dark:bg-slate-800 border-none shadow-sm ring-1 ring-slate-200 dark:ring-slate-700 focus:ring-2 focus:ring-primary text-slate-900 dark:text-white placeholder:text-slate-400 text-base transition-all" 
                  placeholder="Search for answers, articles, and guides..." 
                  type="text"
                />
                <button 
                  onClick={() => handleAction(`Searching for: ${searchQuery}`)}
                  className="absolute right-3 bg-primary hover:bg-secondary text-white px-5 py-2 rounded-lg font-bold shadow-md transition-all active:scale-95"
                >
                  Search
                </button>
              </div>
            </div>

            {/* Topic Categories */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              {categories.map((cat, i) => (
                <button 
                  key={i}
                  onClick={() => handleAction(cat.title)}
                  className="flex flex-col text-left gap-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800 p-6 hover:shadow-xl hover:-translate-y-1 transition-all group"
                >
                  <div className="size-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-colors shadow-sm">
                    <span className="material-symbols-outlined">{cat.icon}</span>
                  </div>
                  <div>
                    <h2 className="text-slate-900 dark:text-white text-lg font-bold mb-1">{cat.title}</h2>
                    <p className="text-slate-500 dark:text-slate-400 text-sm leading-snug">{cat.desc}</p>
                  </div>
                </button>
              ))}
            </div>

            {/* Popular Articles List */}
            <div className="flex flex-col gap-4 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              <div className="flex items-center justify-between">
                <h3 className="text-slate-900 dark:text-white text-xl font-bold">Popular Articles</h3>
                <button onClick={() => handleAction('View all articles')} className="text-sm font-semibold text-primary hover:text-secondary transition-colors">View all</button>
              </div>
              <div className="flex flex-col gap-3">
                {popularArticles.map((art, i) => (
                  <button 
                    key={i}
                    onClick={() => handleAction(`Read: ${art.title}`)}
                    className="flex items-center gap-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-800 p-4 rounded-xl hover:border-primary hover:shadow-md transition-all group text-left"
                  >
                    <div className="size-10 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center text-slate-500 dark:text-slate-400 group-hover:text-primary transition-colors">
                      <span className="material-symbols-outlined">{art.icon}</span>
                    </div>
                    <p className="text-slate-900 dark:text-white font-medium flex-1">{art.title}</p>
                    <span className="material-symbols-outlined text-slate-400 group-hover:text-primary group-hover:translate-x-1 transition-all">chevron_right</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Contact Support Section */}
            <div className="bg-slate-900 dark:bg-slate-800 rounded-2xl p-8 text-center text-white mt-8 animate-fade-in-up shadow-glow">
              <h3 className="text-2xl font-bold mb-3">Still need help?</h3>
              <p className="text-slate-300 mb-6 max-w-xl mx-auto">Our specialized AI support team is available 24/7 to help you scale your store's creative output.</p>
              <div className="flex flex-wrap justify-center gap-4">
                <button 
                  onClick={() => setIsChatOpen(true)}
                  className="bg-primary hover:bg-secondary text-slate-900 px-6 py-3 rounded-xl font-bold shadow-lg transition-all active:scale-95"
                >
                  Start Live Chat
                </button>
                <button 
                  onClick={() => handleAction('Open Email Support')}
                  className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-xl font-bold border border-white/20 transition-all active:scale-95"
                >
                  Email Support
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Widget */}
      {isChatOpen && (
        <div 
          className={`fixed bottom-6 right-6 z-50 flex flex-col w-[360px] md:w-[400px] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden border border-slate-200 dark:border-slate-700 font-display transition-all duration-500 ease-in-out ${isMinimized ? 'h-[72px]' : 'h-[600px]'}`}
        >
          {/* Chat Header */}
          <div 
            onClick={() => isMinimized && setIsMinimized(false)}
            className={`bg-primary p-4 flex items-center justify-between shrink-0 shadow-md relative z-10 transition-colors ${isMinimized ? 'cursor-pointer hover:bg-secondary' : ''}`}
          >
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="size-10 rounded-full bg-white/30 overflow-hidden border-2 border-white/50 shadow-sm">
                  <img className="w-full h-full object-cover" alt="Sarah Support Agent" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAC1wj_lD4dflpDCPkfo79ZQuwdF3wBHLJr9DiSsraJuQQF47F3K4_vqVJ_TJL4qJxeqrcAgk1etx1olf3U2qPq-ixt-UqilYpDZHOsFb-sFD_Bl8La_3qDrJi5vDrUaFnwAyfR5VjneuwusLDpWUkLElXmACIsfUQur5-UIuLgU-gZIST1yEhSdmG7p_2S9fywSFKpoUomD86PnXuLXCHNEl3Bj3H40MRLFqJt1EA4zewGv7WVZGfpfZtBv-Dg-GkvPGDRB32k7Qs" />
                </div>
                <div className="absolute bottom-0 right-0 size-3 bg-green-500 border-2 border-primary rounded-full"></div>
              </div>
              <div className="flex flex-col">
                <h4 className="text-slate-900 text-base font-extrabold leading-tight">Sarah from Support</h4>
                <div className="flex items-center gap-1">
                  <span className="size-1.5 rounded-full bg-slate-900/40 animate-pulse"></span>
                  <span className="text-slate-900/60 text-xs font-bold">Online</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button 
                onClick={(e) => { e.stopPropagation(); setIsMinimized(!isMinimized); }}
                className="text-slate-900/60 hover:text-slate-900 hover:bg-white/20 rounded-full p-1.5 transition-all"
                title={isMinimized ? "Expand Chat" : "Minimize Chat"}
              >
                <span className="material-symbols-outlined text-[24px]">{isMinimized ? 'keyboard_arrow_up' : 'remove'}</span>
              </button>
              <button 
                onClick={(e) => { e.stopPropagation(); setIsChatOpen(false); }}
                className="text-slate-900/60 hover:text-slate-900 hover:bg-white/20 rounded-full p-1.5 transition-all"
                title="Close Chat"
              >
                <span className="material-symbols-outlined text-[24px]">close</span>
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages Area */}
              <div className="flex-1 bg-white dark:bg-slate-900 overflow-y-auto p-4 flex flex-col gap-4 relative sidebar-scroll">
                <div className="flex justify-center my-2">
                  <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest bg-slate-50 dark:bg-slate-800 px-3 py-1 rounded-full shadow-sm">Today</span>
                </div>
                
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex gap-3 max-w-[90%] ${msg.role === 'user' ? 'self-end flex-row-reverse' : ''}`}>
                    {msg.role === 'model' && (
                      <div className="size-8 rounded-full bg-slate-100 dark:bg-slate-800 shrink-0 overflow-hidden self-end mb-1 border border-slate-200 dark:border-slate-700">
                        <img className="w-full h-full object-cover" alt="Sarah Avatar" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAC1wj_lD4dflpDCPkfo79ZQuwdF3wBHLJr9DiSsraJuQQF47F3K4_vqVJ_TJL4qJxeqrcAgk1etx1olf3U2qPq-ixt-UqilYpDZHOsFb-sFD_Bl8La_3qDrJi5vDrUaFnwAyfR5VjneuwusLDpWUkLElXmACIsfUQur5-UIuLgU-gZIST1yEhSdmG7p_2S9fywSFKpoUomD86PnXuLXCHNEl3Bj3H40MRLFqJt1EA4zewGv7WVZGfpfZtBv-Dg-GkvPGDRB32k7Qs" />
                      </div>
                    )}
                    <div className={`flex flex-col gap-1 ${msg.role === 'user' ? 'items-end' : ''}`}>
                      <div className={`p-4 rounded-2xl shadow-sm transition-all ${msg.role === 'user' ? 'bg-primary text-slate-900 rounded-br-none font-medium' : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-bl-none'}`}>
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                      </div>
                      <span className={`text-[10px] text-slate-400 dark:text-slate-500 font-bold ${msg.role === 'user' ? 'mr-1' : 'ml-1'}`}>{msg.time}</span>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex gap-3 max-w-[85%] animate-pulse">
                    <div className="size-8 rounded-full bg-slate-100 dark:bg-slate-800 shrink-0 overflow-hidden self-end mb-1 border border-slate-200 dark:border-slate-700">
                      <img className="w-full h-full object-cover" alt="Sarah Typing" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAC1wj_lD4dflpDCPkfo79ZQuwdF3wBHLJr9DiSsraJuQQF47F3K4_vqVJ_TJL4qJxeqrcAgk1etx1olf3U2qPq-ixt-UqilYpDZHOsFb-sFD_Bl8La_3qDrJi5vDrUaFnwAyfR5VjneuwusLDpWUkLElXmACIsfUQur5-UIuLgU-gZIST1yEhSdmG7p_2S9fywSFKpoUomD86PnXuLXCHNEl3Bj3H40MRLFqJt1EA4zewGv7WVZGfpfZtBv-Dg-GkvPGDRB32k7Qs" />
                    </div>
                    <div className="bg-slate-100 dark:bg-slate-800 p-4 rounded-2xl rounded-bl-none shadow-sm flex gap-1.5 items-center">
                      <span className="size-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                      <span className="size-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                      <span className="size-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Action Suggestion Pills */}
              <div className="flex gap-2 overflow-x-auto no-scrollbar pb-3 px-4 pt-2 bg-white dark:bg-slate-900 border-t border-slate-50 dark:border-slate-800/50">
                {["Billing Issue", "Image Help", "Export Video", "API Access"].map((suggest, i) => (
                  <button 
                    key={i}
                    onClick={() => sendMessage(suggest)}
                    className="whitespace-nowrap px-4 py-2 rounded-full border border-primary/30 bg-primary/5 text-primary-dark text-xs font-bold hover:bg-primary hover:text-white transition-all shadow-sm active:scale-95"
                  >
                    {suggest}
                  </button>
                ))}
              </div>

              {/* Message Input Container */}
              <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800 shrink-0">
                <div className="relative flex items-center bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl px-2 py-1.5 focus-within:ring-2 focus-within:ring-primary focus-within:border-transparent transition-all shadow-inner">
                  <button 
                    onClick={() => handleAction('Attach File to Chat')}
                    className="p-2 text-slate-400 hover:text-primary transition-colors rounded-xl hover:bg-white dark:hover:bg-slate-700"
                    title="Attach File"
                  >
                    <span className="material-symbols-outlined text-[22px] rotate-45">attach_file</span>
                  </button>
                  <input 
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage(inputValue)}
                    className="flex-1 bg-transparent border-none focus:ring-0 text-sm text-slate-800 dark:text-slate-200 placeholder:text-slate-400 px-2 h-10" 
                    placeholder="Ask Sarah anything..." 
                    type="text"
                  />
                  <button 
                    onClick={() => handleAction('Open Emoji Picker')}
                    className="p-2 text-slate-400 hover:text-yellow-500 transition-colors rounded-xl hover:bg-white dark:hover:bg-slate-700 mr-1"
                    title="Emojis"
                  >
                    <span className="material-symbols-outlined text-[22px]">sentiment_satisfied</span>
                  </button>
                  <button 
                    onClick={() => sendMessage(inputValue)}
                    disabled={!inputValue.trim()}
                    className={`size-10 rounded-xl flex items-center justify-center text-slate-900 transition-all shadow-md ${inputValue.trim() ? 'bg-primary hover:bg-secondary hover:shadow-glow' : 'bg-slate-200 dark:bg-slate-700 text-slate-400 cursor-not-allowed'}`}
                    title="Send Message"
                  >
                    <span className="material-symbols-outlined text-[20px] ml-0.5" style={{ fontVariationSettings: "'FILL' 1" }}>send</span>
                  </button>
                </div>
                <div className="flex justify-center mt-3">
                  <p className="text-[10px] text-slate-400 dark:text-slate-600 flex items-center gap-1 font-bold uppercase tracking-widest">
                    CommerceAI Support <span className="text-primary">•</span> 24/7 Support
                  </p>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Reopen Chat Button (Floating Action Button) */}
      {!isChatOpen && (
        <button 
          onClick={() => { setIsChatOpen(true); setIsMinimized(false); }}
          className="fixed bottom-8 right-8 z-50 group flex items-center gap-3 bg-primary hover:bg-secondary text-slate-900 pl-4 pr-6 py-4 rounded-2xl shadow-2xl transition-all transform hover:scale-105 active:scale-95 animate-fade-in-up"
        >
          <div className="relative">
            <span className="material-symbols-outlined text-3xl group-hover:rotate-12 transition-transform">chat</span>
            <span className="absolute -top-1 -right-1 size-3 bg-red-500 border-2 border-primary rounded-full animate-ping"></span>
            <span className="absolute -top-1 -right-1 size-3 bg-red-500 border-2 border-primary rounded-full"></span>
          </div>
          <span className="font-bold text-sm">Chat with Sarah</span>
        </button>
      )}
    </div>
  );
};

export default HelpSupport;
