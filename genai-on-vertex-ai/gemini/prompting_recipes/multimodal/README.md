## Multimodal prompting with Gemini 1.5

[Gemini 1.5 Pro and 1.5 Flash](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models) models supports adding image, audio, video, and PDF files in text or chat prompts to generate a text or code response. Gemini 1.5 Pro supports up to 2 Million input tokens, making it possible to analyze long videos and audio files in a single prompt. This folder has examples to demonstrate multimodal capabilities of Gemini 1.5 and how to effectively write prompts for better results. 

### [Multimodal Prompting for Images](multimodal_prompting_image.ipynb)
Demonstrate prompting recipes and strategies for working with Gemini on images:
- Image Understanding
- Using system instruction
- Structuring prompt with images
- Adding few-shot examples the image prompt
- Document understanding
- Math understanding

### [Multimodal Prompting for Audio](multimodal_prompting_audio.ipynb)
Demonstrate prompting recipes and strategies for working with Gemini on audio files:
- Audio Understanding
- Effective prompting
- Key event detection
- Using System instruction
- Generating structured output

### [Multimodal Prompting for Videos](multimodal_prompting_video.ipynb)
Demonstrate prompting recipes and strategies for working with Gemini on video files:
- Video Understanding
- Key event detection
- Using System instruction
- Analyzing videos with step-by-step reasoning
- Generating structured output
- Using context caching for repeated queries