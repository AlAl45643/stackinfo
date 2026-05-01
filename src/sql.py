import datetime as dt
from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Text,
    create_engine,
    UniqueConstraint,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column
import os


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class WorkdayURLs(Base):
    __tablename__ = "workday_urls"

    url: Mapped[str] = mapped_column(Text(), primary_key=True)


class Locations(Base):
    __tablename__ = "locations"

    city: Mapped[str] = mapped_column(Text(), primary_key=True)
    state: Mapped[str] = mapped_column(Text(), primary_key=True)


class Tech(Base):
    __tablename__ = "tech"

    name: Mapped[str] = mapped_column(Text(), primary_key=True)
    case_sensitive: Mapped[bool] = mapped_column(Boolean())


class Tech_Parent_Tech(Base):
    __tablename__ = "tech_parent_tech"

    child_name: Mapped[str] = mapped_column(
        ForeignKey("tech.name", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    parent_name: Mapped[str] = mapped_column(
        ForeignKey("tech.name", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )


class Tech_Synonym(Base):
    __tablename__ = "tech_synonym"

    synonym: Mapped[str] = mapped_column(Text(), primary_key=True)
    name: Mapped[str] = mapped_column(
        ForeignKey("tech.name", onupdate="CASCADE", ondelete="CASCADE")
    )


class Tech_Count(Base):
    __tablename__ = "tech_count"
    __table_args__ = (
        UniqueConstraint("name", "city", "state", "date", name="uq_name_location_date"),
        ForeignKeyConstraint(
            ["city", "state"],
            ["locations.city", "locations.state"],
            name="fk_city_state",
        ),
    )

    id: Mapped[int | None] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )

    name: Mapped[str] = mapped_column(
        ForeignKey("tech.name", onupdate="CASCADE", ondelete="CASCADE")
    )
    city: Mapped[str] = mapped_column(Text())
    state: Mapped[str] = mapped_column(Text())
    count: Mapped[int] = mapped_column(Integer())
    date: Mapped[dt.date] = mapped_column(Date())


class Stack_Count(Base):
    __tablename__ = "stack_count"
    __table_args = (
        ForeignKeyConstraint(
            ["city", "state"],
            ["locations.city", "locations.state"],
            name="fk_city_state",
        ),
    )

    id: Mapped[int | None] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    city: Mapped[str] = mapped_column(Text())
    state: Mapped[str] = mapped_column(Text())
    count: Mapped[int] = mapped_column(Integer())
    date: Mapped[dt.date] = mapped_column(Date())


class Tech_Stack_Count(Base):
    __tablename__ = "tech_stack_count"

    stack_count_id: Mapped[int | None] = mapped_column(
        ForeignKey("stack_count.id", ondelete="CASCADE"), primary_key=True
    )
    name: Mapped[str] = mapped_column(
        ForeignKey("tech.name", onupdate="CASCADE"), primary_key=True
    )


user = os.getenv("DATABASE_USERNAME")
passw = os.getenv("DATABASE_PASSWORD")
name = os.getenv("DATABASE_NAME")
container = os.getenv("DATABASE_CONTAINER_NAME")
engine = create_engine(f"postgresql+psycopg2://{user}:{passw}@{container}:5432/{name}")
Base.metadata.create_all(engine)
