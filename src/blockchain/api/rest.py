from fastapi import FastAPI, APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import uvicorn
from typing import List

app = FastAPI(
    title="Enterprise Blockchain API",
    description="Production-grade blockchain interface",
    version="2.1.0",
    docs_url="/explorer",
    redoc_url=None
)

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-KEY")

class TransactionRequest(BaseModel):
    sender: str
    receiver: str
    amount: float
    signature: str
    nonce: int

class BlockResponse(BaseModel):
    hash: str
    height: int
    miner: str
    timestamp: float
    difficulty: int

@router.get("/blocks/latest", response_model=BlockResponse)
async def get_latest_block():
    latest_block = blockchain.get_latest_block()
    return {
        "hash": latest_block.hash.hex(),
        "height": blockchain.height,
        "miner": latest_block.get_miner_address(),
        "timestamp": latest_block.header.timestamp,
        "difficulty": latest_block.header.difficulty
    }

@router.post("/transactions", status_code=202)
async def submit_transaction(tx: TransactionRequest, 
                           api_key: str = Security(api_key_header)):
    if not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if blockchain.submit_transaction(tx.dict()):
        return {"status": "queued"}
    raise HTTPException(status_code=400, detail="Invalid transaction")

@router.get("/network/peers", response_model=List[str])
async def get_connected_peers():
    return p2p_network.get_active_peers()

app.include_router(router, prefix="/api/v2")

def run_server(host: str = "0.0.0.0", port: int = 8080):
    uvicorn.run(
        app,
        host=host,
        port=port,
        ssl_keyfile="./key.pem",
        ssl_certfile="./cert.pem",
        timeout_keep_alive=300
    )
