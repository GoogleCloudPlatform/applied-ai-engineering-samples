# Chapter 6: Gemini Live Chat - Real-time Multimodal Interaction with WebSockets

This chapter takes the real-time audio chat application from **Chapter 5** and significantly enhances it by incorporating **live video input** from the user's webcam or screen. This creates a truly **multimodal** interaction with the Gemini API, demonstrating a more sophisticated and engaging use case. We'll be building upon the existing WebSocket communication and Web Audio API infrastructure to handle both audio and video streams simultaneously.

**Building Upon Previous Chapters:**

Chapter 6 leverages the foundational concepts and components established in earlier chapters:

*   **Chapter 2 (Live Audio Chat with Gemini):** Provided the basis for real-time audio interaction, which we extend here.
*   **Chapter 3 (Low-Level WebSocket Interaction):** Introduced the core WebSocket communication principles that are essential for this chapter.
*   **Chapter 4 (Text-to-Speech with WebSockets):** Demonstrated basic audio handling with WebSockets, which we build upon for live audio streaming.
*   **Chapter 5 (Real-time Audio-to-Audio):**  Established the foundation for real-time audio streaming using WebSockets and the Web Audio API. Chapter 6 extends this by adding video capabilities. We'll reuse the `AudioRecorder`, `AudioStreamer`, and WebSocket communication logic from this chapter.

**New Functionalities in Chapter 6:**

This chapter introduces the following key additions:

1. **Video Capture and Management:**
    *   **`MediaHandler` Class:** A new `MediaHandler` class is introduced to manage user media, specifically for webcam and screen capture. It's responsible for:
        *   Requesting access to the user's webcam or screen using `navigator.mediaDevices.getUserMedia()` and `navigator.mediaDevices.getDisplayMedia()`.
        *   Starting and stopping video streams.
        *   Capturing individual frames from the video stream.
        *   Managing the active state of the webcam and screen sharing (using `isWebcamActive` and `isScreenActive` flags).
    *   **Webcam and Screen Sharing Toggle:** The UI now includes two new buttons with material symbol icons:
        *   **Webcam Button:** Toggles the webcam on and off.
        *   **Screen Sharing Button:** Toggles screen sharing on and off.
    *   **Video Preview:** A `<video>` element is added to the UI to display a live preview of the selected video stream (webcam or screen). This provides visual feedback to the user.
    *   **`startWebcam()` and `startScreenShare()`:** These methods within `MediaHandler` handle the intricacies of starting the respective video streams, including requesting user permissions.
    *   **`stopAll()`:** This method in `MediaHandler` ensures that all active media streams (both audio and video) are properly stopped when needed, such as during interruptions or when the user stops recording.

2. **Video Frame Processing:**
    *   **`startFrameCapture()`:** This method, called when a video stream starts, sets up an interval to capture frames from the video element at a rate of 2 frames per second (every 500 milliseconds).
        ```javascript
        startFrameCapture(onFrame) {
            const captureFrame = () => {
              // ... capture and process frame ...
            };

            // Capture frames at 2fps
            this.frameCapture = setInterval(captureFrame, 500);
        }
        ```
    *   **`stopFrameCapture()`:** This method clears the interval, stopping the frame capturing process.
    *   **Canvas for Frame Extraction:** An invisible `<canvas>` element is used as an intermediary to extract the current frame from the `<video>` element. The `drawImage()` method of the canvas's 2D rendering context is used to copy the video frame onto the canvas.
    *   **JPEG Encoding:** Each captured frame is converted into a base64-encoded JPEG image using `canvas.toDataURL('image/jpeg', 0.8)`.
        *   **`toDataURL()`:** This method returns a data URL representing the image in the specified format (JPEG here) and quality (0.8, which is a value between 0 and 1, where 1 is the best quality and 0 is the worst).
        *   **Why JPEG:** JPEG is a widely supported image format that offers a good balance between compression and image quality. It's suitable for transmitting images over a network.
        *   **Base64 Encoding:** The image data is encoded in base64 because the WebSocket connection primarily handles text data. Base64 provides a way to represent binary data (the image) as text.
        *   **Token Usage:** Note that regardless of the JPEG quality setting or compression level, each image will consume exactly 258 tokens when processed by the Gemini API. The quality setting only affects network bandwidth usage, not token consumption.
    *   **Frame Rate (2 FPS):** The frame capture rate is set to 2 frames per second. This value is a compromise between providing relatively smooth visual updates and managing both bandwidth and token usage (each frame consumes 258 tokens).
    *   **Quality (0.8):** The quality parameter (0.8) in `toDataURL()` represents a balance between image quality and network bandwidth usage. Lower values will result in smaller file sizes for transmission but won't affect the token count - each frame still uses 258 tokens regardless of quality or file size.
        *   **Dynamic Control (Future Improvement):** Ideally, the frame rate and quality could be dynamically adjusted based on network conditions and API performance.

3. **Sending Video Frames to the API:**

    *   **`realtime_input` with `media_chunks`:** The `realtime_input` message format is used to send both audio and video data. This message format is defined in the API documentation under `BidiGenerateContentRealtimeInput`.
        *   **`mime_type: "image/jpeg"`:** Video frames are sent as `media_chunks` with the `mime_type` set to `"image/jpeg"` to indicate that they are JPEG images.
        *   **`data`:** The base64-encoded JPEG data is included in the `data` field of the `media_chunks` object.

    ```javascript
    const message = {
      realtimeInput: {
        mediaChunks: [{
          mime_type: "image/jpeg",
          data: base64Image
        }]
      }
    };
    ```

    *   **Sending Logic:** The `startFrameCapture()` method sends each captured and encoded frame to the API via `ws.send()`.
    *   **No Continuous Video Streaming:** Unlike the continuous audio streaming, video frames are sent only when a video stream is active (webcam or screen sharing).
    *   **User Control:** The user explicitly starts and stops video streams using the provided buttons, giving them control over when video data is sent.

4. **UI Enhancements:**

    *   **Video Container:** A `video-container` div is added to the HTML to hold the video preview element, providing a dedicated area for the video.
    *   **Video Preview Element:** The `<video>` element with ID `videoPreview` is styled with CSS to ensure it fits within the `video-container` and has rounded corners for a visually appealing presentation. It also has the `autoplay` and `playsinline` attributes.
        *   **`autoplay`:** Makes the video play automatically when a stream is available.
        *   **`playsinline`:** Prevents the video from automatically going fullscreen on some mobile devices.
    *   **Material Symbols:** The webcam and screen sharing buttons use Material Symbols for a visually consistent and user-friendly interface. The icons are dynamically updated to reflect the active/inactive state of each stream (e.g., `videocam` vs. `videocam_off`).

**In essence, Chapter 6 extends the audio-only chat of Chapter 5 by adding:**

*   **Video capture capabilities (webcam and screen sharing).**
*   **Frame-by-frame encoding of video data into base64 JPEG images.**
*   **Transmission of video frames alongside audio chunks to the Gemini API using the `realtime_input` message format.**
*   **UI elements for controlling video input and previewing the video stream.**

By building upon the foundation of Chapter 5, this chapter demonstrates a more complex and interactive **multimodal** application, showcasing the versatility of the Gemini Multimodal Live API for handling both audio and video input in a real-time setting.

## Project Structure

This chapter's application consists of the following files:

*   **`index.html`:** The main HTML file that sets up the user interface (microphone button, video preview, and an output area for messages) and includes the core JavaScript logic for WebSocket communication, video and overall application flow.
*   **`audio-recorder.js`:**  Contains the `AudioRecorder` class, which handles capturing audio from the microphone, converting it to the required format, and emitting chunks of audio data using an `EventEmitter3` interface.
*   **`audio-streamer.js`:** Contains the `AudioStreamer` class, which manages audio playback using the Web Audio API. It handles queuing, buffering, and playing audio chunks received from the API, ensuring smooth and continuous playback.
*   **`audio-recording-worklet.js`:** Defines an `AudioWorkletProcessor` that runs in a separate thread and performs the low-level audio processing, including float32 to int16 conversion and chunking.
*   **`audioworklet-registry.js`:** A utility to help register and manage `AudioWorklet`s, preventing duplicate registration.
*   **`utils.js`:** Provides utility functions like `audioContext` (for creating an `AudioContext`) and `base64ToArrayBuffer` (for decoding base64 audio data).
*   **`style.css`:** Contains basic CSS styles for the user interface.
*   **`media-handler.js`:** Contains the `MediaHandler` class, which manages user media (webcam or screen capture). It handles requesting access to the user's webcam or screen, starting and stopping the video streams, and capturing video frames.

## Further Considerations

*   **Error Handling:** The code includes basic error handling, but it could be made more robust by handling specific error codes or messages from the API and providing more informative feedback to the user.
*   **Security:** The API key is currently hardcoded in the HTML file. For production, you should **never** expose your API key directly in client-side code. Instead, use a secure backend server to handle authentication and proxy requests to the API.
*   **Scalability:** This example is designed for a single user. For a multi-user scenario, you would need to manage multiple WebSocket connections and potentially use a server-side component to handle user sessions and routing.
*   **Audio Quality:** The audio quality depends on the microphone, network conditions, and the API's processing. You can experiment with different sample rates and chunk sizes, but these values are often constrained by the API's requirements and the need to balance latency and bandwidth.
*   **Network Latency:** Network latency can significantly impact the real-time performance of the application. There's no single solution to mitigate network latency, but using a server closer to the user's location and optimizing the audio processing pipeline can help.
*   **Video Quality:** Currently, video frames are captured every 500ms at a quality setting of 0.8. While the quality setting affects network bandwidth usage, it's important to note that it has no impact on token consumption - each frame will use 258 tokens regardless of its compression level or file size. You can adjust the quality parameter and `captureRate` based on your network bandwidth requirements without worrying about token usage.
*   **Bandwidth Usage:** Sending video frames in addition to audio increases bandwidth consumption. Consider the user's network conditions and potentially provide options to adjust video quality or frame rate.


## Summary

This chapter demonstrated how to build a real-world application with the multimodal capabilities of the Gemini API. Now Gemini can not only respond to your voice but also to what it sees in real time.