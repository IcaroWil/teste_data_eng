from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String, Float

class Base(DeclarativeBase):
    pass

class Data(Base):
    __tablename__ = "data"
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), primary_key=True, index=True)
    wind_speed: Mapped[float] = mapped_column(Float, nullable=False)
    power: Mapped[float] = mapped_column(Float, nullable=False)
    ambient_temperature: Mapped[float] = mapped_column(Float, nullable=False)