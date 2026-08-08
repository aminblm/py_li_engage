import re
import httpx
import asyncio

from py_li_engage.constants.app_constants import AppConstants
from py_li_engage.constants.app_secrets import AppSecrets
from py_li_engage.constants.log_messages import LogMessages
from py_li_engage.config import logger


class CommentCleaner:
    def __init__(
        self,
        comment_clean_regex_unicode: str,
        quote_strip_pattern: str,
        dash_spacing_pattern: str,
    ) -> None:
        self.comment_clean_regex_unicode = comment_clean_regex_unicode
        self.quote_strip_pattern = quote_strip_pattern
        self.dash_spacing_pattern = dash_spacing_pattern

    def clean(self, raw_comment: str) -> str:
        logger.info(LogMessages.COMMENT_SERVICE_LOG_PREFIX + LogMessages.CLEANING_COMMENT_INFO)
        if not raw_comment:
            return ""
            
        emoji_regex: re.Pattern = re.compile(self.comment_clean_regex_unicode, re.UNICODE)
        cleaned: str = re.sub(self.quote_strip_pattern, "", raw_comment)
        cleaned = re.sub(self.dash_spacing_pattern, ", ", cleaned)
        cleaned = emoji_regex.sub("", cleaned)
        return cleaned.strip()


class GroqService:
    def __init__(
        self,
        api_key: str,
        comment_cleaner: CommentCleaner,
        groq_comment_prompt_template: str,
        groq_model_name: str,
        groq_role_user: str,
        groq_request_timeout_sec: float,
        groq_api_url: str,
    ) -> None:
        self.api_key = api_key
        self.comment_cleaner = comment_cleaner
        self.groq_comment_prompt_template = groq_comment_prompt_template
        self.groq_model_name = groq_model_name
        self.groq_role_user = groq_role_user
        self.groq_request_timeout_sec = groq_request_timeout_sec
        self.groq_api_url = groq_api_url

    async def generate_comment(self, post_content: str) -> str:
        logger.info(LogMessages.GROQ_SERVICE_LOG_PREFIX + LogMessages.GROQ_API_REQUEST_INFO)
        prompt: str = self.groq_comment_prompt_template.format(post_content=post_content)
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload: dict[str, str | list[dict[str, str]]] = {
            "model": self.groq_model_name,
            "messages": [{"role": self.groq_role_user, "content": prompt}],
        }

        try:
            async with httpx.AsyncClient(timeout=self.groq_request_timeout_sec) as client:
                response = await client.post(self.groq_api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                raw_comment: str = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                logger.info(LogMessages.GROQ_SERVICE_LOG_PREFIX + LogMessages.GROQ_API_SUCCESS_INFO)
                return self.comment_cleaner.clean(raw_comment)
        except Exception as error:
            logger.error(LogMessages.GROQ_SERVICE_LOG_PREFIX + LogMessages.GROQ_API_ERROR_ERROR.format(error))
            raise


# --- Live Testing Main Entrypoints ---

async def test_comment_cleaner() -> None:
    cleaner = CommentCleaner(
        comment_clean_regex_unicode=AppConstants.COMMENT_CLEAN_REGEX_UNICODE,
        quote_strip_pattern=AppConstants.QUOTE_STRIP_PATTERN,
        dash_spacing_pattern=AppConstants.DASH_SPACING_PATTERN
    )
    raw = '\"Great insights🔥 - loved it!\"'
    cleaned = cleaner.clean(raw_comment=raw)
    print(f"Cleaned Comment: {cleaned}")


async def test_groq_service() -> None:
    cleaner = CommentCleaner(
        comment_clean_regex_unicode=AppConstants.COMMENT_CLEAN_REGEX_UNICODE,
        quote_strip_pattern=AppConstants.QUOTE_STRIP_PATTERN,
        dash_spacing_pattern=AppConstants.DASH_SPACING_PATTERN,
    )
    groq_service = GroqService(
        api_key=AppSecrets.GROQ_API_KEY,
        comment_cleaner=cleaner,
        groq_comment_prompt_template=AppConstants.GROQ_COMMENT_PROMPT_TEMPLATE,
        groq_model_name=AppConstants.GROQ_MODEL_NAME,
        groq_role_user=AppConstants.GROQ_ROLE_USER,
        groq_request_timeout_sec=AppConstants.GROQ_REQUEST_TIMEOUT_SEC,
        groq_api_url=AppConstants.GROQ_API_URL,
    )
    post_text = "AI agents are transforming how we build backend software architectures."
    try:
        comment = await groq_service.generate_comment(post_content=post_text)
        print(f"Cleaned generated Groq Comment: {comment}")
    except Exception as e:
        print(f"Groq Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_comment_cleaner())
    asyncio.run(test_groq_service())