from fastapi import FastAPI

from database import engine, Base

from router import auth
from router import transactions

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(transactions.router)

@app.get("/")
def home():
    return {"message": "Expense Tracker API"}