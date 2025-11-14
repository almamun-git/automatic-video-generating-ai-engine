import time
import os
import logging
from app.config import SHOTSTACK_API_KEY, SHOTSTACK_STAGE
from shotstack_sdk.api import edit_api
from shotstack_sdk.model.clip import Clip
from shotstack_sdk.model.track import Track
from shotstack_sdk.model.timeline import Timeline
from shotstack_sdk.model.output import Output
from shotstack_sdk.model.edit import Edit
from shotstack_sdk.model.video_asset import VideoAsset
from shotstack_sdk.model.audio_asset import AudioAsset
from shotstack_sdk.model.soundtrack import Soundtrack
from shotstack_sdk.model.title_asset import TitleAsset
import shotstack_sdk

DEV_FALLBACK_MODE = (
    os.getenv("AUTOVIDAI_DEV_MODE", "").lower() in {"1", "true", "yes"}
    or (not SHOTSTACK_API_KEY) or (isinstance(SHOTSTACK_API_KEY, str) and SHOTSTACK_API_KEY.startswith("dev_"))
)

def render_video(scenes: list, title: str) -> dict:
    fast_mode = os.getenv("FAST_MODE", "").lower() in {"1", "true", "yes"}
    print("--- Stage 4: Renderer (Using Shotstack) ---")
    logging.info("Shotstack environment: %s | fast_mode=%s", SHOTSTACK_STAGE, fast_mode)
    if DEV_FALLBACK_MODE:
        # Bypass Shotstack in dev; return a known public demo video URL.
        logging.warning("Dev fallback active for Stage 4 — skipping Shotstack render.")
        return {"final_video_url": "https://www.w3schools.com/html/mov_bbb.mp4", "fallback": True}
    configuration = shotstack_sdk.Configuration(host="https://api.shotstack.io/" + SHOTSTACK_STAGE)
    with shotstack_sdk.ApiClient(configuration) as api_client:
        api_client.set_default_header('x-api-key', SHOTSTACK_API_KEY)
        api_instance = edit_api.EditApi(api_client)
        video_clips, audio_clips, caption_clips = [], [], []
        start_time = 0.0
        # Optionally limit scenes and reduce duration in fast mode (sandbox credit-friendly)
        scene_iter = scenes[:3] if fast_mode else scenes
        for scene in scene_iter:
            words_per_second = 2.5
            base_duration = max(len(scene["narration"].split()) / words_per_second, 3.0)
            duration = min(base_duration, 4.0) if fast_mode else base_duration
            video_clips.append(Clip(asset=VideoAsset(src=scene["video_url"], volume=0.0), start=start_time, length=duration))
            audio_clips.append(Clip(asset=AudioAsset(src=scene["audio_path"], volume=1.0), start=start_time, length=duration))
            caption_asset = TitleAsset(text=scene["narration"], style="subtitle")
            caption_clips.append(Clip(asset=caption_asset, start=start_time, length=duration))
            start_time += duration
        soundtrack = None if fast_mode else Soundtrack(src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", effect="fadeInFadeOut", volume=0.1)
        tracks = [Track(clips=video_clips), Track(clips=audio_clips), Track(clips=caption_clips)]
        timeline = Timeline(background="#000000", tracks=tracks, soundtrack=soundtrack)
        output = Output(format="mp4", resolution="1080")
        edit = Edit(timeline=timeline, output=output)
        try:
            print("Sending render request to Shotstack...")
            api_response = api_instance.post_render(edit)
            render_id = api_response['response']['id']
            print(f"Request accepted. Render ID: {render_id}")
            print("Waiting for render to complete... (this may take a few minutes)")
            poll_interval = 6 if fast_mode else 10
            while True:
                time.sleep(poll_interval)
                status_response = api_instance.get_render(render_id)
                status = status_response['response']['status']
                print(f"  -> Current status: {status}")
                if status == 'done':
                    final_video_url = status_response['response']['url']
                    print("✅ Video rendered successfully!")
                    return {"final_video_url": final_video_url}
                elif status in ['failed', 'cancelled']:
                    error_message = status_response['response'].get('error', 'Unknown render failure.')
                    print(f"❌ Video rendering failed: {error_message}")
                    return {"error": "Shotstack rendering failed"}
        except Exception as e:
            print(f"❌ Error calling Shotstack API: {e}")
            return {"error": "Shotstack API request failed", "details": str(e)}
