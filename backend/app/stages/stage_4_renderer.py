import time
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

def render_video(scenes: list, title: str) -> dict:
    print("--- Stage 4: Renderer (Using Shotstack) ---")
    configuration = shotstack_sdk.Configuration(host="https://api.shotstack.io/" + SHOTSTACK_STAGE)
    with shotstack_sdk.ApiClient(configuration) as api_client:
        api_client.set_default_header('x-api-key', SHOTSTACK_API_KEY)
        api_instance = edit_api.EditApi(api_client)
        video_clips, audio_clips, caption_clips = [], [], []
        start_time = 0.0
        for scene in scenes:
            words_per_second = 2.5
            duration = max(len(scene["narration"].split()) / words_per_second, 3.0)
            video_clips.append(Clip(asset=VideoAsset(src=scene["video_url"], volume=0.0), start=start_time, length=duration))
            audio_clips.append(Clip(asset=AudioAsset(src=scene["audio_path"], volume=1.0), start=start_time, length=duration))
            caption_asset = TitleAsset(text=scene["narration"], style="subtitle")
            caption_clips.append(Clip(asset=caption_asset, start=start_time, length=duration))
            start_time += duration
        soundtrack = Soundtrack(src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", effect="fadeInFadeOut", volume=0.1)
        timeline = Timeline(background="#000000", tracks=[Track(clips=video_clips), Track(clips=audio_clips), Track(clips=caption_clips)], soundtrack=soundtrack)
        output = Output(format="mp4", resolution="1080")
        edit = Edit(timeline=timeline, output=output)
        try:
            print("Sending render request to Shotstack...")
            api_response = api_instance.post_render(edit)
            render_id = api_response['response']['id']
            print(f"Request accepted. Render ID: {render_id}")
            print("Waiting for render to complete... (this may take a few minutes)")
            while True:
                time.sleep(10)
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
