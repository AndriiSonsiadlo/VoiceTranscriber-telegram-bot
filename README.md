# 🎙️ Telegram Voice Transcriber Bot

A simple Telegram bot built with Python that automatically transcribes voice messages (and audio files) into text using speech-to-text APIs such as Whisper, Google Speech Recognition, or OpenAI Speech API.

## The bot can receive:
- 🔁 Forwarded messages containing voice notes
- 🎤 Directly recorded voice messages from users

## Once a voice note is received, the bot:
1. 🎧 Transcribes the audio
2. 🧠 Summarizes the transcription
3. 💬 Returns both the formatted transcription and a concise summary

The project is designed to be easily hosted on a serverless setup, making it lightweight and cost-efficient.
Python dependencies are managed using UV, providing reproducible environments and clean dependency control.
