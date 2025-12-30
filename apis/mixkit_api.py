from core.sound_result import SoundResult

class MixkitAPI:
    async def search(self, query, limit=2):
        return [
            SoundResult(
                title=f"{query.title()} (Mixkit)",
                source="Mixkit",
                preview_url=None,
                page_url="https://mixkit.co/free-sound-effects/"
            )
        ]