# Part 2: WebSocket Development with Gemini API

This section demonstrates how to work directly with the Gemini API using WebSockets, progressively building towards Project Pastra - a production-ready multimodal AI assistant inspired by Google DeepMind's Project Astra. Through a series of chapters, we evolve from basic implementations to a sophisticated, mobile-first application that showcases the full potential of the Gemini API.

## Journey to Project Pastra
Starting with fundamental WebSocket concepts, each chapter adds new capabilities, ultimately culminating in Project Pastra - our implementation of a universal AI assistant that can see, hear, and interact in real-time. Like Project Astra (Google DeepMind's research prototype), our application demonstrates how to create an AI assistant that can engage in natural, multimodal interactions while maintaining production-grade reliability.

## Contents

### Chapter 3: Basic WebSocket Communication
- Single exchange example with the Gemini API
- Core WebSocket setup and communication
- Understanding the API's message formats
- Handling the mandatory setup phase

### Chapter 4: Text-to-Speech Implementation
- Converting text input to audio responses
- Real-time audio playback in the browser
- Audio chunk management and streaming
- WebSocket and AudioContext integration

### Chapter 5: Real-time Audio Chat
- Bidirectional audio communication
- Live microphone input processing
- Voice activity detection and turn management
- Advanced audio streaming techniques

### Chapter 6: Multimodal Interactions
- Adding video capabilities (webcam and screen sharing)
- Frame capture and processing
- Simultaneous audio and video streaming
- Enhanced user interface controls

### Chapter 7: Advanced Features
- Function calling capabilities
- System instructions integration
- External API integrations (weather, search)
- Code execution functionality

### Chapter 8: Project Pastra
- Mobile-first UI design inspired by Project Astra
- Cloud Run deployment setup
- Production-grade error handling
- Scalable architecture implementation

## Key Features
- Direct WebSocket communication with Gemini API
- Real-time audio and video processing
- Browser-based implementation
- Mobile and desktop support
- Production deployment guidance

## Prerequisites
- Basic understanding of WebSockets
- Familiarity with JavaScript and HTML5
- Google Gemini API access
- Modern web browser with WebSocket support

## Getting Started

This guide uses a simple development server to:
- Serve the HTML/JavaScript files for each chapter
- Provide access to shared components (audio processing, media handling, etc.) used across chapters
- Enable proper loading of JavaScript modules and assets
- Avoid CORS issues when accessing local files

1. Start the development server:
   ```bash
   python server.py
   ```
   This will serve both the chapter files and shared components at http://localhost:8000

2. Navigate to the specific chapter you want to work with:
   - Chapter 3: http://localhost:8000/chapter_03/
   - Chapter 4: http://localhost:8000/chapter_04/
   And so on...

3. Begin with Chapter 3 to understand the fundamentals of WebSocket communication with Gemini. Each subsequent chapter builds upon previous concepts, gradually introducing more complex features and capabilities. By Chapter 8, you'll have transformed the development prototype into Project Pastra - a production-ready AI assistant that demonstrates the future of human-AI interaction. 