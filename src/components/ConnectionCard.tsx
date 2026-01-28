import React from 'react';
import { Server } from 'lucide-react';

interface ConnectionCardProps {
    serverUrl: string;
    setServerUrl: (url: string) => void;
    isConnected: boolean;
    toggleConnection: () => void;
    error: string | null;
}

export const ConnectionCard: React.FC<ConnectionCardProps> = ({
    serverUrl,
    setServerUrl,
    isConnected,
    toggleConnection,
    error
}) => {
    return (
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
                <Server className="w-5 h-5 text-blue-400" />
                Connection
            </h2>

            <div className="space-y-4">
                <div>
                    <label className="text-xs text-slate-400 uppercase tracking-wider">WebSocket URL</label>
                    <input
                        type="text"
                        value={serverUrl}
                        onChange={(e) => setServerUrl(e.target.value)}
                        disabled={isConnected}
                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 mt-1 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                </div>

                <button
                    onClick={toggleConnection}
                    className={`w-full py-3 rounded-lg font-bold transition-all ${isConnected
                        ? 'bg-red-600 hover:bg-red-700 text-white'
                        : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-900/50'
                        }`}
                >
                    {isConnected ? 'Terminate Link' : 'Initialize Connection'}
                </button>
            </div>

            {
                error && (
                    <div className="mt-4 p-3 bg-red-900/50 border border-red-700/50 rounded-lg text-red-200 text-xs text-center">
                        {error}
                    </div>
                )
            }
        </div >
    );
};
