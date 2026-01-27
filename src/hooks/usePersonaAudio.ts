import { useState, useRef, useCallback, useEffect } from 'react';

export interface AudioConfig {
    persona: string;
    voice: string;
}

export const usePersonaAudio = () => {
    // State
    const [isConnected, setIsConnected] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [inputVolume, setInputVolume] = useState(0);
    const [outputVolume, setOutputVolume] = useState(0);

    // Refs
    const audioContext = useRef<AudioContext | null>(null);
    const socket = useRef<WebSocket | null>(null);
    const workletNode = useRef<AudioWorkletNode | null>(null);
    const inputAnalyser = useRef<AnalyserNode | null>(null);
    const outputAnalyser = useRef<AnalyserNode | null>(null);
    const nextStartTime = useRef(0);
    const animationFrameId = useRef<number | null>(null);

    // --- AUDIO HELPERS ---

    const convertFloat32ToInt16 = (float32Array: Float32Array): Int16Array => {
        const int16Array = new Int16Array(float32Array.length);
        for (let i = 0; i < float32Array.length; i++) {
            let s = Math.max(-1, Math.min(1, float32Array[i]));
            int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return int16Array;
    };

    const playAudioChunk = (ctx: AudioContext, float32Data: Float32Array) => {
        const buffer = ctx.createBuffer(1, float32Data.length, 24000);
        buffer.getChannelData(0).set(float32Data);

        const source = ctx.createBufferSource();
        source.buffer = buffer;

        if (!outputAnalyser.current) {
            outputAnalyser.current = ctx.createAnalyser();
            outputAnalyser.current.fftSize = 64;
            outputAnalyser.current.connect(ctx.destination);
        }

        source.connect(outputAnalyser.current);

        const currentTime = ctx.currentTime;
        const startTime = Math.max(currentTime, nextStartTime.current);

        source.start(startTime);
        nextStartTime.current = startTime + buffer.duration;
    };

    const initAudio = async () => {
        try {
            // Requirement: Sample Rate 24000
            const ctx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });

            // Load Worklet
            await ctx.audioWorklet.addModule('/audio-processor.js');

            audioContext.current = ctx;
            return ctx;
        } catch (err) {
            console.error("Audio Init Error:", err);
            return null;
        }
    };

    // --- VISUALIZER LOOP ---

    const updateVisualizers = useCallback(() => {
        if (!isConnected) return;

        if (inputAnalyser.current) {
            const dataArray = new Uint8Array(inputAnalyser.current.frequencyBinCount);
            inputAnalyser.current.getByteFrequencyData(dataArray);
            const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
            setInputVolume(avg);
        }

        if (outputAnalyser.current) {
            const dataArray = new Uint8Array(outputAnalyser.current.frequencyBinCount);
            outputAnalyser.current.getByteFrequencyData(dataArray);
            const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
            setOutputVolume(avg);
        }

        animationFrameId.current = requestAnimationFrame(updateVisualizers);
    }, [isConnected]);

    // Start/Stop loop based on connection
    useEffect(() => {
        if (isConnected) {
            animationFrameId.current = requestAnimationFrame(updateVisualizers);
        } else {
            if (animationFrameId.current) {
                cancelAnimationFrame(animationFrameId.current);
            }
            setInputVolume(0);
            setOutputVolume(0);
        }
        return () => {
            if (animationFrameId.current) cancelAnimationFrame(animationFrameId.current);
        };
    }, [isConnected, updateVisualizers]);


    // --- MAIN API ---

    const connect = async (url: string, config: AudioConfig) => {
        if (isConnected) return;

        const ctx = await initAudio();
        if (!ctx) return;

        const ws = new WebSocket(url);

        ws.onopen = () => {
            console.log("Connected to PersonaPlex Backend");
            setIsConnected(true);

            ws.send(JSON.stringify({
                type: 'config',
                persona: config.persona,
                voice: config.voice
            }));
        };

        ws.onmessage = async (event) => {
            if (event.data instanceof Blob) {
                const arrayBuffer = await event.data.arrayBuffer();
                const float32Data = new Float32Array(arrayBuffer);
                playAudioChunk(ctx, float32Data);
            } else {
                try {
                    const data = JSON.parse(event.data);
                    console.log("Server Msg:", data);
                } catch (e) { }
            }
        };

        ws.onclose = () => {
            console.log("Disconnected");
            handleDisconnect();
        };

        ws.onerror = (e) => {
            console.error("WebSocket Error:", e);
            handleDisconnect();
        }

        socket.current = ws;
    };

    const handleDisconnect = () => {
        setIsConnected(false);
        setIsRecording(false);
        stopMic();

        socket.current?.close();
        socket.current = null;

        audioContext.current?.close();
        audioContext.current = null;

        outputAnalyser.current = null;
        inputAnalyser.current = null;
    };

    const disconnect = () => {
        handleDisconnect();
    };

    const startMic = async () => {
        if (!audioContext.current || !socket.current) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    channelCount: 1
                }
            });

            const source = audioContext.current.createMediaStreamSource(stream);

            inputAnalyser.current = audioContext.current.createAnalyser();
            inputAnalyser.current.fftSize = 64;
            source.connect(inputAnalyser.current);

            workletNode.current = new AudioWorkletNode(audioContext.current, 'audio-processor');
            source.connect(workletNode.current);

            workletNode.current.port.onmessage = (event) => {
                if (socket.current?.readyState === WebSocket.OPEN) {
                    const pcmData = event.data;
                    const int16Data = convertFloat32ToInt16(pcmData);
                    socket.current.send(int16Data);
                }
            };

            setIsRecording(true);

        } catch (err) {
            console.error("Mic Error:", err);
            alert("Microphone access denied.");
        }
    };

    const stopMic = () => {
        if (workletNode.current) {
            workletNode.current.disconnect();
            workletNode.current = null;
        }
        setIsRecording(false);
    };

    return {
        isConnected,
        isRecording,
        inputVolume,
        outputVolume,
        connect,
        disconnect,
        startMic,
        stopMic
    };
};
