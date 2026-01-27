class AudioProcessor extends AudioWorkletProcessor {
    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input && input.length > 0) {
            const inputChannel = input[0];
            // Post raw float32 data to the main React thread
            this.port.postMessage(inputChannel);
        }
        return true;
    }
}
registerProcessor('audio-processor', AudioProcessor);
