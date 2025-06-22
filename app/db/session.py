from sqlalchemy import create_engine

from app.env_data import get_env

engine = create_engine(
    f"postgresql://{get_env('PG_USER')}:{get_env('PG_PASSWORD')}@{get_env('PG_HOST')}:{get_env('PG_PORT')}/{get_env('PG_DATABASE')}",
    echo=True,
)
