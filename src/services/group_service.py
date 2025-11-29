"""Service helpers for orchestrating group lifecycle and membership logic."""

import logging
import random
import string

from sqlmodel import Session, delete, select

from a_logger_setup import LOGGER_NAME
from models.db_models import (
    ConsentSheet,
    ConsentStatus,
    GroupConsentSheetLink,
    RPGGroup,
    User,
    UserGroupLink,
)
from models.model_utils import add_and_refresh, session_scope
from services.async_utils import run_sync
from services.service_utils import transactional
from services.sheet_service import create_consent_sheet
from utlis import sanitize_name

LOGGER = logging.getLogger(LOGGER_NAME)


@transactional
def get_group_by_id(group_id: int, session: Session | None = None) -> RPGGroup | None:
    """Return the group with the given primary key or ``None`` if not found."""
    LOGGER.debug("get_group_by_id %s", group_id)
    return session.get(RPGGroup, group_id)


@transactional
def fetch_group_sheets(group: RPGGroup, session: Session = None) -> list[ConsentSheet]:
    """Return all consent sheets attached to ``group``."""
    LOGGER.debug("fetch_group_sheets %s", group)
    return group.fetch_consent_sheets(session)


@transactional
def fetch_group_users(group: RPGGroup, session: Session = None) -> list[User]:
    """Return all users who are members of the supplied ``group``."""
    LOGGER.debug("fetch_group_users %s", group)
    return group.fetch_users(session)


@transactional
def get_group_by_name_id(group_name_id: str, session: Session = None) -> RPGGroup:
    """Resolve the composite ``name-id`` identifier used in the UI to a group."""
    LOGGER.debug("get_group_by_name_id %s", group_name_id)

    name, group_id = group_name_id.rsplit("-", 1)
    group = session.get(RPGGroup, int(group_id))
    if not group:
        groups = session.exec(select(RPGGroup)).all()
        for existing in groups:
            LOGGER.debug("%s", existing)
        raise ValueError(f"Invalid questioneer_id: {group_name_id}")

    normalized_expected = name.lower().replace(" ", "")
    normalized_actual = (group.name or "").lower().replace(" ", "")

    if group.invite_code == "global" and not group.gm_consent_sheet:
        gm_sheet = session.exec(
            select(ConsentSheet).where(ConsentSheet.user_id == group.gm_user_id)
        ).first()
        if gm_sheet:
            group.gm_consent_sheet = gm_sheet
            group.gm_consent_sheet_id = gm_sheet.id
            session.merge(group)
            session.merge(
                GroupConsentSheetLink(
                    group_id=group.id,
                    consent_sheet_id=gm_sheet.id,
                )
            )
            session.commit()
            session.refresh(group)

    if normalized_actual == normalized_expected:
        return group

    raise ValueError(f"Mismatch questioneer_id: {group_name_id}", group.name)


@transactional
def assign_consent_sheet_to_group(
    sheet: ConsentSheet, group: RPGGroup, session: Session = None
) -> RPGGroup:
    """Link ``sheet`` to ``group`` and return the updated group."""
    LOGGER.debug(
        "assign_consent_sheet_to_group %s <RPGGroup id=%s name=%s>",
        sheet,
        group.id,
        group.name,
    )

    db_group = session.get(RPGGroup, group.id)
    db_sheet = session.get(ConsentSheet, sheet.id)
    if not db_group or not db_sheet:
        raise ValueError("Unable to assign sheet to group; entity missing")

    session.merge(
        GroupConsentSheetLink(
            group_id=db_group.id,
            consent_sheet_id=db_sheet.id,
        )
    )
    session.commit()
    session.refresh(db_group)
    return db_group


@transactional
def unassign_consent_sheet_from_group(
    sheet: ConsentSheet, group: RPGGroup, session: Session = None
) -> RPGGroup:
    """Remove the association between ``sheet`` and ``group`` if present."""
    LOGGER.debug(
        "unassign_consent_sheet_from_group %s <RPGGroup id=%s name=%s>",
        sheet,
        group.id,
        group.name,
    )

    db_group = session.get(RPGGroup, group.id)
    db_sheet = session.get(ConsentSheet, sheet.id)
    if not db_group or not db_sheet:
        raise ValueError("Unable to unassign sheet from group; entity missing")

    link = session.exec(
        select(GroupConsentSheetLink).where(
            GroupConsentSheetLink.group_id == db_group.id,
            GroupConsentSheetLink.consent_sheet_id == db_sheet.id,
        )
    ).first()
    if link:
        session.delete(link)
        session.commit()
    else:
        LOGGER.warning(
            "no link found %s <RPGGroup id=%s name=%s>",
            sheet,
            group.id,
            group.name,
        )
    return db_group


@transactional
def create_new_group(
    user: User, sheet_id: int | None = None, session: Session = None
) -> RPGGroup:
    """Create a new group for ``user`` and seed it with a consent sheet."""
    LOGGER.debug("create_group %s", user)

    managed_user = session.get(User, user.id) or user
    sheet = (
        session.get(ConsentSheet, sheet_id)
        if sheet_id
        else create_consent_sheet(managed_user, session=session)
    )
    group = RPGGroup(
        name=sanitize_name(f"{managed_user.nickname}-Group"),
        gm_user_id=managed_user.id,
        gm_consent_sheet_id=sheet.id,
        gm_consent_sheet=sheet,
        invite_code=_generate_invite_code(None),
    )
    session.add(group)
    session.commit()
    session.add(GroupConsentSheetLink(group_id=group.id, consent_sheet_id=sheet.id))
    session.add(UserGroupLink(user_id=managed_user.id, group_id=group.id))
    session.commit()
    session.refresh(group)
    return regenerate_invite_code(group, session=session)


@transactional
def update_group(group: RPGGroup, session: Session = None) -> RPGGroup:
    """Persist display name updates for ``group`` and return the managed entity."""
    LOGGER.debug("update_group %s", group)

    group.name = sanitize_name(group.name)
    session.merge(group)
    session.commit()
    session.refresh(group)
    LOGGER.debug("merged %s", group)
    return group


@transactional
def regenerate_invite_code(group: RPGGroup, session: Session = None) -> RPGGroup:
    """Issue a fresh invite code for ``group`` and persist the change."""

    db_group = session.get(RPGGroup, group.id)
    if not db_group:
        raise ValueError("Group not found when regenerating invite code")
    LOGGER.debug("regenerate_invite_code %s", db_group)
    db_group.invite_code = _generate_invite_code(db_group.id)
    session.commit()
    session.refresh(db_group)
    LOGGER.debug("merged %s", db_group)
    return db_group


@transactional
def delete_group(group: RPGGroup, session: Session = None) -> RPGGroup:
    """Delete ``group`` and all associated membership and sheet links."""
    LOGGER.debug("delete_group %s", group)

    db_group = session.get(RPGGroup, group.id)
    if not db_group:
        raise ValueError("Group not found when deleting")
    session.exec(
        delete(GroupConsentSheetLink).where(
            GroupConsentSheetLink.group_id == db_group.id
        )
    )
    session.exec(delete(UserGroupLink).where(UserGroupLink.group_id == db_group.id))
    session.delete(db_group)
    session.commit()
    LOGGER.debug("deleted %s", db_group)
    return db_group


def ensure_global_group(session: Session) -> RPGGroup:
    """Create or return the shared "global" group used for open membership."""
    LOGGER.debug("ensure_global_group")
    if group := session.exec(
        select(RPGGroup).where(RPGGroup.invite_code == "global")
    ).first():
        return group

    global_gm_user = _get_or_create_global_gm_user(session)
    global_gm_sheet = _get_or_create_global_sheet(session, global_gm_user)

    group = RPGGroup(
        name="Global",
        gm_user_id=global_gm_user.id,
        gm_user=global_gm_user,
        gm_consent_sheet_id=global_gm_sheet.id,
        invite_code="global",
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


@transactional
def join_group(code: str, user: User, session: Session = None) -> RPGGroup | None:
    """Add ``user`` to the group identified by ``code`` if it exists."""
    LOGGER.debug("join_group <%s> invite_code=%s", user, code)

    managed_user = session.get(User, user.id)
    if managed_user is None:
        return None

    if code.lower() == "global":
        return _ensure_membership(
            managed_user,
            ensure_global_group(session),
            session,
        )

    group = session.exec(select(RPGGroup).where(RPGGroup.invite_code == code)).first()
    if group:
        return _ensure_membership(managed_user, group, session)

    LOGGER.debug("no group found %s", code)
    return None


@transactional
def leave_group(
    group: RPGGroup, user: User, session: Session = None
) -> RPGGroup | None:
    """Remove ``user`` from ``group`` and clean up any related sheet links."""
    LOGGER.debug("leave_group %s %s", group, user)

    db_group = session.get(RPGGroup, group.id)
    db_user = session.get(User, user.id)
    if not db_group or not db_user:
        return None

    session.exec(
        delete(UserGroupLink).where(
            UserGroupLink.user_id == db_user.id,
            UserGroupLink.group_id == db_group.id,
        ),
        execution_options={"is_delete_using": True},
    )
    group_sheet_links = session.exec(
        select(GroupConsentSheetLink).where(
            GroupConsentSheetLink.group_id == db_group.id,
            GroupConsentSheetLink.consent_sheet_id == ConsentSheet.id,
            ConsentSheet.user_id == db_user.id,
        )
    ).all()
    for link in group_sheet_links:
        session.delete(link)
    session.merge(db_group)
    session.commit()
    LOGGER.debug("left %s", db_group)
    return db_group


def _ensure_membership(user: User, group: RPGGroup, session: Session) -> RPGGroup:
    """Upsert the membership link between ``user`` and ``group``."""
    session.merge(
        UserGroupLink(
            user_id=user.id,
            group_id=group.id,
        )
    )
    session.commit()
    LOGGER.debug("joined %s", group)
    return group


def _get_or_create_global_gm_user(session: Session) -> User:
    """Return the synthetic Global GM user, creating it if missing."""
    global_gm_user = session.exec(
        select(User).where(User.id_name == "global_gm")
    ).first()
    if global_gm_user:
        return global_gm_user

    global_gm_user = User(
        id_name="global_gm",
        nickname="Global GM",
    )
    add_and_refresh(session, global_gm_user)
    return global_gm_user


def _get_or_create_global_sheet(session: Session, user: User) -> ConsentSheet:
    """Return the default consent sheet used by the Global GM."""
    existing_sheet = session.exec(
        select(ConsentSheet).where(ConsentSheet.user_id == user.id)
    ).first()
    if existing_sheet is not None:
        return existing_sheet

    sheet = create_consent_sheet(user, session=session)
    for entry in sheet.consent_entries:
        entry.preference = ConsentStatus.yes
    session.commit()
    session.refresh(sheet)
    return sheet


def _generate_invite_code(group_id: int | None) -> str:
    """Return a short invite code, prefixing the group id once available."""
    prefix = str(group_id) if group_id else "?"
    return "-".join(
        [
            prefix,
            "".join(random.choices(string.digits, k=3)),
            "".join(random.choices(string.digits, k=3)),
        ]
    )


# Async-friendly wrappers ---------------------------------------------------


async def get_group_by_id_async(group_id: int) -> RPGGroup | None:
    """Asynchronous wrapper for :func:`get_group_by_id`."""

    return await run_sync(get_group_by_id, group_id)


async def fetch_group_sheets_async(group: RPGGroup) -> list[ConsentSheet]:
    """Asynchronous wrapper for :func:`fetch_group_sheets`."""

    return await run_sync(fetch_group_sheets, group)


async def fetch_group_users_async(group: RPGGroup) -> list[User]:
    """Asynchronous wrapper for :func:`fetch_group_users`."""

    return await run_sync(fetch_group_users, group)


async def get_group_by_name_id_async(group_name_id: str) -> RPGGroup:
    """Asynchronous wrapper for :func:`get_group_by_name_id`."""

    return await run_sync(get_group_by_name_id, group_name_id)


async def assign_consent_sheet_to_group_async(
    sheet: ConsentSheet,
    group: RPGGroup,
) -> RPGGroup:
    """Asynchronous wrapper for :func:`assign_consent_sheet_to_group`."""

    return await run_sync(assign_consent_sheet_to_group, sheet, group)


async def unassign_consent_sheet_from_group_async(
    sheet: ConsentSheet,
    group: RPGGroup,
) -> RPGGroup:
    """Asynchronous wrapper for :func:`unassign_consent_sheet_from_group`."""

    return await run_sync(unassign_consent_sheet_from_group, sheet, group)


async def create_new_group_async(
    user: User,
    sheet_id: int | None = None,
) -> RPGGroup:
    """Asynchronous wrapper for :func:`create_new_group`."""

    return await run_sync(create_new_group, user, sheet_id)


async def update_group_async(group: RPGGroup) -> RPGGroup:
    """Asynchronous wrapper for :func:`update_group`."""

    return await run_sync(update_group, group)


async def regenerate_invite_code_async(group: RPGGroup) -> RPGGroup:
    """Asynchronous wrapper for :func:`regenerate_invite_code`."""

    return await run_sync(regenerate_invite_code, group)


async def delete_group_async(group: RPGGroup) -> RPGGroup:
    """Asynchronous wrapper for :func:`delete_group`."""

    return await run_sync(delete_group, group)


async def join_group_async(code: str, user: User) -> RPGGroup | None:
    """Asynchronous wrapper for :func:`join_group`."""

    return await run_sync(join_group, code, user)


async def leave_group_async(group: RPGGroup, user: User) -> RPGGroup | None:
    """Asynchronous wrapper for :func:`leave_group`."""

    return await run_sync(leave_group, group, user)
