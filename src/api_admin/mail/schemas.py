from pydantic import BaseModel, ConfigDict
from typing import Optional


class TextMail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mail_text: str
    photo_url: Optional[str] = None