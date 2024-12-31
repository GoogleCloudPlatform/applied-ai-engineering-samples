# Chapter 9: Gemini Live Audio Chat - Real-time Audio-to-Audio with WebSockets (Vertex API)

This chapter implements the exact same real-time audio-to-audio chat application as [Chapter 5](../../part_2_dev_api/chapter_05/README.md), but using the Vertex AI API instead of the Development API.

**Key Differences from Chapter 5:**

1. **API Endpoint:** Uses the Vertex AI WebSocket endpoint through a proxy instead of the direct Development API endpoint
2. **Authentication:** Uses service account authentication through the proxy instead of an API key
3. **Model Path:** Uses the full Vertex AI model path format: `projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/gemini-2.0-flash-exp`
4. **Setup Configuration:** Includes additional Vertex AI-specific configuration parameters in the setup message

The core functionality, audio processing, WebSocket communication patterns, and user interface remain identical to Chapter 5. For detailed technical information about the implementation, including:
- Audio processing pipeline
- WebSocket communication
- Interruption handling
- Audio streaming and buffering
- Web Audio API usage
- Configuration parameters
- Best practices and lessons learned

Please refer to the comprehensive documentation in [Chapter 5's README](../../part_2_dev_api/chapter_05/README.md).

## Code Comparison

You can compare the implementations by looking at:
- [Chapter 9 index.html](./index.html) (Vertex API version)
- [Chapter 5 index.html](../../part_2_dev_api/chapter_05/index.html) (Development API version)

The main differences are in the initialization and configuration sections, while the core audio handling logic remains the same.
