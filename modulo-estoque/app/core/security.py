from fastapi import Header, HTTPException
from jose import JWTError, jwt

from app.core.config import settings


def _extract_token(
    authorization: str | None, x_service_token: str | None
) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip() or None
    if x_service_token:
        return x_service_token.strip() or None
    return None


def require_core_token(
    authorization: str | None = Header(None, alias="Authorization"),
    x_service_token: str | None = Header(None, alias="X-Service-Token"),
):
    if not settings.AUTH_ENABLED:
        return

    token = _extract_token(authorization, x_service_token)
    if not token:
        raise HTTPException(status_code=401, detail="Não autorizado")

    secret = settings.CORE_JWT_SECRET or settings.SECRET_KEY
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.CORE_JWT_ALG])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Token inválido") from exc

    if settings.CORE_JWT_ISSUER and payload.get("iss") != settings.CORE_JWT_ISSUER:
        raise HTTPException(status_code=401, detail="Token inválido")
