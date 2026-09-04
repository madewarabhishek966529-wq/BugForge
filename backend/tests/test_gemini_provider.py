import pytest
from backend.app.ai.provider import get_ai_provider
from backend.app.ai.gemini_provider import GeminiProvider

@pytest.mark.anyio
async def test_gemini_provider_factory():
    provider = get_ai_provider("gemini")
    assert isinstance(provider, GeminiProvider)

@pytest.mark.anyio
async def test_gemini_provider_fallback_without_key():
    provider = GeminiProvider(api_key="")
    context = {
        "error_type": "TypeError",
        "message": "'NoneType' object is not subscriptable",
        "file_path": "src/user.py",
        "line_number": 42
    }
    result = await provider.analyze_bug(context)
    assert result["error_type"] == "TypeError"
    assert "GEMINI_API_KEY" in result["summary"]
    assert isinstance(result["facts"], list)
