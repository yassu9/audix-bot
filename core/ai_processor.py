from config import Config

class AudixAI:
    def __init__(self):
        self.enabled = bool(Config.OPENAI_API_KEY)
        if self.enabled:
            from openai import OpenAI
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def improve(self, text: str) -> str:
        if not self.enabled:
            return text
        try:
            r = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"Fix spelling and improve this sound effect search query, keep it short:\n{text}"
                }],
                max_tokens=20
            )
            return r.choices[0].message.content.strip()
        except:
            return text