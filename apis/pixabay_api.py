import aiohttp
from core.sound_result import SoundResult

class PixabayAPI:
    URL = "https://pixabay.com/api/sounds/"

    def __init__(self, api_key):
        self.api_key = api_key

    async def search(self, query, limit=5):
        if not self.api_key:
            return []
        params = {"key": self.api_key, "q": query, "per_page": limit}
        out = []
        async with aiohttp.ClientSession() as s:
            async with s.get(self.URL, params=params) as r:
                if r.status != 200:
                    return []
                data = await r.json()
                for h in data.get("hits", []):
                    out.append(SoundResult(
                        title=h.get("tags","Pixabay sound"),
                        preview_url=None,                 # Pixabay preview on site
                        page_url=h.get("pageURL"),
                        source="Pixabay"
                    ))
        return out