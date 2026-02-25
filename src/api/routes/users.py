from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/register")
async def register_user():
    raise HTTPException(status_code=501, detail="Not implemented yet")