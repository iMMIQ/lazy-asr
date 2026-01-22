"""
CORS security tests - TDD Second Cycle
"""
import pytest
from fastapi.testclient import TestClient


class TestCORSSecurity:
    """Test CORS configuration for security"""

    def test_cors_configured_with_restricted_origins(self):
        """CORS should be configured with restricted origins, not wildcard"""
        from app.main import app
        from app.core.config import settings

        # Check that ALLOWED_ORIGINS is not a wildcard
        assert hasattr(settings, "ALLOWED_ORIGINS"), "ALLOWED_ORIGINS setting must exist"
        assert settings.ALLOWED_ORIGINS != ["*"], "ALLOWED_ORIGINS should not be wildcard for security"
        assert len(settings.ALLOWED_ORIGINS) > 0, "ALLOWED_ORIGINS should have at least one origin"

    def test_cors_restricts_methods(self):
        """CORS should restrict allowed methods"""
        from app.core.config import settings

        # Check that allowed methods are restricted
        assert hasattr(settings, "CORS_ALLOW_METHODS"), "CORS_ALLOW_METHODS setting must exist"
        assert settings.CORS_ALLOW_METHODS != ["*"], "CORS_ALLOW_METHODS should not be wildcard"
        assert "GET" in settings.CORS_ALLOW_METHODS, "GET should be allowed"
        assert "POST" in settings.CORS_ALLOW_METHODS, "POST should be allowed"

    def test_cors_restricts_headers(self):
        """CORS should restrict allowed headers"""
        from app.core.config import settings

        # Check that allowed headers are restricted
        assert hasattr(settings, "CORS_ALLOW_HEADERS"), "CORS_ALLOW_HEADERS setting must exist"
        assert settings.CORS_ALLOW_HEADERS != ["*"], "CORS_ALLOW_HEADERS should not be wildcard"

    def test_preflight_request_from_allowed_origin(self):
        """Preflight request from allowed origin should succeed"""
        from app.main import app

        client = TestClient(app)

        # This test will fail initially because we need to set up ALLOWED_ORIGINS
        response = client.options(
            "/api/v1/asr/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )

        # Should allow the origin
        assert response.status_code == 200
        assert "http://localhost:3000" in response.headers.get("access-control-allow-origin", "")

    def test_preflight_request_from_disallowed_origin_blocked(self):
        """Preflight request from disallowed origin should be blocked"""
        from app.main import app

        client = TestClient(app)

        response = client.options(
            "/api/v1/asr/health",
            headers={
                "Origin": "http://evil-site.com",
                "Access-Control-Request-Method": "GET",
            }
        )

        # Should NOT include the disallowed origin in headers
        allowed_origin = response.headers.get("access-control-allow-origin", "")
        assert "evil-site.com" not in allowed_origin
