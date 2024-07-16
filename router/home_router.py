from fastapi import APIRouter

router = APIRouter(
    tags=["HOME"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def read_root():
    return {"message": "Welcome to the MQTT Client API"}


