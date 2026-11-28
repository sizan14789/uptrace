import httpx


async def check_site(url: str, timeout_ms: int) -> dict:
    try:
        # creates and auto closes client, like file opening and closing in python
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=timeout_ms / 1000)
            return {
                "up": res.status_code < 400,
                "status_code": res.status_code,
                "error": None,
            }
    except Exception as e:  # noqa: BLE001
        return {"up": False, "status_code": None, "error": str(e)}
