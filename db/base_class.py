from typing import Any

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative


@as_declarative()
class Base:
    id: Any
    metadata: Any
    __name__: str

    # to generate tablename from class name
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
