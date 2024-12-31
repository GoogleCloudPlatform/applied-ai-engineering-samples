# Chapter 11: Function Calling and System Instructions (Vertex API)

This chapter implements the function calling and system instructions capabilities demonstrated in [Chapter 7](../../part_2_dev_api/chapter_07/README.md), but using the Vertex AI API instead of the Development API.

**Key Differences from Chapter 7:**

1. **API Endpoint:** Uses the Vertex AI WebSocket endpoint through a proxy instead of the direct Development API endpoint
2. **Authentication:** Uses service account authentication through the proxy instead of an API key
3. **Model Path:** Uses the full Vertex AI model path format: `projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/gemini-2.0-flash-exp`
4. **Setup Configuration:** Includes additional Vertex AI-specific configuration parameters in the setup message
5. **⚠️ Important Tool Limitation:** Unlike the Development API which supports multiple tools, the Vertex AI API currently supports only one tool declaration. This means you must choose a single function to expose to the model (weather, search, or code execution) rather than providing all three simultaneously.

The core functionality remains similar to Chapter 7, but adapted for the single-tool limitation:
- System instructions support
- Function calling (limited to one function)
- WebSocket communication patterns
- Enhanced connection handling
- All multimodal capabilities from Chapter 10

Please refer to the comprehensive documentation in [Chapter 7's README](../../part_2_dev_api/chapter_07/README.md), keeping in mind that you'll need to adapt the implementation to work with a single tool at a time.

## Code Comparison

You can compare the implementations by looking at:
- [Chapter 11 index.html](./index.html) (Vertex API version)
- [Chapter 7 index.html](../../part_2_dev_api/chapter_07/index.html) (Development API version)

The main differences are in the initialization, configuration, and tool declaration sections, while the core system instruction handling remains the same.