import asyncio
from types import SimpleNamespace

import pytest
from nicegui.testing import User
from sqlmodel import Session, select

from fastapi_sso.sso.google import GoogleSSO
from models import model_utils
from models.db_models import UserLogin
from test_signup import clean_db


async def _login_with_credentials(
    user: User, account: str = "testuser", password: str = "123123123"
) -> None:
    await user.open("/login")
    await user.should_see("login_tab")
    user.find("login_tab").click()
    await user.should_see("login_account")
    user.find("login_account").type(account)
    user.find("login_pw").type(password)
    user.find("login_button").click()
    await user.should_see("logout_btn")


@pytest.mark.anyio
async def test_login_sets_secure_session_cookie(user: User) -> None:
    """Local login should issue a dedicated session token cookie."""

    await clean_db(user)
    await _login_with_credentials(user)

    secure_cookie = user.http_client.cookies.get("rpg_session")

    assert secure_cookie, "expected login to set a signed session cookie"

    await asyncio.sleep(0.5)


@pytest.mark.anyio
async def test_google_callback_persists_identity(
    user: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Successful Google SSO should create a persisted login mapping."""

    await clean_db(user)

    fake_profile = SimpleNamespace(
        id="abc123", email="fake@example.com", name="Test User"
    )

    async def _fake_verify_and_process(self, request):  # noqa: ANN001, D401
        return fake_profile

    monkeypatch.setattr(
        GoogleSSO, "verify_and_process", _fake_verify_and_process, raising=False
    )

    response = await user.http_client.get(
        "/google/callback?code=fake", follow_redirects=True
    )
    assert response.status_code == 200

    with Session(model_utils.engine) as session:
        query = select(UserLogin).where(
            UserLogin.account_name == f"google:{fake_profile.id}"
        )
        persisted_login = session.exec(query).first()

    assert persisted_login is not None, (
        "expected Google login to persist a UserLogin record"
    )
