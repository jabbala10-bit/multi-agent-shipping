from policymesh.config import Settings


def test_settings_defaults_are_local_development_friendly():
    settings = Settings()

    assert settings.model
    assert settings.shopping_a2a_url.endswith("/a2a/shopping")
    assert settings.shipping_a2a_url.endswith("/a2a/shipping")
