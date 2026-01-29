import React, { useRef, useState } from 'react';
import { Settings, Volume2, ChevronDown } from 'lucide-react';

// Persona presets matching NVIDIA's documented prompting format
const PERSONA_PRESETS = [
    {
        name: "Custom",
        prompt: "",
        description: "Write your own prompt"
    },
    {
        name: "Friendly Teacher",
        prompt: "You are a wise and friendly teacher. Answer questions or provide advice in a clear and engaging way.",
        description: "NVIDIA's default assistant role"
    },
    {
        name: "Casual Conversation",
        prompt: "You enjoy having a good conversation.",
        description: "Open-ended natural chat"
    },
    {
        name: "Restaurant Service",
        prompt: "You work for Golden Dragon which is a restaurant and your name is Sam. Information: Today's special is Kung Pao Chicken ($12.50). Appetizers include spring rolls ($5) and hot and sour soup ($4). Open until 10 PM for dine-in and takeout.",
        description: "Restaurant customer service"
    },
    {
        name: "Tech Support",
        prompt: "You work for TechHelp Solutions which is a tech support company and your name is Alex. Information: Common issues include password resets, software installation, and connectivity problems. Support hours are 8 AM to 8 PM.",
        description: "Technical support agent"
    },
    {
        name: "Astronaut Crisis",
        prompt: "You enjoy having a good conversation. Have a technical discussion about fixing a reactor core on a spaceship to Mars. You are an astronaut on a Mars mission. Your name is Alex. You are already dealing with a reactor core meltdown. Several ship systems are failing. You explain what is happening and urgently ask for help.",
        description: "NVIDIA's demo scenario"
    },
    {
        name: "Cooking Discussion",
        prompt: "You enjoy having a good conversation. Have a casual conversation about favorite foods and cooking experiences. You enjoy cooking diverse international dishes and appreciate many ethnic restaurants.",
        description: "Casual cooking chat"
    },
];

// Voice options using NVIDIA's official naming
const VOICE_OPTIONS = [
    {
        group: "Natural (Female)", voices: [
            { id: "NATF0", name: "NATF0" },
            { id: "NATF1", name: "NATF1" },
            { id: "NATF2", name: "NATF2" },
            { id: "NATF3", name: "NATF3" },
        ]
    },
    {
        group: "Natural (Male)", voices: [
            { id: "NATM0", name: "NATM0" },
            { id: "NATM1", name: "NATM1" },
            { id: "NATM2", name: "NATM2" },
            { id: "NATM3", name: "NATM3" },
        ]
    },
    {
        group: "Variety (Female)", voices: [
            { id: "VARF0", name: "VARF0" },
            { id: "VARF1", name: "VARF1" },
            { id: "VARF2", name: "VARF2" },
            { id: "VARF3", name: "VARF3" },
            { id: "VARF4", name: "VARF4" },
        ]
    },
    {
        group: "Variety (Male)", voices: [
            { id: "VARM0", name: "VARM0" },
            { id: "VARM1", name: "VARM1" },
            { id: "VARM2", name: "VARM2" },
            { id: "VARM3", name: "VARM3" },
            { id: "VARM4", name: "VARM4" },
        ]
    },
];

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
    const audioRef = useRef<HTMLAudioElement>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [selectedPreset, setSelectedPreset] = useState("Custom");

    const playVoicePreview = () => {
        if (audioRef.current) {
            audioRef.current.src = `/voice-samples/${voiceId}.wav`;
            audioRef.current.play();
            setIsPlaying(true);
        }
    };

    const handlePresetChange = (presetName: string) => {
        setSelectedPreset(presetName);
        const preset = PERSONA_PRESETS.find(p => p.name === presetName);
        if (preset && preset.prompt) {
            setPersona(preset.prompt);
        }
    };

    return (
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
                <Settings className="w-5 h-5 text-purple-400" />
                Configuration
            </h2>

            <div className="space-y-4">
                {/* Persona Preset Selector */}
                <div>
                    <label className="text-xs text-slate-400 uppercase tracking-wider">Persona Preset</label>
                    <select
                        value={selectedPreset}
                        onChange={(e) => handlePresetChange(e.target.value)}
                        disabled={isConnected}
                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 mt-1 text-sm focus:outline-none focus:border-purple-500"
                    >
                        {PERSONA_PRESETS.map(preset => (
                            <option key={preset.name} value={preset.name}>
                                {preset.name} {preset.description && `- ${preset.description}`}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Custom Persona Prompt */}
                <div>
                    <label className="text-xs text-slate-400 uppercase tracking-wider">System Prompt</label>
                    <textarea
                        value={persona}
                        onChange={(e) => {
                            setPersona(e.target.value);
                            setSelectedPreset("Custom");
                        }}
                        disabled={isConnected}
                        placeholder="Describe your AI's personality, role, and behavior..."
                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 mt-1 h-24 text-sm focus:outline-none focus:border-purple-500 transition-colors resize-none"
                    />
                </div>

                {/* Voice Selection with Preview */}
                <div>
                    <label className="text-xs text-slate-400 uppercase tracking-wider">Voice</label>
                    <div className="flex gap-2 mt-1">
                        <select
                            value={voiceId}
                            onChange={(e) => setVoiceId(e.target.value)}
                            disabled={isConnected}
                            className="flex-1 bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-purple-500"
                        >
                            {VOICE_OPTIONS.map(group => (
                                <optgroup key={group.group} label={group.group}>
                                    {group.voices.map(voice => (
                                        <option key={voice.id} value={voice.id}>
                                            {voice.name}
                                        </option>
                                    ))}
                                </optgroup>
                            ))}
                        </select>
                        <button
                            onClick={playVoicePreview}
                            disabled={isPlaying}
                            className="px-3 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-600 rounded text-sm font-medium transition-colors flex items-center gap-1"
                            title="Preview voice"
                        >
                            <Volume2 className="w-4 h-4" />
                        </button>
                    </div>
                    <audio
                        ref={audioRef}
                        onEnded={() => setIsPlaying(false)}
                        className="hidden"
                    />
                </div>
            </div>
        </div>
    );
};
