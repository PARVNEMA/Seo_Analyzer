import pytest
from app.core.config import get_settings

def test_settings_loading():
    """Test that settings load correctly."""
    settings = get_settings()
    assert settings.APP_NAME == "FastAPI Template"
    assert settings.ENVIRONMENT in ["dev", "staging", "prod"]
    assert settings.API_V1_PREFIX == "/api/v1"
