from fastapi import APIRouter, Depends, HTTPException
import httpx

from license_gate import require_active_license
from schemas import ScriptInput


router = APIRouter()


@router.post("/script", dependencies=[Depends(require_active_license)])
async def generate_script(data: ScriptInput) -> dict:
    if not data.api_key:
        raise HTTPException(400, "请在本机安全设置中配置百炼 API Key")
    system_prompt = (
        "你是实体店短视频编导。输出约60秒、可直接拍摄的中文脚本。"
        "必须包含标题、开场钩子、3到6个分镜（画面、口播、时长）和结尾行动指引。"
        "不得捏造优惠、疗效或资质。"
    )
    user_prompt = (
        f"门店：{data.shop_name or '未填写'}\n"
        f"目标顾客：{data.audience or '本地顾客'}\n"
        f"表达风格：{data.style}\n"
        f"本期主题：{data.topic}"
    )
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers={"Authorization": f"Bearer {data.api_key}"},
                json={
                    "model": data.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            payload = response.json()
            script = payload["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, f"AI 服务返回错误：{exc.response.status_code}，请检查模型连接设置") from exc
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise HTTPException(502, "AI 服务调用失败，请检查模型连接和网络") from exc
    return {"success": True, "script": script, "model": data.model}
