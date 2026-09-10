from fastapi import APIRouter

router = APIRouter(
    prefix="/interview",
    tags=["interview"]
)


@router.get("/")
async def get_interview():
    return {"message": "Interview done"} 