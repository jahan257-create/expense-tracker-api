from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal
from router.auth import get_current_user


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)
user_dependency = Depends(get_current_user)


@router.post(
    "",
    response_model=schemas.TransactionResponse
)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = db_dependency,
    user: dict = user_dependency
):
    new_transaction = models.Transaction(
        title=transaction.title,
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category,
        date=transaction.date,
        owner_id=user.get("id")
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

@router.get("",
    response_model=list[schemas.TransactionResponse]
)
def get_transactions(
    db: Session = db_dependency,
    user: dict = user_dependency
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.owner_id == user.get("id")
    ).all()

    return transactions


@router.get(
    "/filter",
    response_model=list[schemas.TransactionResponse]
)
def filter_transactions(
    type: str | None = None,
    category: str | None = None,
    minimum_amount: float | None = None,
    maximum_amount: float | None = None,
    db: Session = db_dependency,
    user: dict = user_dependency
):
    query = db.query(models.Transaction).filter(
        models.Transaction.owner_id == user.get("id")
    )

    if type:
        query = query.filter(
            models.Transaction.type == type
        )

    if category:
        query = query.filter(
            models.Transaction.category == category
        )

    if minimum_amount is not None:
        query = query.filter(
            models.Transaction.amount >= minimum_amount
        )

    if maximum_amount is not None:
        query = query.filter(
            models.Transaction.amount <= maximum_amount
        )

    return query.all()
@router.get(
    "/{transaction_id}",
    response_model=schemas.TransactionResponse
)
def get_transaction(
    transaction_id: int,
    db: Session = db_dependency,
    user: dict = user_dependency
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).filter(
        models.Transaction.owner_id == user.get("id")
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction

@router.put(
    "/{transaction_id}",
    response_model=schemas.TransactionResponse
)
def update_transaction(
    transaction_id: int,
    transaction: schemas.TransactionUpdate,
    db: Session = db_dependency,
    user: dict = user_dependency
):
    existing_transaction = db.query(
        models.Transaction
    ).filter(
        models.Transaction.id == transaction_id
    ).filter(
        models.Transaction.owner_id == user.get("id")
    ).first()

    if not existing_transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    update_data = transaction.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(existing_transaction, key, value)

    db.commit()
    db.refresh(existing_transaction)

    return existing_transaction

@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = db_dependency,
    user: dict = user_dependency
):
    transaction = db.query(
        models.Transaction
    ).filter(
        models.Transaction.id == transaction_id
    ).filter(
        models.Transaction.owner_id == user.get("id")
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully"
    }