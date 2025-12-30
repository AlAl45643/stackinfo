from sqlalchemy import Text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, MappedAsDataclass
from enum import Enum


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class WorkdayURLs(Base):
    __tablename__ = "workday_urls"

    url: Mapped[str] = mapped_column(Text(), primary_key=True)


class YesOrNo(Enum):
    YES = 1
    NO = 0


class WorkdayRemoteYorN(Base):
    __tablename__ = "workday_remote_YorN"

    remote_text: Mapped[str] = mapped_column(Text(), primary_key=True)
    yes_or_no: Mapped[YesOrNo]


class GreenhouseURLs(Base):
    __tablename__ = "greenhouse_urls"

    url: Mapped[str] = mapped_column(Text(), primary_key=True)


class TechnologyCurrent(Base):
    __tablename__ = "technology_current"

    name: Mapped[str] = mapped_column(Text(), primary_key=True)

    count: Mapped[int] = mapped_column(Integer())


class StackCurrent(Base):
    __tablename__ = "stack_current"

    stack_id: Mapped[int] = mapped_column(Integer(), primary_key=True)

    count: Mapped[int] = mapped_column(Integer())


class TechnologyStackCurrent(Base):
    __tablename__ = "technology_stack_current"

    stack_id: Mapped[int] = mapped_column(Integer(), primary_key=True)

    name: Mapped[str] = mapped_column(Text(), primary_key=True)




