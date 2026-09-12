from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
    
class Loan(BaseModel):
    Age: int
    Income: float
    amount: float

@app.post("/predict")
def loan_take(application: Loan):
    
    if application.Age <18 or application.Income<=50000:
        decision = "Rejected"

    else:
        decision = "Aproved"
    
    print(f"You have been granted a loan of: {application.amount}")

    return {
        "Decision": decision,
        "Amount": application.amount
    }