# Gemini Live Audio Chat

This project enables real-time, two-way audio communication with a Gemini language model. The application captures audio input from the user's microphone, sends it to the Gemini API for processing, receives the model's audio response, and plays it back through the user's speakers. This creates an interactive and conversational experience, similar to talking to a voice assistant.

The core of the application lies in its ability to manage the continuous flow of audio data between the user and the model. It uses asynchronous programming to handle audio input and output concurrently, ensuring smooth and responsive interaction. The application utilizes the `pyaudio` library to interface with the user's audio hardware, capturing microphone input and playing audio output. The `google-genai` library facilitates communication with the Gemini API, sending audio data for processing and receiving the model's responses.

## How it works

### System Architecture

![Audio Client Diagram](/assets/audio-client.png)

The application's functionality can be broken down into several key components:

### Audio Input and Output

The `pyaudio` library is used to create input and output streams that interface with the user's audio hardware.

*   **Input Stream:** An input stream is initialized to capture audio data from the user's microphone. The stream is configured with parameters such as format, channels, sample rate, and chunk size. The `SEND_SAMPLE_RATE` is set to 16000 Hz, which is a common sample rate for speech recognition. The `CHUNK_SIZE` determines the number of audio frames read from the microphone at a time. The `exception_on_overflow` parameter is set to `False` to prevent the stream from raising an exception if the buffer overflows.
*   **Output Stream:** An output stream is initialized to play audio data through the user's speakers. Similar to the input stream, it is configured with appropriate parameters. The `RECEIVE_SAMPLE_RATE` is set to 24000 Hz, which is suitable for high-quality audio playback.

### Communication with Gemini API

The `google-genai` library provides the necessary tools to connect to the Gemini API and establish a communication session.

*   **Client Initialization:** A `genai.Client` is created to interact with the API. The `http_options` parameter is used to specify the API version, which is set to `'v1alpha'` in this case.
*   **Session Configuration:** A configuration object `CONFIG` is defined to customize the interaction with the model. This includes:
    *   `generation_config`: Specifies the response modality as "AUDIO" and configures the "speech_config" to "Puck".
    *   `system_instruction`: Sets a system instruction to always start the model's sentences with "mate".
*   **Live Connection:** The `client.aio.live.connect` method establishes a live connection to the Gemini model specified by `MODEL`, which is set to `"models/gemini-2.0-flash-exp"`.

### Asynchronous Audio Handling

The `asyncio` library is used to manage the asynchronous operations involved in audio processing and communication.

*   **Audio Queue:** An `asyncio.Queue` is created to store audio data temporarily. This queue is not used in the current implementation but is defined for potential future use.
*   **Task Group:** An `asyncio.TaskGroup` is used to manage two concurrent tasks: `listen_and_send` and `receive_and_play`.
*   **`listen_and_send` Task:** This task continuously reads audio data from the input stream in chunks and sends it to the Gemini API. It checks if the model is currently speaking (`model_speaking` flag) and only sends data if the model is not speaking. The chunking is performed using the `pyaudio` library's `read()` method, which is called with a specific `CHUNK_SIZE` (number of audio frames per chunk). Here's how it's done in the code:

    ```python
    while True:
        if not model_speaking:
            try:
                data = await asyncio.to_thread(input_stream.read, CHUNK_SIZE, exception_on_overflow=False)
                # ... send data to API ...
            except OSError as e:
                # ... handle error ...
    ```

    In this code, `input_stream.read(CHUNK_SIZE)` reads a chunk of audio frames from the microphone's input buffer. Each chunk is then sent to the API along with the `end_of_turn=True` flag.
*   **`receive_and_play` Task:** This task continuously receives responses from the Gemini API and plays the audio data through the output stream. It sets the `model_speaking` flag to `True` when the model starts speaking and to `False` when the turn is complete. It then iterates through the parts of the response and writes the audio data to the output stream.

### Audio Chunking and Real-time Interaction

A crucial aspect of the application's real-time audio processing is how the continuous audio stream from the microphone is divided into smaller chunks before being sent to the Gemini API. This chunking is performed in the `listen_and_send` task using the `pyaudio` library.

**Chunking Process:**

The `input_stream.read(CHUNK_SIZE)` method is called repeatedly to read a fixed number of audio frames (defined by `CHUNK_SIZE`) from the microphone's buffer. Each chunk represents a small segment of the audio stream. The current implementation uses a `CHUNK_SIZE` of 512 frames.

**Calculating Chunk Duration:**

The duration of each audio chunk can be calculated using the following formula:

`Chunk Duration (seconds) = (Number of Frames) / (Sample Rate)`

In this case, with a `CHUNK_SIZE` of 512 frames and a `SEND_SAMPLE_RATE` of 16000 Hz, the chunk duration is:

`Chunk Duration = 512 frames / 16000 Hz = 0.032 seconds = 32 milliseconds`


Therefore, each chunk represents 32 milliseconds of audio.

**Real-time Interaction Flow:**

To understand how chunking enables a smooth, real-time conversation, let's trace the steps involved when you speak to the model:

1. **User Speaks:** You start speaking into the microphone.
2. **Audio Capture:** The `listen_and_send` task continuously captures audio data from the microphone.
3. **Chunking (Fast):** Every time 512 frames (32 milliseconds of audio) are captured, a chunk is created.
4. **Send to API (Frequent):** This small chunk is immediately sent to the Gemini API, along with `end_of_turn=True`.
5. **API Processing (Starts Early):** The API receives the chunk and its Voice Activity Detection (VAD) starts analyzing it. Because the chunks are small and frequent, the API can begin processing the audio very quickly, even while the user is still speaking.
6. **Model Response (Begins Quickly):** Once the API's VAD detects a pause that it interprets as the end of a user's turn (even if it's a short pause between phrases), the Gemini model starts generating a response based on the audio it has received so far.
7. **Audio Output (Low Latency):** The response audio is sent back to the client in chunks. The `receive_and_play` task starts playing the response audio as soon as it arrives, minimizing the delay.

**Impact of `CHUNK_SIZE`:**

The `CHUNK_SIZE` is a configurable parameter that affects the latency and responsiveness of the system. Smaller chunks can potentially reduce latency, as they allow the API to start processing and responding sooner. However, very small chunks might increase processing overhead. Larger chunks, on the other hand, would introduce noticeable delays in the conversation, making it feel sluggish and less interactive. The choice of 512 frames strikes a good balance between low latency and manageable processing overhead for a real-time chat application.

**Why `end_of_turn=True` with Each Chunk?**

Each chunk is sent to the API with the `end_of_turn=True` flag. While this might seem like it would interrupt the flow of the conversation, the Gemini API uses its Voice Activity Detection (VAD) to determine the actual turn boundaries based on longer pauses in the audio stream, not solely on the `end_of_turn` flag from each chunk. This allows for a relatively smooth conversation flow despite the frequent `end_of_turn` signals.

### Input/Output and Turn-Taking

The application distinguishes between user input and model output through a combination of the `model_speaking` flag, the `end_of_turn=True` signal sent with each audio chunk, and the Gemini API's Voice Activity Detection (VAD).

**Distinguishing Input from Output:**

*   **`model_speaking` Flag:** This boolean flag serves as a primary mechanism to differentiate between when the user is providing input and when the model is generating output.
    *   When `model_speaking` is `False`, the application assumes it's the user's turn to speak. The `listen_and_send` task reads audio data from the microphone and sends it to the API.
    *   When `model_speaking` is `True`, the application understands that the model is currently generating an audio response. The `listen_and_send` task pauses, preventing user input from being sent to the API while the model is "speaking." The `receive_and_play` task is active during this time, receiving and playing the model's audio output.

**How Audio Chunks are Sent:**

*   **`end_of_turn=True` with Each Chunk:** The `listen_and_send` task sends each chunk of audio data (determined by `CHUNK_SIZE`) with `end_of_turn=True` in the message payload: `await session.send({"data": data, "mime_type": "audio/pcm"}, end_of_turn=True)`. This might seem like it would constantly interrupt the conversation flow. However, the API handles this gracefully.
*   **API-Side Buffering and VAD:** The Gemini API likely buffers the incoming audio chunks on its end. Even though each chunk is marked as the end of a turn with `end_of_turn=True`, the API's Voice Activity Detection (VAD) analyzes the buffered audio to identify longer pauses or periods of silence that more accurately represent the actual end of the user's speech. The API can group several chunks into what it considers a single user turn based on its VAD analysis, rather than strictly treating each chunk as a separate turn.
*   **Low-Latency Processing:** The API is designed for low-latency interaction. It starts processing the received audio chunks as soon as possible. Even if `end_of_turn=True` is sent with each chunk, the API can begin generating a response while still receiving more audio from the user, as long as it hasn't detected a significant enough pause to finalize the user's turn based on its VAD.

**Determining End of Model Turn:**

*   **`turn_complete` Field:** The `receive_and_play` task continuously listens for responses from the API. Each response includes a `server_content` object, which contains a `turn_complete` field.
    *   When `turn_complete` is `True`, it signifies that the model has finished generating its response for the current turn.
    *   Upon receiving a `turn_complete: True` signal, the `receive_and_play` task sets the `model_speaking` flag to `False`. This signals that the model's turn is over, and the application is ready to accept new user input.

**Turn-Taking Flow:**

1. Initially, `model_speaking` is `False`, indicating it's the user's turn.
2. The `listen_and_send` task captures audio chunks from the microphone and sends each chunk to the API with `end_of_turn=True`.
3. The API buffers the audio and its VAD determines the actual end of the user's speech based on longer pauses, not just the `end_of_turn` signal from each chunk.
4. The model processes the input and starts generating a response.
5. The `receive_and_play` task receives the response, sets `model_speaking` to `True`, and plays the audio.
6. When the model finishes, it sends `turn_complete: True`.
7. The `receive_and_play` task sets `model_speaking` to `False`, switching back to the user's turn.

In essence, although `end_of_turn=True` is sent with each audio chunk, the API's VAD plays a more significant role in determining the actual turn boundaries. The `end_of_turn=True` in this implementation might act more as a hint or a nudge to the API to process the audio, rather than a definitive end-of-turn marker. This approach allows for a relatively smooth conversation flow despite the frequent `end_of_turn` signals, thanks to the API's buffering, VAD, and low-latency processing.

### Why Always Set `end_of_turn=True`?

Setting `end_of_turn=True` with each audio chunk, even when the user hasn't finished speaking, might seem counterintuitive. Here are some  reasons for this design choice:

1. **Simplicity and Reduced Client-Side Complexity:** Implementing robust Voice Activity Detection (VAD) on the client-side can be complex. By always setting `end_of_turn=True`, the developers might have opted for a simpler client-side implementation that offloads the more complex VAD task to the Gemini API.
2. **Lower Latency:** Sending smaller chunks with `end_of_turn=True` might allow the API to start processing the audio sooner. However, this potential latency benefit depends heavily on how the API is designed.
3. **Emphasis on API-Side Control:** By sending `end_of_turn=True` frequently, the client cedes more control over turn-taking to the API. The API's VAD becomes the primary mechanism for determining turn boundaries.

**It's important to note:** While this approach can work, it's not necessarily the most optimal or efficient way to handle turn-taking in a voice conversation system. Ideally, you would want to send `end_of_turn=True` only when the user has actually finished speaking, which would typically involve implementing client-side VAD.

### Main Loop

The `audio_loop` function orchestrates the entire process.

1. **Initialization:** It initializes variables, including the audio queue, `model_speaking` flag, and session object.
2. **Connection and Task Creation:** It establishes a live connection to the Gemini API and creates the `listen_and_send` and `receive_and_play` tasks within a task group.
3. **Error Handling:** It includes a `try...except` block to catch any exceptions that occur during the process and prints the traceback.

### Execution

The `if __name__ == "__main__":` block ensures that the `audio_loop` function is executed only when the script is run directly. The `asyncio.run` function starts the asynchronous event loop and runs the `audio_loop` function, enabling the real-time audio chat.

## Limitations

The current implementation does not support user interruption of the model's speech.

