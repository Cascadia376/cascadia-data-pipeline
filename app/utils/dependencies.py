from fastapi import Depends, HTTPException, status
from ..core.config import settings
from ..core.logging import logger

async def verify_write_allowed():
    if not settings.allow_writes:
        logger.warning("Write attempted but writes are disabled")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Writes are disabled")
    if settings.env == "prod" and not settings.backup_verified:
        logger.error("Backup not verified in production")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Backup not verified")
    return True
