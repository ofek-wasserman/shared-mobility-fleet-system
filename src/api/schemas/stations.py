from src.api.schemas.base import StrictBaseModel

class NearestStationResponse(StrictBaseModel):
    station_id: int
    lat: float
    lon: float
    
class ActiveUsersResponse(StrictBaseModel):
    user_id: list[int]