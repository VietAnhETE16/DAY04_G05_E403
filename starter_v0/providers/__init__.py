from providers.gemini_provider import GeminiProvider


def make_provider(name: str = "gemini") -> GeminiProvider:
    if name != "gemini":
        raise ValueError("This project is configured to use the Gemini provider only.")
    return GeminiProvider()
