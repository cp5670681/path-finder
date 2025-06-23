from datetime import datetime

from sqlmodel import SQLModel, Field, Session

from app.db.session import engine


class BaseModel(SQLModel):
    id: int = Field(primary_key=True, index=True, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def find(cls, id):
        with Session(engine) as session:
            return session.get(cls, id)
