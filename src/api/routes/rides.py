from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/start")
async def start_ride():
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.post("/{ride_id}/end")
async def end_ride(ride_id: int):
    raise HTTPException(status_code=501, detail="Not implemented yet")