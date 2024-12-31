# Gemini WebSocket Test - Single Exchange Example

This HTML file demonstrates a **single exchange** with the Gemini language model using WebSockets, illustrating the fundamental principles of interacting with the API at a low level, **without using an SDK**. The application establishes a WebSocket connection, sends a hardcoded user message, and displays the model's response in the browser.

**This example is primarily for educational purposes**, showcasing how to use the browser's built-in WebSocket API to communicate with the Gemini API directly. It is not intended to be a full-fledged chat application but rather a simplified demonstration of the underlying communication mechanism.

## How it works

The application's functionality can be broken down into several key components:

### 1. Establishing a WebSocket Connection

*   **API Endpoint:** The application connects to the Gemini API using a specific WebSocket endpoint URL:
    ```
    wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key=${apiKey}
    ```
    This URL includes the API host, the service path, and an API key for authentication. Replace `${apiKey}` with your actual API key.
*   **WebSocket Object:** A new `WebSocket` object is created in JavaScript, initiating the connection:
    ```javascript
    const ws = new WebSocket(endpoint);
    ```
*   **Event Handlers:** Event handlers are defined to manage the connection's lifecycle and handle incoming messages:
    *   `onopen`: Triggered when the connection is successfully opened.
    *   `onmessage`: Triggered when a message is received from the server.
    *   `onerror`: Triggered if an error occurs during the connection.
    *   `onclose`: Triggered when the connection is closed.

### 2. Sending a Setup Message (Mandatory First Step)

*   **API Requirement:** The Gemini API requires a setup message to be sent as the **very first message** after the WebSocket connection is established. This is crucial for configuring the session.
*   **`onopen` Handler:** The `onopen` event handler, which is triggered when the connection is open, is responsible for sending this setup message.
*   **Setup Message Structure:** The setup message is a JSON object that conforms to the `BidiGenerateContentSetup` format as defined in the API documentation:
    ```javascript
    const setupMessage = {
      setup: {
        model: "models/gemini-2.0-flash-exp",
        generation_config: {
          response_modalities: ["text"]
        }
      }
    };
    ```
    *   `model`: Specifies the Gemini model to use (`"models/gemini-2.0-flash-exp"` in this case).
    *   `generation_config`: Configures the generation parameters, such as the `response_modalities` (set to `"text"` for text-based output). You can also specify other parameters like `temperature`, `top_p`, `top_k`, etc., within `generation_config` as needed.
*   **Sending the Message:** The setup message is stringified and sent to the server using `ws.send()`:
    ```javascript
    ws.send(JSON.stringify(setupMessage));
    ```

### 3. Receiving and Processing Messages

*   **`onmessage` Handler:** The `onmessage` event handler receives messages from the server.
*   **Data Handling:** The code handles potential `Blob` data using `new Response(event.data).text()`, but in this text-only example, it directly parses the message as JSON.
*   **Response Parsing:** The received message is parsed as a JSON object using `JSON.parse()`.
*   **Message Types:** The code specifically checks for a `BidiGenerateContentSetupComplete` message type, indicated by the `setupComplete` field in the response.

### 4. Confirming Setup Completion Before Proceeding

*   **`setupComplete` Check:** The code includes a conditional check to ensure that a `setupComplete` message is received before sending any user content:
    ```javascript
    if (response.setupComplete) {
        // ... Send user message ...
    }
    ```
*   **Why This Is Important:** This check is essential because the API will not process user content messages until the setup is complete. Sending content before receiving confirmation that the setup is complete will likely result in an error or unexpected behavior. The API might close the connection if messages other than the initial setup message are sent before the setup is completed.

### 5. Sending a Hardcoded User Message

*   **Triggered by `setupComplete`:** Only after the `setupComplete` message is received and processed does the application send a user message to the model.
*   **User Message Structure:** The user message is a JSON object conforming to the `BidiGenerateContentClientContent` format:
    ```javascript
    const contentMessage = {
      client_content: {
        turns: [{
          role: "user",
          parts: [{ text: "Hello! Are you there?" }]
        }],
        turn_complete: true
      }
    };
    ```
    *   `client_content`: Contains the conversation content.
    *   `turns`: An array representing the conversation turns.
    *   `role`: Indicates the role of the speaker ("user" in this case).
    *   `parts`: An array of content parts (in this case, a single text part).
    *   `text`: The actual user message (hardcoded to "Hello! Are you there?").
    *   `turn_complete`: Set to `true` to signal the end of the user's turn.
*   **Sending the Message:** The content message is stringified and sent to the server using `ws.send()`.

### 6. Displaying the Model's Response

*   **`serverContent` Handling:** When a `serverContent` message is received (which contains the model's response), the application extracts the response text.
*   **Response Extraction:** The model's response is accessed using `response.serverContent.modelTurn.parts[0]?.text`.
*   **Displaying the Response:** The `logMessage()` function displays the model's response in the `output` div on the HTML page.

### 7. Error Handling and Connection Closure

*   **`onerror` Handler:** The `onerror` event handler logs any WebSocket errors to the console and displays an error message on the page.
*   **`onclose` Handler:** The `onclose` event handler logs information about the connection closure, including the reason and status code.

### 8. Logging Messages

*   **`logMessage()` Function:** This utility function creates a new paragraph element (`<p>`) and appends it to the `output` div, displaying the provided message on the page.

## Educational Purpose

This example focuses on demonstrating the **low-level interaction with the Gemini API using WebSockets**. It highlights the importance of the **setup phase** and demonstrates how to:

1. **Establish a raw WebSocket connection** without relying on an SDK.
2. **Send a properly formatted `BidiGenerateContentSetup` message** as the first message to configure the session.
3. **Wait for and verify the `setupComplete` message** before sending any user content.
4. **Send properly formatted `BidiGenerateContentClientContent` messages** containing user input.
5. **Parse and interpret the JSON responses** from the API, including `BidiGenerateContentSetupComplete` and `BidiGenerateContentServerContent` messages.
6. **Handle basic events** like `onopen`, `onmessage`, `onerror`, and `onclose`.

By examining this code, you can gain a deeper understanding of the underlying communication protocol and message formats used by the Gemini API, particularly the **mandatory setup phase**. This knowledge can be valuable for debugging, troubleshooting, or building custom integrations that require more control than an SDK might offer.

**Note:** This is a simplified example for educational purposes. A real-world chat application would involve more complex features like:

*   Dynamic user input.
*   Handling multiple conversation turns.
*   Maintaining conversation history.
*   Potentially integrating audio or video.

This example provides a solid foundation for understanding the basic principles involved in interacting with the Gemini API at a low level using WebSockets, especially the crucial setup process.