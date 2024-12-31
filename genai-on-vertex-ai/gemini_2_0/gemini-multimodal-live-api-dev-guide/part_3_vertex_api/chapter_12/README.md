# Chapter 12: Project Vastra - Mobile-First Multimodal AI Assistant (Vertex API)

This chapter implements the mobile-first multimodal assistant demonstrated in [Chapter 8 (Project Pastra)](../../part_2_dev_api/chapter_08/README.md), but using the Vertex AI API instead of the Development API. We call it "Project Vastra" to distinguish it from the Development API version.

**Key Differences from Chapter 8:**

1. **API Endpoint:** Uses the Vertex AI WebSocket endpoint through a proxy instead of the direct Development API endpoint
2. **Authentication:** Uses service account authentication through the proxy instead of an API key
3. **Model Path:** Uses the full Vertex AI model path format: `projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/gemini-2.0-flash-exp`
4. **Setup Configuration:** Includes additional Vertex AI-specific configuration parameters in the setup message
5. **⚠️ Complex Deployment Architecture:** Unlike Project Pastra which could be deployed as a single service, Project Vastra requires a more complex setup:
   - Main application service (Cloud Run)
   - WebSocket proxy service (separate Cloud Run instance)
   - Service account configuration
   - IAM role setup for service-to-service communication

The core functionality remains identical to Chapter 8, including:
- Mobile-first UI design
- Touch-friendly controls
- Status indicators
- Cloud Run deployment
- Enhanced user experience
- All multimodal capabilities from Chapter 10
- Function calling capabilities from Chapter 11 (with single-tool limitation)

## Deployment Architecture

The deployment is more complex due to the proxy server requirement:

```
Client <-> Cloud Run (Main App) <-> Cloud Run (Proxy) <-> Vertex AI
```

Key components:
1. **Main Application Service:**
   - Serves the web interface
   - Handles media processing
   - Manages client connections

2. **Proxy Service:**
   - Authenticates with Vertex AI
   - Manages WebSocket connections
   - Handles service account credentials
   - Routes messages between client and API

For detailed technical information about the implementation, including:
- Mobile-first UI design
- Cloud Run deployment
- Status management
- Project structure
- Usage instructions
- Design philosophy

Please refer to the comprehensive documentation in [Chapter 8's README](../../part_2_dev_api/chapter_08/README.md).

## Code Comparison

You can compare the implementations by looking at:
- [Chapter 12 index.html](./index.html) (Vertex API version)
- [Chapter 8 index.html](../../part_2_dev_api/chapter_08/index.html) (Development API version)

The main differences are in the deployment architecture, service configuration, and authentication handling, while the core mobile-first UI and user experience remain the same.