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