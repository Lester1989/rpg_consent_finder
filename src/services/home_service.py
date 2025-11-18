from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from sqlmodel import Session, select

from controller.sheet_controller import delete_sheet, import_sheet_from_json
from controller.user_controller import delete_account
from models.db_models import ConsentSheet, RPGGroup, User
from models.model_utils import session_scope
from services.async_utils import run_sync
from services.group_service import delete_group, join_group, leave_group


class HomeServiceError(RuntimeError):
    """Base class for recoverable dashboard failures."""


class UserNotFoundError(HomeServiceError):
    """Raised when the active session refers to a missing user."""


@dataclass(frozen=True)
class SheetGroupLink:
    """Projection of a group that references a consent sheet."""

    group_id: int
    name: str
    is_gm_group: bool


@dataclass(frozen=True)
class SheetSummary:
    """Renderable metadata for a consent sheet on the home dashboard."""

    id: int
    unique_name: str
    human_name: str | None
    public_share_id: str | None
    comment: str | None
    groups: tuple[SheetGroupLink, ...]

    @property
    def display_name(self) -> str:
        return self.human_name or self.unique_name

    @property
    def can_be_deleted(self) -> bool:
        return all(not group.is_gm_group for group in self.groups)

    @property
    def group_names(self) -> tuple[str, ...]:
        return tuple(group.name for group in self.groups)


@dataclass(frozen=True)
class GroupSummary:
    """Renderable metadata for a group listed on the home dashboard."""

    id: int
    name: str
    invite_code: str | None
    gm_consent_sheet_id: int | None
    is_user_gm: bool


@dataclass(frozen=True)
class HomeDashboard:
    """Aggregated information required to render the home page."""

    user_id_name: str
    nickname: str
    sheets: tuple[SheetSummary, ...]
    groups: tuple[GroupSummary, ...]

    @property
    def sheet_count(self) -> int:
        return len(self.sheets)


class HomeService:
    """Provide an async-friendly façade for home dashboard interactions."""

    async def load_dashboard(self, user_id_name: str) -> HomeDashboard:
        return await run_sync(self._load_dashboard, user_id_name)

    async def delete_sheet(self, user_id_name: str, sheet_id: int) -> None:
        await run_sync(self._delete_sheet, user_id_name, sheet_id)

    async def delete_group(self, user_id_name: str, group_id: int) -> None:
        await run_sync(self._delete_group, user_id_name, group_id)

    async def leave_group(self, user_id_name: str, group_id: int) -> None:
        await run_sync(self._leave_group, user_id_name, group_id)

    async def join_group(self, user_id_name: str, invite_code: str) -> None:
        await run_sync(self._join_group, user_id_name, invite_code)

    async def delete_account(self, user_id_name: str) -> None:
        await run_sync(self._delete_account, user_id_name)

    async def import_sheet(self, user_id_name: str, json_text: str) -> int:
        return await run_sync(self._import_sheet, user_id_name, json_text)

    def _load_dashboard(self, user_id_name: str) -> HomeDashboard:
        with session_scope() as session:
            user = self._require_user(session, user_id_name)
            sheets = tuple(self._gather_sheets(session, user))
            groups = tuple(self._gather_groups(session, user))
            return HomeDashboard(
                user_id_name=user.id_name,
                nickname=user.nickname or "",
                sheets=sheets,
                groups=groups,
            )

    def _delete_sheet(self, user_id_name: str, sheet_id: int) -> None:
        with session_scope() as session:
            user = self._require_user(session, user_id_name)
            sheet = session.get(ConsentSheet, sheet_id)
            if sheet is None:
                raise HomeServiceError("Consent sheet not found.")
            delete_sheet(user, sheet, session)

    def _delete_group(self, user_id_name: str, group_id: int) -> None:
        with session_scope() as session:
            user = self._require_user(session, user_id_name)
            group = session.get(RPGGroup, group_id)
            if group is None:
                raise HomeServiceError("Group not found.")
            if group.gm_user_id != user.id:
                raise HomeServiceError("Only the GM can delete this group.")
            delete_group(group, session=session)

    def _leave_group(self, user_id_name: str, group_id: int) -> None:
        with session_scope() as session:
            user = self._require_user(session, user_id_name)
            group = session.get(RPGGroup, group_id)
            if group is None:
                raise HomeServiceError("Group not found.")
            if group.gm_user_id == user.id:
                raise HomeServiceError(
                    "The GM must delete the group instead of leaving it."
                )
            leave_group(group, user, session=session)

    def _join_group(self, user_id_name: str, invite_code: str) -> None:
        with session_scope(autoflush=False) as session:
            user = self._require_user(session, user_id_name)
            if not invite_code:
                raise HomeServiceError("Provide a group invite code.")
            joined = join_group(invite_code, user, session=session)
            if joined is None:
                raise HomeServiceError("Invite code not recognised.")

    def _delete_account(self, user_id_name: str) -> None:
        with session_scope() as session:
            user = self._require_user(session, user_id_name)
            delete_account(user, session=session)

    def _import_sheet(self, user_id_name: str, json_text: str) -> int:
        with session_scope() as session:
            user = self._require_user(session, user_id_name)
        return import_sheet_from_json(json_text, user)

    @staticmethod
    def _require_user(session: Session, user_id_name: str) -> User:
        user = session.exec(select(User).where(User.id_name == user_id_name)).first()
        if user is None:
            raise UserNotFoundError("User session is no longer valid.")
        return user

    @staticmethod
    def _gather_sheets(session: Session, user: User) -> Iterable[SheetSummary]:
        sheet_rows: Sequence[ConsentSheet] = session.exec(
            select(ConsentSheet).where(ConsentSheet.user_id == user.id)
        ).all()
        for sheet in sheet_rows:
            sheet_groups = sheet.fetch_groups(session)
            links = tuple(
                SheetGroupLink(
                    group_id=group.id,
                    name=group.name or "",
                    is_gm_group=group.gm_consent_sheet_id == sheet.id,
                )
                for group in sheet_groups
                if group is not None
            )
            yield SheetSummary(
                id=sheet.id,
                unique_name=sheet.unique_name,
                human_name=sheet.human_name,
                public_share_id=sheet.public_share_id,
                comment=sheet.comment,
                groups=links,
            )

    @staticmethod
    def _gather_groups(session: Session, user: User) -> Iterable[GroupSummary]:
        for group in user.fetch_groups(session):
            yield GroupSummary(
                id=group.id,
                name=group.name or "",
                invite_code=group.invite_code,
                gm_consent_sheet_id=group.gm_consent_sheet_id,
                is_user_gm=group.gm_user_id == user.id,
            )
