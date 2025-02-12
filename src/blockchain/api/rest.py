from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
import logging

# Initialize FastAPI app
app = FastAPI(
    title="Blockchain Node API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

router = APIRouter()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionRequest(BaseModel):
    sender: str
    receiver: str
    amount: float
    signature: str

@router.get("/blocks/latest", response_model=dict)
async def get_latest_block():
    try:
        latest_block = {
            "hash": blockchain.last_block.hash.hex(),
            "height": blockchain.height,
            "transactions": len(blockchain.last_block.transactions)
        }
        return latest_block
    except Exception as e:
        logger.error(f"Error fetching latest block: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/transactions", status_code=201)
async def submit_transaction(tx: TransactionRequest):
    try:
        if not blockchain.validator.validate_transaction(tx.dict()):
            raise HTTPException(status_code=400, detail="Invalid transaction")
        blockchain.unconfirmed_transactions.append(tx.dict())
        logger.info("Transaction accepted")
        return {"status": "Transaction accepted"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error submitting transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/network/peers", response_model=List[str])
async def get_peers():
    try:
        peers = list(network.peers)
        return peers
    except Exception as e:
        logger.error(f"Error fetching network peers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

app.include_router(router, prefix="/api/v1")

def run_api(host: str = "0.0.0.0", port: int = 8080):
    uvicorn.run(app, host=host, port=port)
