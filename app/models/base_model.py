from sqlmodel import SQLModel, Field, Session

from app.db.session import engine


class BaseModel(SQLModel):
    id: int = Field(primary_key=True, index=True, nullable=False)

    @classmethod
    def find(cls, id):
        with Session(engine) as session:
            return session.get(cls, id)
