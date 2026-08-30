# FORGE — IVR Offline Fallback Demo Script

## Context
In remote connectivity dead zones at NRL Golaghat or along pipeline corridors, smartphones lose internet access. Field workers cannot upload files or send Telegram messages.

## Telephony IVR Flow
1. **Supervisor Calls Toll-Free Line**: Rahul dials the FORGE toll-free number from standard cellular voice network (2G/GSM).
2. **Audio Prompt**: *"Welcome to FORGE NRL Site Reporting. Please speak your zone, component, and completed activity after the tone."*
3. **Supervisor Speaks**: *"Sector B Pier 14 concrete pouring completed today."*
4. **Webhook Reception**: The telephony service (Twilio/Exotel) captures the call audio stream and delivers it to `/api/webhooks/twilio` or `/api/ingestion/upload` with `source: ivr` and `media_type: voice`.
5. **Pipeline Execution**: Whisper ASR transcribes the audio, extracts structured project attributes, matches against the schedule, and places the record in the Review Tray marked `Source: IVR / Dead-Zone Fallback`.
6. **Planner Visibility**: Priya sees the update with audio playback capability, approves it, and updates the master schedule without needing high-bandwidth site connectivity.
