from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from router import url
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])
from dotenv import load_dotenv
load_dotenv()
import os
app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    logging.info("Application started successfully")
@app.on_event("shutdown")
def shutdown():
    logging.info("Application ended succesfully")
app.include_router(url.router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)