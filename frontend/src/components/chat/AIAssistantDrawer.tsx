import React, { useEffect, useRef, useState } from 'react';
import {
  X,
  Send,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Bot,
  User,
  Sparkles,
  Wrench,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';
import { api } from '../../services/api';
import { ChatMessage } from '../../types';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';

interface AIAssistantDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onDataChanged?: () => void;
}

export const AIAssistantDrawer: React.FC<AIAssistantDrawerProps> = ({
  isOpen,
  onClose,
  onDataChanged,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      content:
        "Hello! I am your AI Life Manager powered by FastMCP. You can speak or type naturally to record expenses, inspect financial analytics, schedule reminders, plan your day, or check the weather.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { speak, isSpeaking, isMuted, toggleMute } = useSpeechSynthesis();

  const handleSpeechResult = (spokenText: string) => {
    if (spokenText.trim()) {
      handleSend(spokenText);
    }
  };

  const {
    isListening,
    interimTranscript,
    startListening,
    stopListening,
    isSupported: isSpeechSupported,
    error: speechError,
  } = useSpeechRecognition(handleSpeechResult);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    const userMsg: ChatMessage = {
      id: String(Date.now()),
      sender: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Map prior conversation history for contextual multi-turn
      const history = messages
        .filter((m) => m.id !== 'welcome')
        .slice(-6)
        .map((m) => ({
          role: m.sender === 'user' ? 'user' : 'assistant',
          content: m.content,
        }));

      const result = await api.sendChatMessage(text, history);

      const assistantMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: 'assistant',
        content: result.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        tools_called: result.tools_called,
        used_fallback: result.used_fallback,
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // Speak response aloud if TTS is enabled
      speak(result.response);

      // Trigger dashboard data refresh if a tool was executed
      if (result.tools_called && result.tools_called.length > 0 && onDataChanged) {
        onDataChanged();
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: String(Date.now() + 1),
          sender: 'assistant',
          content: `Sorry, an error occurred: ${err.message || 'Could not process request'}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const samplePrompts = [
    'I spent ₹250 on food today',
    'How much did I spend this week?',
    'Compare my spending with last week',
    'Which category am I spending the most on?',
    'Plan my day',
    'Remind me to submit assignment tomorrow at 6 PM',
    'Do I need an umbrella today?',
    'How much can I safely spend this week?',
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-sm flex justify-end transition-opacity">
      <div className="w-full max-w-lg bg-white dark:bg-slate-900 h-full shadow-2xl flex flex-col border-l border-slate-200 dark:border-slate-800 animate-in slide-in-from-right duration-300">
        {/* Drawer Header */}
        <div className="p-4 px-6 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/50">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">AI Life Assistant</h3>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  FastMCP Online
                </span>
              </div>
              <p className="text-[11px] text-slate-500">Autonomous tool caller & memory</p>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={toggleMute}
              className={`p-2 rounded-lg text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors ${
                !isMuted ? 'text-brand-600 dark:text-brand-400' : ''
              }`}
              title={isMuted ? 'Enable Voice Responses' : 'Mute Voice Responses'}
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Messages List */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-50/30 dark:bg-slate-950/40">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 ${
                msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-xs font-bold shadow-sm ${
                  msg.sender === 'user'
                    ? 'bg-brand-600 text-white'
                    : 'bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800'
                }`}
              >
                {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`max-w-[82%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
                  msg.sender === 'user'
                    ? 'bg-brand-600 text-white rounded-tr-none'
                    : 'bg-white dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 text-slate-800 dark:text-slate-100 rounded-tl-none'
                }`}
              >
                <div className="whitespace-pre-line leading-relaxed">{msg.content}</div>

                {/* Tool execution badge tags */}
                {msg.tools_called && msg.tools_called.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-slate-100 dark:border-slate-700/60 flex flex-wrap gap-1.5 items-center">
                    <span className="text-[10px] font-semibold text-slate-400 flex items-center gap-1">
                      <Wrench className="w-3 h-3 text-brand-500" /> FastMCP Tools:
                    </span>
                    {msg.tools_called.map((tool, idx) => (
                      <span
                        key={idx}
                        className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 border border-brand-200/60 dark:border-brand-800/60 font-medium"
                      >
                        {tool}
                      </span>
                    ))}
                  </div>
                )}

                <span
                  className={`block text-[10px] mt-1.5 text-right ${
                    msg.sender === 'user' ? 'text-brand-200' : 'text-slate-400'
                  }`}
                >
                  {msg.timestamp}
                </span>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-4 h-4 animate-spin text-brand-600" />
              </div>
              <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl rounded-tl-none px-4 py-3 text-xs text-slate-500 flex items-center space-x-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Executing FastMCP tool & generating response...</span>
              </div>
            </div>
          )}

          {isListening && (
            <div className="p-3 rounded-xl bg-brand-500/10 border border-brand-500/30 flex items-center justify-between text-brand-600 dark:text-brand-400 text-xs voice-pulsing">
              <div className="flex items-center space-x-2">
                <Mic className="w-4 h-4 animate-bounce" />
                <span>Listening to voice... {interimTranscript && `"${interimTranscript}"`}</span>
              </div>
              <button
                onClick={stopListening}
                className="text-[10px] font-bold uppercase underline hover:text-brand-800"
              >
                Stop
              </button>
            </div>
          )}

          {speechError && (
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{speechError}</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Quick Prompt Chips */}
        <div className="p-3 px-6 border-t border-slate-100 dark:border-slate-800/80 bg-white dark:bg-slate-900">
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Try saying:</p>
          <div className="flex overflow-x-auto pb-1 gap-1.5 no-scrollbar">
            {samplePrompts.slice(0, 4).map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(prompt)}
                className="flex-shrink-0 text-xs px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-brand-950/40 hover:text-brand-600 dark:hover:text-brand-300 text-slate-600 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700/80 transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <div className="p-4 px-6 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center space-x-2">
          {isSpeechSupported && (
            <button
              onClick={isListening ? stopListening : startListening}
              className={`p-2.5 rounded-xl transition-all ${
                isListening
                  ? 'bg-rose-500 text-white voice-pulsing'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-brand-50 hover:text-brand-600'
              }`}
              title={isListening ? 'Stop listening' : 'Start speaking'}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
          )}

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type a command (e.g. 'I spent ₹250 on food', 'Plan my day')..."
            className="flex-1 px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:ring-2 focus:ring-brand-500 focus:outline-none"
          />

          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            className="p-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white shadow-md shadow-brand-500/20 transition-transform active:scale-95"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
