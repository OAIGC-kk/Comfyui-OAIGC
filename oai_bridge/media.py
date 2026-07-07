from __future__ import annotations

from io import BytesIO
from urllib.request import urlopen


async def _download_bytes(url: str) -> bytes:
    try:
        with urlopen(url, timeout=300) as response:
            return response.read()
    except Exception as exc:
        raise RuntimeError(f"下载结果失败：{exc}") from exc


async def download_image_url(url: str):
    import numpy as np
    import torch
    from PIL import Image

    data = await _download_bytes(url)
    image = Image.open(BytesIO(data))
    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        image = image.convert("RGBA")
    else:
        image = image.convert("RGB")
    arr = np.asarray(image).astype(np.float32) / 255.0
    return torch.from_numpy(arr).unsqueeze(0)


async def download_video_url(url: str):
    from comfy_api.latest import InputImpl

    data = BytesIO(await _download_bytes(url))
    data.seek(0)
    return InputImpl.VideoFromFile(data)

def image_tensor_to_png_bytes(image) -> bytes:
    import numpy as np
    from PIL import Image

    tensor = image[0] if len(image.shape) == 4 else image
    arr = (tensor.detach().cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
    out = BytesIO()
    Image.fromarray(arr).save(out, format="PNG")
    return out.getvalue()


async def upload_image_tensor(client, image, filename: str = "image.png") -> str:
    return await client.upload_file(filename, image_tensor_to_png_bytes(image), "image/png")

def video_input_to_mp4_bytes(video) -> bytes:
    out = BytesIO()
    try:
        from comfy_api.latest import Types
        container = Types.VideoContainer.MP4
    except (ImportError, ModuleNotFoundError, AttributeError):
        container = None
    if container is None:
        video.save_to(out)
    else:
        video.save_to(out, format=container)
    out.seek(0)
    return out.getvalue()



def audio_input_to_wav_bytes(audio) -> bytes:
    import wave
    import numpy as np

    waveform = audio["waveform"]
    sample_rate = int(audio["sample_rate"])
    if len(waveform.shape) == 3:
        waveform = waveform[0]
    samples = waveform.detach().cpu().numpy()
    samples = np.clip(samples, -1.0, 1.0)
    samples = (samples * 32767.0).astype(np.int16)
    samples = samples.T

    out = BytesIO()
    with wave.open(out, "wb") as wav:
        wav.setnchannels(samples.shape[1] if len(samples.shape) > 1 else 1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(samples.tobytes())
    out.seek(0)
    return out.getvalue()


async def upload_audio_input(client, audio, filename: str = "reference_audio.wav") -> str:
    return await client.upload_file(filename, audio_input_to_wav_bytes(audio), "audio/wav")

async def upload_video_input(client, video, filename: str = "reference_video.mp4") -> str:
    return await client.upload_file(filename, video_input_to_mp4_bytes(video), "video/mp4")






def save_video_bytes_to_output(url: str, filename_prefix: str = "OAI_Bridge") -> dict:
    import os
    import time

    import folder_paths

    output_dir = folder_paths.get_output_directory()
    subfolder = "OAI_Bridge"
    full_output_folder = os.path.join(output_dir, subfolder)
    os.makedirs(full_output_folder, exist_ok=True)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{stamp}.mp4"
    path = os.path.join(full_output_folder, filename)
    with open(path, "wb") as out:
        out.write(_download_bytes_sync(url))

    return {"filename": filename, "subfolder": subfolder, "type": "output", "format": "video/mp4"}


def _download_bytes_sync(url: str) -> bytes:
    try:
        with urlopen(url, timeout=300) as response:
            return response.read()
    except Exception as exc:
        raise RuntimeError(f"下载结果失败：{exc}") from exc