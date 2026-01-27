import { useState } from 'react';
import { usePersonaAudio } from './hooks/usePersonaAudio';
import { ConnectionCard } from './components/ConnectionCard';
import { SettingsCard } from './components/SettingsCard';
import { VisualizerStage } from './components/VisualizerStage';

function App() {
    // Local UI State
    const [serverUrl, setServerUrl] = useState('ws://localhost:8000/ws');
    const [persona, setPersona] = useState("You are a helpful, witty AI assistant named Plex.");
    const [voiceId, setVoiceId] = useState("natural_female_1");

    // Audio Hook
    const {
        isConnected,
        isRecording,
        inputVolume,
        outputVolume,
        connect,
        disconnect,
        startMic,
        stopMic
    } = usePersonaAudio();

    const handleToggleConnection = () => {
        if (isConnected) {
            disconnect();
        } else {
            connect(serverUrl, { persona, voice });
        }
    };

    // Aliasing voiceId to voice for the hook config, ensuring type safety
    const voice = voiceId;

    const handleToggleMic = () => {
        if (isRecording) {
            stopMic();
        } else {
            startMic();
        }
    };

    return (
        <div className="min-h-screen bg-slate-900 text-slate-100 font-sans p-6 flex flex-col items-center">

            {/* HEADER */}
            <div className="w-full max-w-2xl mb-12 flex justify-between items-center border-b border-slate-700 pb-4">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
                        PersonaPlex Node
                    </h1>
                    <p className="text-slate-400 text-sm">Full-Duplex Speech Interface</p>
                </div>
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono ${isConnected ? 'bg-green-900/50 text-green-400 border border-green-800' : 'bg-red-900/50 text-red-400 border border-red-800'}`}>
                    <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                    {isConnected ? 'SYSTEM ONLINE' : 'DISCONNECTED'}
                </div>
            </div>

            {/* MAIN CONTROL PANEL */}
            <div className="w-full max-w-2xl grid grid-cols-1 md:grid-cols-2 gap-6">
                <ConnectionCard
                    serverUrl={serverUrl}
                    setServerUrl={setServerUrl}
                    isConnected={isConnected}
                    toggleConnection={handleToggleConnection}
                />

                <SettingsCard
                    persona={persona}
                    setPersona={setPersona}
                    voiceId={voiceId}
                    setVoiceId={setVoiceId}
                    isConnected={isConnected}
                />
            </div>

            {/* VISUALIZER STAGE */}
            <VisualizerStage
                isConnected={isConnected}
                isRecording={isRecording}
                inputVolume={inputVolume}
                outputVolume={outputVolume}
                toggleMic={handleToggleMic}
            />

        </div>
    );
}

export default App;
