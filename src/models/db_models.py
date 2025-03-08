from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship, Session, select
from enum import Enum

LAZY_MODE = "selectin"


class GroupConsentSheetLink(SQLModel, table=True):
    group_id: int = Field(default=None, primary_key=True, foreign_key="rpggroup.id")
    consent_sheet_id: int = Field(
        default=None, primary_key=True, foreign_key="consentsheet.id"
    )


class UserGroupLink(SQLModel, table=True):
    user_id: int = Field(default=None, primary_key=True, foreign_key="user.id")
    group_id: int = Field(default=None, primary_key=True, foreign_key="rpggroup.id")


class ConsentStatus(str, Enum):
    yes = "yes"
    okay = "okay"
    maybe = "maybe"
    no = "no"
    unknown = "unknown"

    @property
    def as_emoji(self):
        return {
            ConsentStatus.yes: "🟢",
            ConsentStatus.okay: "🟡",
            ConsentStatus.maybe: "🟠",
            ConsentStatus.no: "❌",
            ConsentStatus.unknown: "❔",
        }[self]

    @property
    def order(self):
        return {
            ConsentStatus.yes: 0,
            ConsentStatus.okay: 1,
            ConsentStatus.maybe: 2,
            ConsentStatus.unknown: 3,
            ConsentStatus.no: 4,
        }[self]

    @staticmethod
    def get_consent(statuses: list["ConsentStatus"]):
        return (
            sorted(statuses, key=lambda x: x.order, reverse=True)[0]
            if statuses
            else ConsentStatus.unknown
        )

    @staticmethod
    def ordered() -> list["ConsentStatus"]:
        return sorted(list(ConsentStatus), key=lambda x: x.order, reverse=True)

    def explanation(self, lang: str = ""):
        if lang == "de":
            return self.explanation_de()
        return {
            ConsentStatus.yes: "I am fine with it. Lets go for it",
            ConsentStatus.okay: "It is okay but I do not need it",
            ConsentStatus.maybe: "It depends on the situation, other in the group or on the day, **ASK BEFORE** doing it",
            ConsentStatus.unknown: "I have not decided yet",
            ConsentStatus.no: "This is a **hard Limit**, do **NOT** do it",
        }[self]

    def explanation_de(self):
        return {
            ConsentStatus.yes: "Ich bin einverstanden. Lass uns das machen",
            ConsentStatus.okay: "Es ist okay, aber ich brauche es nicht",
            ConsentStatus.maybe: "Das hängt von der Situation, den Anderen in der Gruppe oder vom Tag ab, **FRAGE VORHER**, bevor du es tust",
            ConsentStatus.unknown: "Ich habe mich noch nicht entschieden",
            ConsentStatus.no: "Das ist ein **hartes Limit**, tu es **NICHT**",
        }[self]


class PlayFunQuestion(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    question_id: int = Field(default=None, foreign_key="localizedtext.id")
    question_local: "LocalizedText" = Relationship(
        sa_relationship_kwargs={"lazy": LAZY_MODE}
    )
    play_style: str = Field(default="")
    weight: float = Field(default=0)
    created_at: datetime = Field(default=datetime.now())


class PlayFunResult(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    challenge_rating: int = Field(default=0)
    discovery_rating: int = Field(default=0)
    expression_rating: int = Field(default=0)
    fantasy_rating: int = Field(default=0)
    fellowship_rating: int = Field(default=0)
    narrative_rating: int = Field(default=0)
    sensation_rating: int = Field(default=0)
    submission_rating: int = Field(default=0)
    user_id: int = Field(default=None, foreign_key="user.id")
    user: "User" = Relationship(sa_relationship_kwargs={"lazy": LAZY_MODE})
    created_at: datetime = Field(default=datetime.now())

    @staticmethod
    def categories(lang: str) -> list[str]:
        return (
            [
                "challenge",
                "discovery",
                "expression",
                "fantasy",
                "fellowship",
                "narrative",
                "sensation",
                "submission",
            ]
            if lang == "en"
            else [
                "Herausforderung",
                "Entdeckung",
                "Ausdruck",
                "Fantasie",
                "Gemeinschaft",
                "Erzählstruktur",
                "Sensation",
                "Zeitvertreib",
            ]
        )

    @property
    def ratings(self) -> dict[str, int]:
        return {
            "challenge": self.challenge_rating,
            "discovery": self.discovery_rating,
            "expression": self.expression_rating,
            "fantasy": self.fantasy_rating,
            "fellowship": self.fellowship_rating,
            "narrative": self.narrative_rating,
            "sensation": self.sensation_rating,
            "submission": self.submission_rating,
        }


class UserFAQ(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    question: str = Field(default=None)
    created_at: datetime = Field(default=datetime.now())


class UserContentQuestion(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    question: str = Field(default=None)
    created_at: datetime = Field(default=datetime.now())


class LocalizedText(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    text_en: str = Field(default=None, index=True)
    text_de: str | None = Field(default=None, index=True)

    def get_text(self, lang: str = ""):
        return self.text_de if lang == "de" else self.text_en


class FAQItem(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    question_id: int = Field(default=None, foreign_key="localizedtext.id")
    question_local: LocalizedText = Relationship(
        sa_relationship_kwargs={
            "lazy": LAZY_MODE,
            "foreign_keys": "[FAQItem.question_id]",
        }
    )
    answer_id: int = Field(default=None, foreign_key="localizedtext.id")
    answer_local: LocalizedText = Relationship(
        sa_relationship_kwargs={
            "lazy": LAZY_MODE,
            "foreign_keys": "[FAQItem.answer_id]",
        }
    )

    def __repr__(self):
        return f"<FAQItem {self.id} {self.question_local.get_text()[:20]}... -> {self.answer_local.get_text()[:20]}...>"


class ConsentTemplate(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    category_id: int = Field(default=None, foreign_key="localizedtext.id")
    category_local: LocalizedText = Relationship(
        sa_relationship_kwargs={
            "lazy": LAZY_MODE,
            "foreign_keys": "[ConsentTemplate.category_id]",
        }
    )
    topic_id: int = Field(default=None, foreign_key="localizedtext.id")
    topic_local: LocalizedText = Relationship(
        sa_relationship_kwargs={
            "lazy": LAZY_MODE,
            "foreign_keys": "[ConsentTemplate.topic_id]",
        }
    )
    explanation_id: int = Field(default=None, foreign_key="localizedtext.id")
    explanation_local: LocalizedText = Relationship(
        sa_relationship_kwargs={
            "lazy": LAZY_MODE,
            "foreign_keys": "[ConsentTemplate.explanation_id]",
        }
    )

    def __repr__(self):
        return f"<ConsentTemplate {self.id} {self.category} {self.topic}>"


class UserLogin(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    user: "User" = Relationship(sa_relationship_kwargs={"lazy": LAZY_MODE})
    account_name: str = Field(default=None, index=True, unique=True)
    password_hash: str = Field(default=None)

    def __repr__(self):
        return f"<UserLogin {self.id} user:{self.user_id} {self.user.nickname} {self.account_name}>"


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    id_name: str = Field(default=None, index=True, unique=True)
    nickname: str = Field(default=None)
    created_at: datetime = Field(default=datetime.now())
    last_login: datetime = Field(default=datetime.now())  # not used yet

    consent_sheets: list["ConsentSheet"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": LAZY_MODE},
        cascade_delete=True,
    )

    def fetch_groups(self, session: Session) -> list["RPGGroup"]:
        return session.exec(
            select(RPGGroup).where(
                UserGroupLink.user_id == self.id,
                RPGGroup.id == UserGroupLink.group_id,
            )
        ).all()

    def __repr__(self):
        return f"<User {self.id} {self.id_name} {self.nickname} [{len(self.consent_sheets)} sheets] >"

    def __str__(self):
        return f"<User {self.id} {self.id_name} {self.nickname} [{len(self.consent_sheets)} sheets] >"


class ConsentSheet(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    unique_name: str = Field(unique=True, index=True)
    human_name: str | None = Field(default=None)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())
    comment: str | None = Field(default=None)
    public_share_id: str | None = Field(
        default=None, description="if set, the sheet can be found by everyone"
    )
    consent_entries: list["ConsentEntry"] = Relationship(
        back_populates="consent_sheet",
        sa_relationship_kwargs={"lazy": LAZY_MODE},
        cascade_delete=True,
    )
    custom_consent_entries: list["CustomConsentEntry"] = Relationship(
        back_populates="consent_sheet",
        sa_relationship_kwargs={"lazy": LAZY_MODE},
        cascade_delete=True,
    )
    user_id: int = Field(default=None, foreign_key="user.id")
    user: User = Relationship(
        sa_relationship_kwargs={"lazy": LAZY_MODE}, back_populates="consent_sheets"
    )

    def fetch_groups(self, session: Session) -> list["RPGGroup"]:
        return session.exec(
            select(RPGGroup).where(
                GroupConsentSheetLink.consent_sheet_id == self.id,
                RPGGroup.id == GroupConsentSheetLink.group_id,
            )
        ).all()

    @property
    def consent_entries_dict(self):
        return {entry.consent_template_id: entry for entry in self.consent_entries}

    def get_entry(self, template_id: int) -> "ConsentEntry":
        return self.consent_entries_dict.get(template_id)

    @property
    def display_name(self):
        return self.human_name or self.unique_name

    def __str__(self):
        return f"<ConsentSheet {self.id} {self.unique_name} {len(self.consent_entries)} entries, Owner:{self.user.nickname}, shared:{self.public_share_id}>"


class ConsentEntry(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    consent_sheet_id: int = Field(default=None, foreign_key="consentsheet.id")
    consent_sheet: "ConsentSheet" = Relationship(
        back_populates="consent_entries", sa_relationship_kwargs={"lazy": LAZY_MODE}
    )
    consent_template_id: int = Field(default=None, foreign_key="consenttemplate.id")
    consent_template: "ConsentTemplate" = Relationship(
        sa_relationship_kwargs={"lazy": LAZY_MODE}
    )
    preference: ConsentStatus = Field(default=ConsentStatus.unknown)
    comment: str | None = Field(default=None)


class CustomConsentEntry(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    consent_sheet_id: int = Field(default=None, foreign_key="consentsheet.id")
    consent_sheet: "ConsentSheet" = Relationship(
        back_populates="custom_consent_entries",
        sa_relationship_kwargs={"lazy": LAZY_MODE},
    )
    content: str = Field(default=None)
    preference: ConsentStatus = Field(default=ConsentStatus.unknown)
    comment: str | None = Field(default=None)


class RPGGroup(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    invite_code: str = Field(default=None)
    gm_user_id: int = Field(default=None, foreign_key="user.id")
    gm_user: User = Relationship(sa_relationship_kwargs={"lazy": LAZY_MODE})
    gm_consent_sheet_id: int | None = Field(default=None, foreign_key="consentsheet.id")
    gm_consent_sheet: ConsentSheet | None = Relationship(
        sa_relationship_kwargs={"lazy": LAZY_MODE}
    )

    def fetch_consent_sheets(self, session: Session) -> list[ConsentSheet]:
        return session.exec(
            select(ConsentSheet).where(
                GroupConsentSheetLink.group_id == self.id,
                ConsentSheet.id == GroupConsentSheetLink.consent_sheet_id,
            )
        ).all()

    def fetch_users(self, session: Session) -> list[User]:
        return session.exec(
            select(User).where(
                UserGroupLink.group_id == self.id, User.id == UserGroupLink.user_id
            )
        ).all()

    def __str__(self):
        return f"<RPGGroup {self.id} {self.name} GM:{self.gm_user.nickname}>"

    def __repr__(self):
        return f"<RPGGroup {self.id} {self.name} GM:{self.gm_user.nickname}>"
