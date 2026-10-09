"""Validated request models for the local API."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PersonaInput(StrictModel):
    name: str = Field(default="", max_length=80)
    shop_name: str = Field(default="", max_length=120)
    industry: str = Field(default="", max_length=80)
    story: str = Field(default="", max_length=5000)
    speaking_style: str = Field(default="", max_length=500)
    philosophy: str = Field(default="", max_length=1000)
    audience: str = Field(default="", max_length=1000)
    logo_path: str = Field(default="", max_length=1024)


class CategoryInput(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    root_dir: str = Field(min_length=1, max_length=1024)


class ShotInput(StrictModel):
    path: str = Field(min_length=1, max_length=2048)
    duration: float = Field(default=5.0, ge=0.5, le=600)
    script: str = Field(default="", max_length=3000)
    role: str = Field(default="", max_length=80)


class MixOptions(StrictModel):
    resolution: Literal["720p", "1080p"] = "1080p"
    title_text: str = Field(default="", max_length=200)
    subtitle_enabled: bool = False
    subtitle_font_size: int = Field(default=48, ge=18, le=96)
    subtitle_font_color: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    bgm_path: str = Field(default="", max_length=2048)
    bgm_volume: float = Field(default=0.25, ge=0, le=1)


class TemplateInput(StrictModel):
    name: str = Field(min_length=1, max_length=120)
    clips: list[ShotInput] = Field(default_factory=list, max_length=100)
    options: MixOptions = Field(default_factory=MixOptions)


class ComposeInput(StrictModel):
    template_id: int | None = Field(default=None, ge=1)
    shots: list[ShotInput] = Field(default_factory=list, max_length=100)
    options: MixOptions = Field(default_factory=MixOptions)
    output_name: str = Field(default="", max_length=180)

    @field_validator("output_name")
    @classmethod
    def safe_output_name(cls, value: str) -> str:
        if value and ("/" in value or "\\" in value or ".." in value):
            raise ValueError("输出文件名不能包含路径")
        return value


class BatchInput(StrictModel):
    template_ids: list[int] = Field(min_length=1, max_length=100)
    output_dir: str = Field(default="", max_length=1024)


class LicenseActivateInput(StrictModel):
    license_key: str = Field(min_length=20, max_length=2048)
    machine_id: str = Field(default="", max_length=256)


class PublishScheduleInput(StrictModel):
    video_path: str = Field(min_length=1, max_length=2048)
    title: str = Field(default="", max_length=200)
    platforms: list[str] = Field(min_length=1, max_length=8)
    topics: list[str] = Field(default_factory=list, max_length=30)
    schedule_time: datetime | None = None


class PublishAccountInput(StrictModel):
    platform: Literal["douyin", "wechat_channels", "kuaishou", "xiaohongshu"]
    account_name: str = Field(min_length=1, max_length=120)
    account_id: str = Field(default="", max_length=200)


class ScriptInput(StrictModel):
    topic: str = Field(min_length=1, max_length=500)
    shop_name: str = Field(default="", max_length=120)
    audience: str = Field(default="", max_length=500)
    style: str = Field(default="亲切、真实、有烟火气", max_length=300)
    api_key: str = Field(default="", max_length=1024)
    provider: Literal["dashscope"] = "dashscope"
    model: str = Field(default="qwen-plus", max_length=100)


class SettingsInput(BaseModel):
    model_config = ConfigDict(extra="allow")
    auto_start: bool | None = None
    minimize_to_tray: bool | None = None
    publish_interval: int | None = Field(default=None, ge=5, le=1440)
    theme: Literal["dark", "light"] | None = None
    language: str | None = Field(default=None, max_length=20)
    ai_provider: str | None = Field(default=None, max_length=50)
    ai_model: str | None = Field(default=None, max_length=100)

