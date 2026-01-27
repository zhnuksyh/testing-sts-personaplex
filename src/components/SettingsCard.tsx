import React from 'react';
import { Settings } from 'lucide-react';

interface SettingsCardProps {
    persona: string;
    setPersona: (persona: string) => void;
    voiceId: string;
    setVoiceId: (voiceId: string) => void;
    isConnected: boolean;
}

export const SettingsCard: React.FC<SettingsCardProps> = ({
    persona,
    setPersona,
    voiceId,
    setVoiceId,
    isConnected
}) => {
    return (
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
                <Settings className="w-5 h-5 text-purple-400" />
                Configuration
            </h2>

            <div className="space-y-4">
                <div>
                    <label className="text-xs text-slate-400 uppercase tracking-wider">Persona System Prompt</label>
                    <textarea
                        value={persona}
                        onChange={(e) => setPersona(e.target.value)}
                        disabled={isConnected}
                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 mt-1 h-20 text-sm focus:outline-none focus:border-purple-500 transition-colors resize-none"
                    />
                </div>

                <div className="flex gap-4">
                    <div className="flex-1">
                        <label className="text-xs text-slate-400 uppercase tracking-wider">Voice ID</label>
                        <select
                            value={voiceId}
                            onChange={(e) => setVoiceId(e.target.value)}
                            disabled={isConnected}
                            className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 mt-1 text-sm focus:outline-none focus:border-purple-500"
                        >
                            <option value="natural_female_1">Natural Female 1</option>
                            <option value="natural_male_1">Natural Male 1</option>
                            <option value="robot_1">Robot V1</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
    );
};
