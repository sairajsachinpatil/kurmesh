import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Mission, Role, User

ModelT = TypeVar("ModelT")


class Repository(Generic[ModelT]):
    """Small persistence boundary; callers supply a transaction-owned session."""
    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session, self.model = session, model

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get(self, entity_id: uuid.UUID) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)


class UserRepository(Repository[User]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, User)

    def by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))


class RoleRepository(Repository[Role]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Role)

    def by_name(self, name: str) -> Role | None:
        return self.session.scalar(select(Role).where(Role.name == name))


class MissionRepository(Repository[Mission]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Mission)
