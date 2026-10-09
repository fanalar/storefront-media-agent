"""FFmpeg-backed media probing and deterministic local composition."""
from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

from config import OUTPUT_DIR, ensure_runtime_dirs


VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


class VideoError(RuntimeError):
    pass


def _tool(name: str) -> str:
    bundled_dir = os.environ.get("STOREX_FFMPEG_DIR", "").strip()
    if bundled_dir:
        candidate = Path(bundled_dir) / (f"{name}.exe" if os.name == "nt" else name)
        if candidate.is_file():
            return str(candidate)
    return name


def _run(command: list[str], timeout: int = 600) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except FileNotFoundError as exc:
        raise VideoError(f"找不到 {command[0]}，请安装 FFmpeg 并加入 PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise VideoError("视频处理超时") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "未知错误").strip()[-1500:]
        raise VideoError(f"FFmpeg 执行失败：{detail}")
    return result


def probe_media(path: str | Path) -> dict[str, Any]:
    media_path = Path(path).expanduser().resolve()
    if not media_path.is_file():
        raise VideoError("素材文件不存在")
    result = _run(
        [
            _tool("ffprobe"),
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=index,codec_type,codec_name,width,height",
            "-of",
            "json",
            str(media_path),
        ],
        timeout=30,
    )
    payload = json.loads(result.stdout)
    payload["path"] = str(media_path)
    return payload


def _safe_output_name(value: str) -> str:
    stem = Path(value or f"作品_{uuid.uuid4().hex[:8]}.mp4").name
    stem = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "_", stem).strip("._")
    if not stem.lower().endswith(".mp4"):
        stem += ".mp4"
    return stem or f"作品_{uuid.uuid4().hex[:8]}.mp4"


def _ass_time(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, rest = divmod(centiseconds, 360000)
    minutes, rest = divmod(rest, 6000)
    secs, cs = divmod(rest, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def _ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}").replace("\n", r"\N")


def _write_ass(path: Path, shots: list[dict[str, Any]], title: str, font_size: int, color: str) -> bool:
    events: list[str] = []
    total = sum(float(shot.get("duration", 5)) for shot in shots)
    if title:
        events.append(f"Dialogue: 0,0:00:00.00,{_ass_time(min(total, 4))},Title,,0,0,0,,{_ass_escape(title)}")
    cursor = 0.0
    for shot in shots:
        duration = float(shot.get("duration", 5))
        script = str(shot.get("script", "")).strip()
        if script:
            events.append(
                f"Dialogue: 0,{_ass_time(cursor)},{_ass_time(cursor + duration)},Default,,0,0,0,,{_ass_escape(script)}"
            )
        cursor += duration
    if not events:
        return False
    bgr = color.lstrip("#")
    ass_color = f"&H00{bgr[4:6]}{bgr[2:4]}{bgr[0:2]}"
    content = "\n".join(
        [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "WrapStyle: 0",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            f"Style: Default,Microsoft YaHei,{font_size},{ass_color},&H000000FF,&HAA000000,&H66000000,0,0,0,0,100,100,0,0,1,3,1,2,70,70,150,1",
            f"Style: Title,Microsoft YaHei,{min(font_size + 16, 96)},{ass_color},&H000000FF,&HAA000000,&H66000000,-1,0,0,0,100,100,0,0,1,4,1,8,70,70,140,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
            *events,
        ]
    )
    path.write_text(content, encoding="utf-8-sig")
    return True


def _filter_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def compose_video(shots: list[dict[str, Any]], options: dict[str, Any], output_name: str = "", output_dir: str = "") -> dict[str, Any]:
    ensure_runtime_dirs()
    if not shots:
        raise VideoError("至少需要一个镜头")
    width, height = (720, 1280) if options.get("resolution") == "720p" else (1080, 1920)
    destination_dir = Path(output_dir).expanduser().resolve() if output_dir else OUTPUT_DIR
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / _safe_output_name(output_name)

    with tempfile.TemporaryDirectory(prefix="storex-mix-", dir=str(OUTPUT_DIR)) as temp_value:
        temp_dir = Path(temp_value)
        normalized: list[Path] = []
        for index, shot in enumerate(shots):
            source = Path(str(shot.get("path", ""))).expanduser().resolve()
            if not source.is_file():
                raise VideoError(f"第 {index + 1} 个素材不存在：{source}")
            if source.suffix.lower() not in VIDEO_EXTENSIONS | IMAGE_EXTENSIONS:
                raise VideoError(f"不支持的素材格式：{source.suffix}")
            duration = max(0.5, min(float(shot.get("duration", 5)), 600))
            segment = temp_dir / f"segment-{index:03d}.mp4"
            input_args = ["-loop", "1", "-t", str(duration), "-i", str(source)] if source.suffix.lower() in IMAGE_EXTENSIONS else ["-i", str(source), "-t", str(duration)]
            _run(
                [
                    _tool("ffmpeg"), "-y", *input_args,
                    "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,fps=30,format=yuv420p",
                    "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    str(segment),
                ]
            )
            normalized.append(segment)

        concat_list = temp_dir / "concat.txt"
        concat_list.write_text("\n".join(f"file '{str(path).replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'" for path in normalized), encoding="utf-8")
        merged = temp_dir / "merged.mp4"
        _run([_tool("ffmpeg"), "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(merged)])

        ass_path = temp_dir / "captions.ass"
        use_ass = _write_ass(
            ass_path,
            shots,
            str(options.get("title_text", "")),
            int(options.get("subtitle_font_size", 48)),
            str(options.get("subtitle_font_color", "#FFFFFF")),
        ) if options.get("subtitle_enabled") or options.get("title_text") else False

        bgm = Path(str(options.get("bgm_path", ""))).expanduser()
        command = [_tool("ffmpeg"), "-y", "-i", str(merged)]
        if bgm.is_file():
            command += ["-stream_loop", "-1", "-i", str(bgm.resolve())]
        else:
            command += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
        command += ["-map", "0:v:0", "-map", "1:a:0"]
        if use_ass:
            command += ["-vf", f"ass='{_filter_path(ass_path)}'", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23"]
        else:
            command += ["-c:v", "copy"]
        volume = max(0.0, min(float(options.get("bgm_volume", 0.25)), 1.0)) if bgm.is_file() else 0.0
        command += ["-filter:a", f"volume={volume}", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(destination)]
        _run(command)

    if not destination.is_file() or destination.stat().st_size < 1024:
        raise VideoError("合成结果为空")
    metadata = probe_media(destination)
    return {
        "success": True,
        "output_path": str(destination),
        "output_url": f"/output/{destination.name}",
        "metadata": metadata,
    }


async def compose_video_async(*args, **kwargs) -> dict[str, Any]:
    return await asyncio.to_thread(compose_video, *args, **kwargs)
