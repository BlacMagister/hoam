from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(
    title="Blockchain Node API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

router = APIRouter()

class TransactionRequest(BaseModel):
    sender: str
    receiver: str
    amount: float
    signature: str

@router.get("/blocks/latest", response_model=dict)
async def get_latest_block():
    return {
        "hash": blockchain.last_block.hash.hex(),
        "height": blockchain.height,
        "transactions": len(blockchain.last_block.transactions)
    }

@router.post("/transactions", status_code=201)
async def submit_transaction(tx: TransactionRequest):
    if not blockchain.validator.validate_transaction(tx.dict()):
        raise HTTPException(status_code=400, detail="Invalid transaction")
    blockchain.unconfirmed_transactions.append(tx.dict())
    return {"status": "Transaction accepted"}

@router.get("/network/peers", response_model=List[str])
async def get_peers():
    return list(network.peers)

app.include_router(router, prefix="/api/v1")

def run_api(host: str = "0.0.0.0", port: int = 8080):
    uvicorn.run(app, host=host, port=port)
