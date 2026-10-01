from fastapi import FastAPI

from app.controllers.alternative_controller import router as alternative_router
from app.controllers.question_controller import router as question_router
from app.controllers.question_package_controller import router as question_package_router
from app.core.config import settings
from app.core.exception_handlers import trivia_exception_handler
from app.core.exceptions import TriviaException

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="0.1.0",
)

app.include_router(question_package_router)
app.include_router(question_router)
app.include_router(alternative_router)
app.add_exception_handler(TriviaException, trivia_exception_handler)