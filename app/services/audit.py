from ..core.logging import logger

async def log_change(action: str, details: dict):
    logger.info("AUDIT %s - %s", action, details)
