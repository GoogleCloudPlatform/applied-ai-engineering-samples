# Chapter 7: Function Calling and System Instructions

This chapter builds upon the multimodal chat application from **Chapter 6** and adds support for function calling and system instructions. These additions enable Gemini to perform specific actions like getting weather information, executing code, and performing web searches, while following a predefined set of behavioral rules.

## New Features

### 1. Function Calling
The application now supports three built-in functions that Gemini can use:
- **get_weather**: Retrieves current weather information for a specified city
- **code_execution**: Executes code snippets on demand
- **google_search**: Performs web searches to find relevant information

These functions are declared in the WebSocket setup message and are automatically invoked by Gemini when appropriate based on the conversation context.

### 2. System Instructions
A new `system-instructions.txt` file defines rules and behaviors for the AI assistant:
- Mandatory use of the weather tool for weather-related queries
- Required use of Google search for information lookups
- Automatic code execution for calculations and data processing

### 3. Enhanced WebSocket Setup
The setup process has been modified to:
- Load system instructions from an external file
- Include function declarations in the setup message
- Support reconnection with preserved system instructions

## Technical Improvements

### Modified Setup Message
The WebSocket setup message now includes:
```javascript
{
  setup: {
    model: "models/gemini-2.0-flash-exp",
    system_instruction: {
      role: "user",
      parts: [{ text: systemInstructions }]
    },
    tools: [{
      functionDeclarations: [
        // Function declarations for weather, search, and code execution
      ]
    }],
    generation_config: {
      // Configuration for audio responses
    }
  }
}
```

### Improved Connection Handling
- System instructions are preserved across reconnections
- Custom setup is resent when reconnecting
- Enhanced error handling for WebSocket operations

## Building Upon Chapter 6

This chapter retains all the core functionality from Chapter 6:
- Real-time audio chat
- Webcam integration
- Screen sharing capabilities
- Video frame capture and processing

The additions in this chapter make the application more capable by allowing Gemini to:
1. Access external data (weather, web search)
2. Execute code for computations
3. Follow specific behavioral rules
4. Maintain consistent behavior through system instructions

## Project Structure

The application consists of the following key files:
- **`index.html`**: Main application file with enhanced WebSocket setup
- **`system-instructions.txt`**: Defines AI assistant behavior rules
- **`style.css`**: UI styling (inherited from Chapter 6)
- Shared components from Chapter 6:
  - **`audio-recorder.js`**
  - **`audio-streamer.js`**
  - **`media-handler.js`**
  - **`gemini-live-api.js`**

## Usage Examples

1. **Weather Queries**:
   - "What's the weather in London?"
   - Gemini automatically uses the weather tool to fetch current conditions

2. **Information Lookup**:
   - "What is the current stock price of Google?"
   - Gemini uses Google search to find current information

3. **Calculations**:
   - "What is the largest prime palindrome under 100000?"
   - Gemini uses code execution to compute the result
