# Chapter 10: Gemini Live Chat - Real-time Multimodal Interaction with WebSockets (Vertex API)

This chapter implements the exact same real-time multimodal chat application as [Chapter 6](../../part_2_dev_api/chapter_06/README.md), but using the Vertex AI API instead of the Development API. The application combines audio chat with live video input from the user's webcam or screen, creating a truly multimodal interaction with Gemini.

**Key Differences from Chapter 6:**

1. **API Endpoint:** Uses the Vertex AI WebSocket endpoint through a proxy instead of the direct Development API endpoint
2. **Authentication:** Uses service account authentication through the proxy instead of an API key
3. **Model Path:** Uses the full Vertex AI model path format: `projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/gemini-2.0-flash-exp`
4. **Setup Configuration:** Includes additional Vertex AI-specific configuration parameters in the setup message

The core functionality remains identical to Chapter 6, including:
- Video capture (webcam and screen sharing)
- Audio processing and streaming
- Frame-by-frame video processing
- WebSocket communication patterns
- User interface and controls
- Media handling and state management

Please refer to the comprehensive documentation in [Chapter 6's README](../../part_2_dev_api/chapter_06/README.md).

## Code Comparison

You can compare the implementations by looking at:
- [Chapter 10 index.html](./index.html) (Vertex API version)
- [Chapter 6 index.html](../../part_2_dev_api/chapter_06/index.html) (Development API version)

The main differences are in the initialization and configuration sections, while the core media handling logic remains the same.