"""Tests for SafeArrayPagination (REVIEW C-3).

The global pagination class caps list responses at ``max_page_size``.
Responses remain plain arrays (no envelope) so frontends don't need to
change; an ``X-Has-More`` header signals truncation.
"""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, PartnerFactory, UserFactory


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestSafeArrayPagination:
    def test_response_is_array_not_envelope(self, api_client):
        """Backward compat: responses look like arrays, not {results: [...]}."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        PartnerFactory(company=company, name="A")
        PartnerFactory(company=company, name="B")
        auth(api_client, user)

        response = api_client.get("/api/v1/core/partners/")
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list), (
            f"Expected array response, got {type(body).__name__}"
        )
        assert len(body) == 2

    def test_emits_result_count_header(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        for i in range(3):
            PartnerFactory(company=company, name=f"P{i}")
        auth(api_client, user)

        response = api_client.get("/api/v1/core/partners/")
        assert response.headers.get("X-Result-Count") == "3"
        assert "X-Has-More" not in response.headers

    def test_caps_at_max_page_size_and_sets_x_has_more(
        self, api_client, settings
    ):
        from api.v1 import pagination

        # Shrink the cap for the test so we don't need 501 partners.
        original = pagination.SafeArrayPagination.max_page_size
        pagination.SafeArrayPagination.max_page_size = 5
        try:
            company = CompanyFactory()
            user = UserFactory(company=company)
            for i in range(10):
                PartnerFactory(company=company, name=f"P{i:02d}")
            auth(api_client, user)

            response = api_client.get("/api/v1/core/partners/")
            assert response.status_code == 200
            body = response.json()
            assert len(body) == 5
            assert response.headers.get("X-Result-Count") == "5"
            assert response.headers.get("X-Has-More") == "true"
        finally:
            pagination.SafeArrayPagination.max_page_size = original
