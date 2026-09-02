import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

from endpoints import user_endpoints, media_endpoints

app = FastAPI()

app.include_router(user_endpoints.router)
app.include_router(media_endpoints.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
