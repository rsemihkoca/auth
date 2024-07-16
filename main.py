from urllib.request import Request

from fastapi import HTTPException, Depends
from starlette.responses import JSONResponse

from config.env_config import EnvironmentConfig
from database.db import get_db, engine, Base, SessionLocal
from database.models import MQTTClient
import uvicorn
import datetime

from exception.exception import AbstractException
from factory import AppFactory, ExtendedFastAPI

Base.metadata.create_all(bind=engine)

factory: AppFactory = AppFactory()
app: ExtendedFastAPI = factory.get_app()


# Custom error handler for HTTPException
@app.exception_handler(AbstractException)
async def http_exception_handler(request: Request, exc: AbstractException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "details": exc.details, "error": exc.message},
    )


# Custom error handler for all other unhandled exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log the exception for debugging purposes
    print(f"Exception occurred: {exc}")

    # Return a generic error response
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "error": str(exc)},

    )

if __name__ == "__main__":
    app.logger.log(10, "MQTT client started")

    config = EnvironmentConfig()
    client_id = config.get('CLIENT_ID')
    username = config.get('USERNAME')
    password = config.get('PASSWORD')


    with SessionLocal() as db:
        db.query(MQTTClient).delete()
        new_client = MQTTClient(
            client_id=client_id,
            username=username,
            password=password,
            is_superuser=True,
            target="",
            is_disabled=False,
            last_update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.add(new_client)
        db.commit()

    uvicorn.run(app, host="0.0.0.0", port=8000)
