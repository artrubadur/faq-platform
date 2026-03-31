from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.dialogs.actions import SendAction
from app.dialogs.send.public.start import send_start
from app.repositories import QuestionsRepository
from app.repositories.users import UsersRepository
from app.services.question.service import QuestionsService
from app.services.user.service import UsersService
from app.storage.instance import async_session
from app.storage.models.user import Role

router = Router()


@router.message(CommandStart())
async def cmd_handler(message: Message):
    async with async_session() as session:
        questions_repo = QuestionsRepository(session)
        questions_service = QuestionsService(questions_repo)
        try:
            questions = await questions_service._get_most_popular_questions(7)
        except Exception:
            logger.exception("Failed to fetch popular questions")
            questions = []

    await send_start(message, SendAction.ANSWER, message, questions)

    async with async_session() as session:
        users_repo = UsersRepository(session)
        users_service = UsersService(users_repo)
        try:
            tg_user = message.from_user
            db_user = await users_service.create_user(
                tg_user.id, tg_user.username, Role.USER
            )
            logger.debug("Newbie created", id=db_user.id, tg_id=db_user.telegram_id)
        except IntegrityError:
            pass
