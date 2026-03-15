import datetime as dt
from sqlalchemy import Boolean, Date, ForeignKey, Integer, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


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

    child_name: Mapped[str] = mapped_column(ForeignKey("tech.name"), primary_key=True)
    parent_name: Mapped[str] = mapped_column(ForeignKey("tech.name"), primary_key=True)


class Tech_Synonym(Base):
    __tablename__ = "tech_synonym"

    synonym: Mapped[str] = mapped_column(Text(), primary_key=True)
    name: Mapped[str] = mapped_column(ForeignKey("tech.name"))


class Tech_Count(Base):
    __tablename__ = "tech_count"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)

    name: Mapped[str] = mapped_column(ForeignKey("tech.name"))
    location: Mapped[str] = mapped_column(Text())
    count: Mapped[int] = mapped_column(Integer())
    date: Mapped[dt.datetime] = mapped_column(Date())


class Stack_Count(Base):
    __tablename__ = "stack_count"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    location: Mapped[str] = mapped_column(Text())
    count: Mapped[int] = mapped_column(Integer())
    date: Mapped[dt.datetime] = mapped_column(Date())


class Tech_Stack_Count(Base):
    __tablename__ = "tech_stack_count"

    stack_count_id: Mapped[int] = mapped_column(
        ForeignKey("stack_count.id"), primary_key=True
    )
    name: Mapped[str] = mapped_column(ForeignKey("tech.name"), primary_key=True)


engine = create_engine(
    "postgresql+psycopg2://dbuser:dbpassword@localhost:5432/stackinfo"
)
Base.metadata.create_all(engine)
