import React from 'react';
import { Radio, Mic, MicOff } from 'lucide-react';

interface VisualizerStageProps {
    isConnected: boolean;
    isRecording: boolean;
    inputVolume: number;
    outputVolume: number;
    toggleMic: () => void;
}

export const VisualizerStage: React.FC<VisualizerStageProps> = ({
    isConnected,
    isRecording,
    inputVolume,
    outputVolume,
    toggleMic
}) => {
    return (
        <div className="w-full max-w-2xl mt-8">
            <div className={`relative bg-slate-800 rounded-2xl p-8 border ${isConnected ? 'border-green-500/30' : 'border-slate-700'} transition-all duration-500 flex flex-col items-center justify-center min-h-[300px]`}>

                {/* Status Overlay */}
                {!isConnected && (
                    <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm z-10 flex items-center justify-center rounded-2xl">
                        <p className="text-slate-400 flex items-center gap-2">
                            <Radio className="animate-ping w-4 h-4 text-slate-500" />
                            Waiting for Uplink...
                        </p>
                    </div>
                )}

                {/* VISUALIZER RINGS */}
                <div className="relative w-48 h-48 flex items-center justify-center mb-8">
                    {/* Output Ring (AI) */}
                    <div
                        className="absolute inset-0 rounded-full border-4 border-blue-500 transition-all duration-75 ease-linear opacity-80"
                        style={{ transform: `scale(${1 + (outputVolume / 255) * 0.5})` }}
                    />
                    <div className="absolute inset-0 rounded-full bg-blue-500/20 blur-xl" style={{ opacity: outputVolume / 255 }} />

                    {/* Input Ring (User) */}
                    <div
                        className="absolute w-32 h-32 rounded-full border-4 border-green-500 transition-all duration-75 ease-linear z-20"
                        style={{ transform: `scale(${1 + (inputVolume / 255) * 0.4})` }}
                    />
                    <div className="absolute w-32 h-32 rounded-full bg-green-500/20 blur-lg z-20" style={{ opacity: inputVolume / 255 }} />
                </div>

                {/* CONTROLS */}
                <div className="flex gap-6 z-20">
                    <button
                        disabled={!isConnected}
                        onClick={toggleMic}
                        className={`p-6 rounded-full transition-all duration-300 transform hover:scale-105 shadow-2xl ${isRecording
                            ? 'bg-green-500 hover:bg-green-600 text-white shadow-green-500/30'
                            : 'bg-red-500 hover:bg-red-600 text-white shadow-red-500/30'
                            } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                        {isRecording ? <Mic className="w-8 h-8" /> : <MicOff className="w-8 h-8" />}
                    </button>
                </div>

                <p className="mt-6 text-slate-400 text-sm font-mono">
                    {isRecording ? "MICROPHONE ACTIVE // DUPLEX OPEN" : "MICROPHONE MUTED"}
                </p>

            </div>
        </div>
    );
};
