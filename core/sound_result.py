class SoundResult:
    def __init__(self, title, preview_url, page_url, source):
        self.title = title
        self.preview_url = preview_url  # mp3 for Telegram preview
        self.page_url = page_url        # exact sound page
        self.source = source