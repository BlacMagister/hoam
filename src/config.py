import os

class Config:
    DIFFICULTY = int(os.getenv("DIFFICULTY", 4))
    PORT = int(os.getenv("PORT", 8080))
    PEERS = os.getenv("PEERS", "").split(",")
    MINING_REWARD = 10.0
    VERSION = "1.0.0-future"
