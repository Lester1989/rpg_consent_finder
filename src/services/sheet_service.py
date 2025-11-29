"""Sheet-oriented business operations shared between UI and controllers."""

import logging
import random
import string
from typing import Callable

from sqlmodel import Session, select

from a_logger_setup import LOGGER_NAME
from models.db_models import ConsentEntry, ConsentSheet, ConsentTemplate, User

from services.service_utils import transactional

LOGGER = logging.getLogger(LOGGER_NAME)


@transactional
def create_consent_sheet(
    user: User,
    *,
    session: Session | None = None,
    unique_name_factory: Callable[[Session], str] | None = None,
) -> ConsentSheet:
    """Create a new consent sheet for the given user.

    The optional ``session`` argument allows composition in larger transactions.
    ``unique_name_factory`` enables deterministic testing.
    """
    managed_user = session.get(User, user.id)
    if managed_user is None:
        raise ValueError("User not found when creating consent sheet")

    name_factory = unique_name_factory or _generate_unique_name
    unique_name = name_factory(session)

    sheet = ConsentSheet(
        unique_name=unique_name,
        user_id=managed_user.id,
        user=managed_user,
    )
    managed_user.consent_sheets.append(sheet)
    session.add(sheet)
    session.commit()
    session.refresh(sheet)

    templates = session.exec(select(ConsentTemplate)).all()
    for template in templates:
        entry = ConsentEntry(
            consent_sheet_id=sheet.id,
            consent_sheet=sheet,
            consent_template_id=template.id,
            consent_template=template,
        )
        sheet.consent_entries.append(entry)
        session.add(entry)
    session.commit()
    session.refresh(sheet)
    session.merge(managed_user)
    session.commit()
    LOGGER.info("created consent sheet %s", sheet)
    return sheet


def _generate_unique_name(session: Session) -> str:
    """Return a random unique identifier not already used by any sheet."""
    existing = set(session.exec(select(ConsentSheet.unique_name)).all())
    while True:
        candidate = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        if candidate not in existing:
            existing.add(candidate)
            return candidate
