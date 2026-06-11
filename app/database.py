from config import settings
from sqlmodel import SQLModel, create_engine

sqlite_url = f"sqlite///{settings.sqlite_file_name}"

engine = create_engine(
    url=sqlite_url,
    connect_args={"check_same_thread": False},
    echo=settings.echo,
)


SQLModel.metadata.create_all(engine)
