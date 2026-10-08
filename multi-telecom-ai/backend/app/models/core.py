import uuid
from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    mobile_number: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="user")
    preferred_provider_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("providers.provider_id")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    provider_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("providers.provider_id"))
    plan_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("recharge_plans.plan_id"))
    mobile_number: Mapped[str] = mapped_column(String)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    data_limit_mb: Mapped[float | None] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class UsageRecord(Base):
    __tablename__ = "usage_records"

    usage_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    usage_date: Mapped[date] = mapped_column(Date)
    data_used_mb: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    call_minutes: Mapped[int] = mapped_column(BigInteger, default=0)
    sms_count: Mapped[int] = mapped_column(BigInteger, default=0)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)


class Recharge(Base):
    __tablename__ = "recharges"

    recharge_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    provider_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("providers.provider_id"))
    plan_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("recharge_plans.plan_id"))
    mobile_number: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    payment_method: Mapped[str] = mapped_column(String, default="SIMULATED")
    status: Mapped[str] = mapped_column(String, default="SUCCESS")
    transaction_id: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Complaint(Base):
    __tablename__ = "complaints"

    complaint_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    category: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String, default="MEDIUM")
    status: Mapped[str] = mapped_column(String, default="OPEN")
    category_confidence: Mapped[float | None] = mapped_column(Numeric(5, 4))
    assigned_to: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column()


class ChatHistory(Base):
    __tablename__ = "chat_history"

    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    role: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(String)
    confidence: Mapped[float | None] = mapped_column(Numeric(5, 4))
    tool_used: Mapped[str | None] = mapped_column(String)
    sources: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("source_table", "source_id"),
    )

    document_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_table: Mapped[str] = mapped_column(Text)
    source_id: Mapped[int] = mapped_column(BigInteger)
    provider_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("providers.provider_id")
    )
    title: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())