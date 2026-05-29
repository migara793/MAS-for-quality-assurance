import React, { useState, useEffect, useRef } from 'react';
import { Play, Activity, Settings, Terminal, Shield, CheckCircle, AlertCircle, Cpu } from 'lucide-react';

function App() {
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState('Idle');
  const [request, setRequest] = useState('');
  const [activeAgent, setActiveAgent] = useState(null);
  const [agents, setAgents] = useState([]);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const fetchAgents = async () => {
    try {
      const response = await fetch('/agents');
      const data = await response.json();
      setAgents(data.agents);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    }
  };

  const runPipeline = async () => {
    if (!request) return;
    setStatus('Running');
    setLogs(prev => [...prev, { type: 'system', message: `🚀 Triggering pipeline: ${request}`, time: new Date().toLocaleTimeString() }]);
    
    try {
      const response = await fetch('/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request })
      });
      const data = await response.json();
      setLogs(prev => [...prev, { type: 'success', message: data.status, time: new Date().toLocaleTimeString() }]);
    } catch (error) {
      setLogs(prev => [...prev, { type: 'error', message: 'Failed to connect to backend', time: new Date().toLocaleTimeString() }]);
      setStatus('Error');
    }
  };

  useEffect(() => {
    fetchAgents();
    const es = new EventSource('/events');
    es.onmessage = (e) => {
      const event = JSON.parse(e.data);
      const time = new Date().toLocaleTimeString();
      
      if (event.type === 'agent') {
        const match = event.message.match(/\[(.*?)\]/);
        if (match) {
          setActiveAgent(match[1].trim());
        }
      }
      
      if (event.message.includes('🏁 PIPELINE COMPLETED')) {
        setStatus('Idle');
        setActiveAgent(null);
      }
      
      if (event.message.includes('🚀 PIPELINE TRIGGERED:')) {
        setStatus('Running');
        setLogs([]);
      }
      
      setLogs(prev => [...prev, { ...event, time }]);
    };
    return () => es.close();
  }, []);

  return (
    <div className="min-h-screen flex flex-col font-sans">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Cpu size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">MAS QA Monitor</h1>
            <p className="text-xs text-gray-400 uppercase tracking-widest font-semibold">Real-time Agent Orchestration</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1 bg-gray-900 rounded-full border border-gray-700">
            <div className={`w-2 h-2 rounded-full ${status === 'Running' ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
            <span className="text-sm font-medium">{status}</span>
          </div>
          <button className="text-gray-400 hover:text-white transition-colors">
            <Settings size={20} />
          </button>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: Controls */}
        <div className="w-80 bg-gray-800/50 border-r border-gray-700 p-6 flex flex-col gap-8">
          <section>
            <label className="text-xs font-bold text-gray-500 uppercase mb-3 block">Trigger Pipeline</label>
            <textarea 
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all resize-none h-32"
              placeholder="Describe the QA task..."
            />
            <button 
              onClick={runPipeline}
              disabled={status === 'Running'}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 py-3 rounded-lg font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-900/20"
            >
              <Play size={18} fill="currentColor" />
              Start Pipeline
            </button>
          </section>

          <section className="flex-1 overflow-y-auto">
            <label className="text-xs font-bold text-gray-500 uppercase mb-3 block">Agent Swarm</label>
            <div className="space-y-3">
              {agents.map(agent => {
                const isActive = activeAgent === agent.name || (agent.role === 'Root' && status === 'Running' && !activeAgent);
                return (
                  <div key={agent.name} className={`p-3 rounded-lg border transition-all ${isActive ? 'bg-blue-900/20 border-blue-500' : 'bg-gray-900/50 border-gray-700'}`}>
                    <div className="flex justify-between items-center">
                      <span className={`text-sm font-bold ${isActive ? 'text-blue-400' : 'text-gray-300'}`}>{agent.name}</span>
                      <span className="text-[10px] bg-gray-800 px-2 py-0.5 rounded uppercase font-bold text-gray-500">{agent.role}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </div>

        {/* Right Content: Real-time Terminal */}
        <div className="flex-1 flex flex-col bg-gray-950 relative">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-50"></div>
          
          <div className="flex items-center justify-between p-4 border-b border-gray-800/50 bg-gray-900/30">
            <div className="flex items-center gap-2 text-gray-400">
              <Terminal size={16} />
              <span className="text-xs font-mono font-bold uppercase tracking-wider">Live Pipeline Output</span>
            </div>
            <button 
              onClick={() => setLogs([])}
              className="text-[10px] uppercase font-bold text-gray-500 hover:text-gray-300 transition-colors"
            >
              Clear Console
            </button>
          </div>

          <div 
            ref={scrollRef}
            className="flex-1 p-6 font-mono text-sm overflow-y-auto space-y-2 selection:bg-blue-500/30"
          >
            {logs.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-gray-600 gap-4">
                <Terminal size={48} strokeWidth={1} />
                <p className="font-sans italic">Awaiting pipeline initialization...</p>
              </div>
            )}
            {logs.map((log, i) => (
              <div key={i} className="flex gap-4 group animate-in fade-in slide-in-from-left-2 duration-300">
                <span className="text-gray-600 shrink-0 select-none">[{log.time}]</span>
                <span className={`
                  ${log.type === 'system' ? 'text-blue-400 font-bold' : ''}
                  ${log.type === 'success' ? 'text-green-400' : ''}
                  ${log.type === 'error' ? 'text-red-400 font-bold' : ''}
                  ${log.type === 'tool' ? 'text-purple-400' : ''}
                  ${!log.type ? 'text-gray-300' : ''}
                `}>
                  {log.message}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
