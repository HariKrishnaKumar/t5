from pydantic import BaseModel

class UserUpdatePreferences(BaseModel):
    preferences: str


class UserPreferencesResponse(BaseModel):
    id: int
    preferences: str | None = None

    class Config:
        from_attributes = True
