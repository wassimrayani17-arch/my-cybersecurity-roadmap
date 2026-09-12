from fastapi import FastAPI
from app.routes import router1

app = FastAPI()

app.includerouter(router1)
