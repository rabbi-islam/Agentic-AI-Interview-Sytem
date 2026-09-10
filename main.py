from fastapi import FastAPI
from routers.interview import router as interview_router
app = FastAPI()
 

app.include_router(interview_router)

 