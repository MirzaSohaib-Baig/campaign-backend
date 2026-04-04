from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.config.database_config import get_db


class BaseRepository:
    def __init__(self, model: None, db: Session = get_db) -> None:
        self.model = model
        self.db = db

    def create(self, schema):
        query = self.model(**schema.dict(exclude={"confirm_password"}))
        try:
            self.db.add(query)
            self.db.commit()
            self.db.refresh(query)
            return query
        except IntegrityError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise e

    def read_all(
        self, eager=False, order_by=None, limit: int = 10, page: int = 1, client: str = None,  **filters
    ):
        query = self.db.query(self.model)
        if eager:
            for eager in getattr(self.model, "eagers", []):
                query = query.options(joinedload(getattr(self.model, eager)))

        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
            
        if client and client.strip() and hasattr(self.model, "client"):
            query = query.filter(self.model.client == client)

        if order_by is not None:
            query = query.order_by(order_by)

        return query.limit(limit).offset((page - 1) * limit).all()

    def read_one(self, id: str = None, eager=False,):
        query = self.db.query(self.model)
        if eager:
            for eager in getattr(self.model, "eagers", []):
                query = query.options(joinedload(getattr(self.model, eager)))

        elif id is not None:
            query = query.filter(self.model.id == id)
        else:
            raise ValueError("Either id or patient_id must be provided")
        
        result = query.first()

        if not result:
            raise Exception(f"{self.model.__name__} with identifier not found")
        return result

    def update(self, schema, id: str = None ):
        query = self.read_one(id=id)
        for key, value in schema.dict(exclude_unset=True).items():
            setattr(query, key, value)
        self.db.commit()
        self.db.refresh(query)
        return query

    def delete(self, id: str):
        query = self.read_one(id)
        self.db.delete(query)
        self.db.commit()

    def read_where(self, **filters):
        query = self.db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.all()
