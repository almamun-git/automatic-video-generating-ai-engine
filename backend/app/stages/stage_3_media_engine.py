import os
import requests
import logging
from app.config import PEXELS_API_KEY, ELEVENLABS_API_KEY

DEV_FALLBACK_MODE = (
    os.getenv("AUTOVIDAI_DEV_MODE", "").lower() in {"1", "true", "yes"}
    or not PEXELS_API_KEY or (isinstance(PEXELS_API_KEY, str) and PEXELS_API_KEY.startswith("dev_"))
    or not ELEVENLABS_API_KEY or (isinstance(ELEVENLABS_API_KEY, str) and ELEVENLABS_API_KEY.startswith("dev_"))
)

# Allow placeholders in Stage 3 even in prod to avoid total pipeline failure if a single provider fails
ALLOW_PLACEHOLDER = os.getenv("STAGE3_ALLOW_PLACEHOLDER", "1").lower() in {"1", "true", "yes"}

def _simplify_query(q: str) -> str:
    q = q or ""
    # Remove known prefixes and keep first 5 words for better Pexels matching
    q = q.replace("B-roll illustrating:", "").replace("Dynamic macro shot related to", "").strip()
    words = q.split()
    return " ".join(words[:5]) or "nature"

def get_video_from_pexels(query: str, scene_index: int) -> dict:
    print(f"  - Searching Pexels for video: '{query}'")
    if DEV_FALLBACK_MODE:
        # Return a public sample video URL suitable for testing.
        url = "https://www.w3schools.com/html/mov_bbb.mp4"
        print(f"    -> ⚙️ Dev fallback video: {url}")
        return {"video_url": url, "fallback": True}
    headers = {'Authorization': PEXELS_API_KEY}
    # Try simplified query first with a few candidates
    simple = _simplify_query(query)
    params = {'query': simple,'per_page': 5}
    try:
        response = requests.get('https://api.pexels.com/videos/search', headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('videos'):
            # Prefer vertical HD then any HD then first available
            for video in data['videos']:
                video_files = video.get('video_files', [])
                # vertical hd
                for vf in video_files:
                    if vf.get('quality') == 'hd' and vf.get('width',0) < vf.get('height',0):
                        url = vf.get('link'); print(f"    -> ✅ Found vertical HD: {url}"); return {"video_url": url}
                # any hd
                for vf in video_files:
                    if vf.get('quality') == 'hd':
                        url = vf.get('link'); print(f"    -> ✅ Found HD: {url}"); return {"video_url": url}
                # any
                if video_files:
                    url = video_files[0].get('link'); print(f"    -> ✅ Found video: {url}"); return {"video_url": url}
        print(f"    -> ⚠️ No suitable video found on Pexels for query: '{query}'")
        if ALLOW_PLACEHOLDER:
            url = "https://www.w3schools.com/html/mov_bbb.mp4"
            print(f"    -> 🔁 Using placeholder video: {url}")
            return {"video_url": url, "placeholder": True}
        return {"error": "No video found on Pexels"}
    except requests.RequestException as e:
        print(f"    -> ❌ Pexels API Error: {e}")
        if ALLOW_PLACEHOLDER:
            url = "https://www.w3schools.com/html/mov_bbb.mp4"
            print(f"    -> 🔁 Using placeholder video due to error: {url}")
            return {"video_url": url, "placeholder": True}
        return {"error": "Pexels API request failed", "details": str(e)}

def get_audio_from_elevenlabs(text: str, scene_index: int) -> dict:
    print(f"  - Generating TTS audio for: '{text[:50]}...'")
    if DEV_FALLBACK_MODE:
        # For dev, pretend an audio file exists; create a short silent file locally.
        os.makedirs('temp', exist_ok=True)
        audio_filename = f"temp/audio_scene_{scene_index}.mp3"
        try:
            if not os.path.exists(audio_filename):
                # Write a tiny placeholder file
                with open(audio_filename, 'wb') as f:
                    f.write(b"ID3\x04\x00\x00\x00\x00\x00\x0Fsimulated")
        except Exception as e:
            logging.debug("Could not create placeholder audio: %s", e)
        print(f"    -> ⚙️ Dev fallback audio: {audio_filename}")
        return {"audio_path": audio_filename, "fallback": True}
    voice_id = "21m00Tcm4TlvDq8ikWAM"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {'Accept': 'audio/mpeg','Content-Type': 'application/json','xi-api-key': ELEVENLABS_API_KEY}
    payload = {'text': text,'model_id': 'eleven_monolingual_v1','voice_settings': {'stability': 0.5,'similarity_boost': 0.75}}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        os.makedirs('temp', exist_ok=True)
        audio_filename = f"temp/audio_scene_{scene_index}.mp3"
        with open(audio_filename, 'wb') as f: f.write(response.content)
        print(f"    -> ✅ TTS audio saved: {audio_filename}")
        return {"audio_path": audio_filename}
    except requests.RequestException as e:
        print(f"    -> ❌ ElevenLabs API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"      -> Response: {e.response.text}")
        if ALLOW_PLACEHOLDER:
            os.makedirs('temp', exist_ok=True)
            audio_filename = f"temp/audio_scene_{scene_index}.mp3"
            try:
                with open(audio_filename, 'wb') as f:
                    f.write(b"ID3\x04\x00\x00\x00\x00\x00\x0Fplaceholder")
                print(f"    -> 🔁 Using placeholder audio: {audio_filename}")
                return {"audio_path": audio_filename, "placeholder": True}
            except Exception as ex:
                print(f"    -> ❌ Failed to write placeholder audio: {ex}")
        return {"error": "ElevenLabs API request failed", "details": str(e)}

def generate_media_assets(video_script: dict) -> list:
    scenes_with_assets = []
    for i, scene in enumerate(video_script["scenes"]):
        print(f"\nProcessing Scene {i+1}/{len(video_script['scenes'])}...")
        visual_query = scene.get("visual", "")
        video_result = get_video_from_pexels(visual_query, i)
        if "error" in video_result:
            print(f"  ⚠️ Skipping scene {i+1} due to video error."); continue
        narration_text = scene.get("narration", "")
        audio_result = get_audio_from_elevenlabs(narration_text, i)
        if "error" in audio_result:
            print(f"  ⚠️ Skipping scene {i+1} due to audio error."); continue
        scenes_with_assets.append({"visual": visual_query,"narration": narration_text,"video_url": video_result["video_url"],"audio_path": audio_result["audio_path"]})
        print(f"  ✅ Scene {i+1} assets ready.")
    return scenes_with_assets
