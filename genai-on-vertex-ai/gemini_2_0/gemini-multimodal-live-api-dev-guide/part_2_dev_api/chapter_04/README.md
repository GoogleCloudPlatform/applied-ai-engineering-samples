# Gemini Text-to-Speech with WebSockets

This HTML file demonstrates a text-to-speech application using the Gemini API and WebSockets. It allows you to type a text message into an input field, send it to the Gemini model, and receive an audio response that is played back in the browser. The application uses the browser's built-in `WebSocket` and `AudioContext` APIs to handle real-time communication and audio playback.

This example focuses on demonstrating:

1. **Low-level interaction with the Gemini API using WebSockets.**
2. **Handling audio responses** from the API and playing them back in the browser.
3. **Managing user input** and displaying messages.
4. **Implementing audio chunk queuing and playback** with `AudioContext`.

## How it works

The application's functionality can be broken down into several key components:

### 1. Establishing a WebSocket Connection

*   **API Endpoint:** The application connects to the Gemini API using a specific WebSocket endpoint URL:
    ```
    wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key=${apiKey}
    ```
    This URL includes the API host, the service path, and an API key for authentication. Remember to replace `${apiKey}` with your actual API key.
*   **WebSocket Object:** A new `WebSocket` object is created in JavaScript, initiating the connection:
    ```javascript
    const ws = new WebSocket(endpoint);
    ```
*   **Event Handlers:** Event handlers are defined to manage the connection's lifecycle and handle incoming messages:
    *   `onopen`: Triggered when the connection is successfully opened.
    *   `onmessage`: Triggered when a message is received from the server.
    *   `onerror`: Triggered if an error occurs during the connection.
    *   `onclose`: Triggered when the connection is closed.

### 2. Sending a Setup Message

*   **`onopen` Handler:** When the `onopen` event is triggered, the application sends a setup message to the API.
*   **Setup Message Structure:** The setup message is a JSON object that configures the interaction:
    ```javascript
    const setupMessage = {
      setup: {
        model: "models/gemini-2.0-flash-exp",
        generation_config: {
          response_modalities: ["AUDIO"]
        }
      }
    };
    ```
    *   `model`: Specifies the Gemini model to use (`"models/gemini-2.0-flash-exp"` in this case).
    *   `generation_config`: Configures the generation parameters. Here, `response_modalities` is set to `["AUDIO"]` to request audio output.
*   **Sending the Message:** The setup message is stringified and sent to the server using `ws.send()`.
*   **Input Disabled:** Initially, the user input field and send button are disabled. They are only enabled after the setup is complete.

### 3. Receiving and Processing Messages

*   **`onmessage` Handler:** The `onmessage` event handler receives messages from the server.
*   **Handling Different Response Types:** The code handles either `Blob` or `JSON` data. It converts `Blob` data to text and parses the text as JSON.
*   **Response Parsing:** The received message is parsed as a JSON object using `JSON.parse()`.
*   **Message Types:** The code checks for two types of messages:
    *   **`setupComplete`:** Indicates that the setup process is finished.
    *   **`serverContent`:** Contains the model's response, which in this case will be audio data.

### 4. Sending User Messages

*   **Enabling Input:** When a `setupComplete` message is received, the application enables the user input field and the send button.
*   **`sendUserMessage()` Function:** This function is called when the user clicks the "Send" button or presses Enter in the input field.
*   **User Message Structure:** The user message is a JSON object:
    ```javascript
      const contentMessage = {
        client_content: {
          turns: [{
            role: "user",
            parts: [{ text: message }]
          }],
          turn_complete: true
        }
      };
    ```
    *   `client_content`: Contains the conversation content.
    *   `turns`: An array representing the conversation turns.
    *   `role`: Indicates the role of the speaker ("user" in this case).
    *   `parts`: An array of content parts (in this case, a single text part containing the user's message).
    *   `turn_complete`: Set to `true` to signal the end of the user's turn.
*   **Sending the Message:** The content message is stringified and sent to the server using `ws.send()`.
*   **Clearing Input:** The input field is cleared after the message is sent.

### 5. Handling Audio Responses

*   **`serverContent` with Audio:** When a `serverContent` message containing audio data is received, the application extracts the base64-encoded audio data.
*   **`inlineData`:** The audio data is found in `response.serverContent.modelTurn.parts[0].inlineData.data`.
*   **`playAudioChunk()`:** This function is called to handle the audio chunk.
* **Audio Queue:** Audio is pushed into an `audioQueue` array for processing.
* **Audio Playback Management:** `isPlayingAudio` flag ensures that chunks are played sequentially, one after the other.

### 6. Audio Playback with `AudioContext`

*   **`ensureAudioInitialized()`:** This function initializes the `AudioContext` when the first audio chunk is received. This is done lazily to comply with browser autoplay policies. It sets a sample rate of 24000.
    *   **Lazy Initialization:** The `AudioContext` is only created when the first audio chunk is received. This is because some browsers restrict audio playback unless it's initiated by a user action.
    *   **Sample Rate:** The sample rate is set to 24000 Hz, which is a common sample rate for speech audio.
*   **`playAudioChunk()`:**  This function adds an audio chunk to a queue (`audioQueue`) and initiates audio playback if it's not already playing.
*   **`processAudioQueue()`:** This function is responsible for processing and playing audio chunks from the queue.
    *   **Chunk Handling:** It retrieves an audio chunk from the queue.
    *   **Base64 Decoding:** The base64-encoded audio chunk is decoded to an `ArrayBuffer` using `base64ToArrayBuffer()`.
    *   **PCM to Float32 Conversion:** The raw PCM16LE (16-bit little-endian Pulse Code Modulation) audio data is converted to Float32 format using `convertPCM16LEToFloat32()`. This is necessary because `AudioContext` works with floating-point audio data.
    *   **Creating an `AudioBuffer`:** An `AudioBuffer` is created with a single channel, the appropriate length, and a sample rate of 24000 Hz. The Float32 audio data is then copied into the `AudioBuffer`.
    *   **Creating an `AudioBufferSourceNode`:** An `AudioBufferSourceNode` is created, which acts as a source for the audio data. The `AudioBuffer` is assigned to the source node.
    *   **Connecting to Destination:** The source node is connected to the `AudioContext`'s destination (the speakers).
    *   **Starting Playback:** `source.start(0)` starts the playback of the audio chunk immediately.
    *   **`onended` Event:** A promise is used with the `onended` event of the source node to ensure that the next chunk in the queue is only played after the current chunk has finished playing. This is crucial for maintaining the correct order and avoiding overlapping audio.

### 7. Helper Functions

*   **`base64ToArrayBuffer()`:** Converts a base64-encoded string to an `ArrayBuffer`.
*   **`convertPCM16LEToFloat32()`:** Converts PCM16LE audio data to Float32 format.
*   **`logMessage()`:** Appends a message to the `output` div on the HTML page.

### 8. Error Handling and Connection Closure

*   **`onerror` Handler:** Logs WebSocket errors to the console and displays an error message on the page.
*   **`onclose` Handler:** Logs information about the connection closure.

## Summary

This example demonstrates a basic text-to-speech application using the Gemini API with WebSockets. It showcases:

*   Establishing a WebSocket connection and sending a setup message.
*   Handling user input and sending text messages to the API.
*   Receiving audio responses in base64-encoded chunks.
*   Decoding and converting audio data to a format suitable for playback.
*   Using `AudioContext` to play the audio in the browser sequentially, one chunk after the other.
*   Implementing basic error handling and connection closure.

This example provides a starting point for building more sophisticated applications that can generate audio responses from the Gemini model and play them back in real time, all within the browser environment using low-level WebSockets and `AudioContext` for audio management.