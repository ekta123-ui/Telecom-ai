from sqlalchemy import BigInteger, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Provider(Base):
    __tablename__ = "providers"

    provider_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider_name: Mapped[str] = mapped_column(String)
    customer_care_number: Mapped[str | None] = mapped_column(String)
    customer_care_email: Mapped[str | None] = mapped_column(String)
    website: Mapped[str | None] = mapped_column(String)
    headquarters: Mapped[str | None] = mapped_column(String)
    launch_year: Mapped[int | None] = mapped_column(BigInteger)
    network_type: Mapped[str | None] = mapped_column(String)
    coverage_score: Mapped[float | None] = mapped_column(Float)


class RechargePlan(Base):
    __tablename__ = "recharge_plans"

    plan_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider_id: Mapped[int] = mapped_column(BigInteger)
    plan_name: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(BigInteger)
    data_per_day: Mapped[str | None] = mapped_column(String)
    validity_days: Mapped[int] = mapped_column(BigInteger)
    unlimited_calls: Mapped[str | None] = mapped_column(String)
    sms_per_day: Mapped[int | None] = mapped_column(BigInteger)
    ott_benefits: Mapped[str | None] = mapped_column(String)
    plan_category: Mapped[str | None] = mapped_column(String)


class TelecomFAQ(Base):
    __tablename__ = "telecom_faqs"

    faq_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider_id: Mapped[int | None] = mapped_column(BigInteger)
    category: Mapped[str | None] = mapped_column(String)
    question: Mapped[str] = mapped_column(String)
    answer: Mapped[str] = mapped_column(String)


class Troubleshooting(Base):
    __tablename__ = "troubleshooting"

    issue_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    issue_type: Mapped[str | None] = mapped_column(String)
    symptom: Mapped[str] = mapped_column(String)
    possible_cause: Mapped[str | None] = mapped_column(String)
    solution: Mapped[str] = mapped_column(String)gitgit