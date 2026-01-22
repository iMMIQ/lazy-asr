"""
Base repository with common CRUD operations
"""
from typing import TypeVar, Generic, Type, Optional, List, Any

from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

# Generic type for model classes
ModelType = TypeVar("ModelType")
# Generic type for create/update schemas
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations

    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self, session: AsyncSession):
                super().__init__(User, session)
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Initialize repository

        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Get a single record by ID

        Args:
            id: Primary key value

        Returns:
            Model instance or None
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_field(
        self, field_name: str, value: Any
    ) -> Optional[ModelType]:
        """
        Get a single record by field value

        Args:
            field_name: Name of the field to query
            value: Value to match

        Returns:
            Model instance or None
        """
        field = getattr(self.model, field_name)
        result = await self.session.execute(
            select(self.model).where(field == value)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = None,
    ) -> List[ModelType]:
        """
        Get all records with pagination

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            order_by: Field name to order by (optional)

        Returns:
            List of model instances
        """
        query = select(self.model)

        if order_by:
            order_field = getattr(self.model, order_by, None)
            if order_field is not None:
                query = query.order_by(order_field)

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelType:
        """
        Create a new record

        Args:
            **kwargs: Field values for the new record

        Returns:
            Created model instance
        """
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        Update an existing record

        Args:
            id: Primary key value
            **kwargs: Field values to update

        Returns:
            Updated model instance or None if not found
        """
        # First check if exists
        obj = await self.get_by_id(id)
        if not obj:
            return None

        # Update fields
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: int) -> bool:
        """
        Delete a record

        Args:
            id: Primary key value

        Returns:
            True if deleted, False if not found
        """
        obj = await self.get_by_id(id)
        if not obj:
            return False

        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def count(self) -> int:
        """
        Count all records

        Returns:
            Number of records
        """
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count(self.model.id))
        )
        return result.scalar()

    async def exists(self, id: int) -> bool:
        """
        Check if a record exists

        Args:
            id: Primary key value

        Returns:
            True if record exists
        """
        return await self.get_by_id(id) is not None

    async def bulk_create(self, items: List[dict]) -> List[ModelType]:
        """
        Create multiple records

        Args:
            items: List of dictionaries with field values

        Returns:
            List of created model instances
        """
        objects = [self.model(**item) for item in items]
        self.session.add_all(objects)
        await self.session.flush()
        return objects
