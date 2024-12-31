# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import traceback
import pyaudio

from google import genai

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 512

MODEL = "models/gemini-2.0-flash-exp"

client = genai.Client(http_options={'api_version': 'v1alpha'})

CONFIG = {
    "generation_config": {"response_modalities": ["AUDIO"], "speech_config": "Puck"},
    "system_instruction": "Always start your sentence with 'mate'."
}

async def audio_loop():
    audio_queue = asyncio.Queue()
    model_speaking = False
    session = None

    pya = pyaudio.PyAudio()
    mic_info = pya.get_default_input_device_info()

    try:
        async with (
            client.aio.live.connect(model=MODEL, config=CONFIG) as session,
            asyncio.TaskGroup() as tg,
        ):
            input_stream = await asyncio.to_thread(
                pya.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=SEND_SAMPLE_RATE,
                input=True,
                input_device_index=mic_info["index"],
                frames_per_buffer=CHUNK_SIZE,
            )
            output_stream = await asyncio.to_thread(
                pya.open, format=FORMAT, channels=CHANNELS, rate=RECEIVE_SAMPLE_RATE, output=True
            )

            async def listen_and_send():
                nonlocal model_speaking
                while True:
                    if not model_speaking:
                        try:
                            data = await asyncio.to_thread(input_stream.read, CHUNK_SIZE, exception_on_overflow=False)
                            await session.send({"data": data, "mime_type": "audio/pcm"}, end_of_turn=True)
                        except OSError as e:
                            print(f"Audio input error: {e}")
                            await asyncio.sleep(0.1)
                    else:
                        await asyncio.sleep(0.1)

            async def receive_and_play():
                nonlocal model_speaking
                while True:
                    async for response in session.receive():
                        server_content = response.server_content
                        if server_content and server_content.model_turn:
                            model_speaking = True
                            for part in server_content.model_turn.parts:
                                if part.inline_data:
                                    await asyncio.to_thread(output_stream.write, part.inline_data.data)

                        if server_content and server_content.turn_complete:
                            print("Turn complete")
                            model_speaking = False

            tg.create_task(listen_and_send())
            tg.create_task(receive_and_play())

    except Exception as e:
        traceback.print_exception(None, e, e.__traceback__)

if __name__ == "__main__":
    asyncio.run(audio_loop(), debug=True)