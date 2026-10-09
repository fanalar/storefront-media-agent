from __future__ import annotations

import json
import subprocess

from video_service import compose_video, probe_media


def _make_clip(path, color: str):
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color}:s=320x240:d=1",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path),
        ],
        check=True,
        capture_output=True,
    )


def test_real_ffmpeg_compose(tmp_path):
    first = tmp_path / "first.mp4"
    second = tmp_path / "second.mp4"
    _make_clip(first, "red")
    _make_clip(second, "blue")
    result = compose_video(
        [
            {"path": str(first), "duration": 0.8, "script": "第一幕"},
            {"path": str(second), "duration": 0.8, "script": "第二幕"},
        ],
        {
            "resolution": "720p",
            "title_text": "门店故事",
            "subtitle_enabled": True,
            "subtitle_font_size": 36,
            "subtitle_font_color": "#FFFFFF",
            "bgm_path": "",
            "bgm_volume": 0.2,
        },
        "验收视频.mp4",
        str(tmp_path),
    )
    assert result["success"] is True
    output = tmp_path / "验收视频.mp4"
    assert output.stat().st_size > 1024
    metadata = probe_media(output)
    video = next(stream for stream in metadata["streams"] if stream["codec_type"] == "video")
    assert (video["width"], video["height"]) == (720, 1280)
