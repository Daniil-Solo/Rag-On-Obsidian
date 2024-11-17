from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from src.database.models import LLMSettingsModel
from src.repositories.settings.interface import SettingsRepository


class SettingsSQLAlchemyRepository(SettingsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_llm_settings(self) -> dict | None:
        statement = select(LLMSettingsModel).limit(1)
        result = await self.session.execute(statement)

        llm_settings = result.scalars().first()
        return llm_settings and llm_settings.model_dump()

    async def update_llm_settings(
        self,
        model_type: str,
        token: str,
        model_name: str,
        max_length: int,
    ) -> None:
        existing_settings = await self.get_llm_settings()
        if existing_settings is None:
            new_settings = LLMSettingsModel(
                model_type=model_type,
                token=token,
                model_name=model_name,
                max_length=max_length,
            )
            self.session.add(new_settings)
        else:
            statement = (
                update(LLMSettingsModel)
                .values(
                    model_type=model_type,
                    token=token,
                    model_name=model_name,
                    max_length=max_length,
                )
            )
            await self.session.execute(statement)

        await self.session.commit()
