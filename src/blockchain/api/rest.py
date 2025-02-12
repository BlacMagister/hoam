from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Blockchain Node API",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

router = APIRouter(prefix="/api/v1")

class TransactionRequest(BaseModel):
    sender: str
    receiver: str
    amount: float
    signature: str

@router.get("/chain", tags=["Blockchain"])
async def get_chain(limit: int = 10):
    return {"height": chain.height, "blocks": chain.get_last_blocks(limit)}

@router.post("/transactions", tags=["Transactions"])
async def submit_transaction(tx: TransactionRequest):
    if chain.add_transaction(tx):
        return {"status": "queued"}
    return {"status": "rejected"}

@router.get("/network", tags=["Network"])
async def get_network_info():
    return {"peers": network.peers, "protocols": network.protocols}

app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_config="log_conf.yaml",
        timeout_keep_alive=300
    )
