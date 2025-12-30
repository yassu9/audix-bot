import aiohttp
from core.sound_result import SoundResult

class FreeSoundAPI:
    URL = "https://freesound.org/apiv2/search/text/"

    def __init__(self, api_key):
        self.api_key = api_key

    async def search(self, query, limit=10):
        headers = {"Authorization": f"Token {self.api_key}"}
        params = {
            "query": query,
            "page_size": limit,
            "fields": "name,previews,url"
        }

        async with aiohttp.ClientSession() as s:
            async with s.get(self.URL, headers=headers, params=params) as r:
                if r.status != 200:
                    return []

                data = await r.json()
                results = []

                for it in data.get("results", []):
                    previews = it.get("previews", {})
                    preview = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
                    if not preview:
                        continue  # quality filter

                    results.append(
                        SoundResult(
                            title=it["name"],
                            source="FreeSound",
                            preview_url=preview,
                            page_url=it["url"]
                        )
                    )
                return results