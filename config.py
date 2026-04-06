from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    group_chat_id: int
    group_thread_id: int = 0
    db_path: str
    admin_ids: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    # Функція для перетворення рядка на список чисел
    def get_admin_list(self) -> list[int]:
        return [int(x.strip()) for x in self.admin_ids.split(',')]

config = Settings()
