from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_current_user, verify_password
from app.database import get_session
from app.models.users import User
from app.schemas.auth import Token, UserCreate, UserResponse
from app.schemas.errors import HTTPError401

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=403,
    responses={
        403: {
            "description": "Registro deshabilitado actualmente. La route existe en el código pero está intencionalmente bloqueada.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": (
                            "Registration is currently disabled. Admin users are "
                            "created via CLI (see api/scripts/create_admin.py). "
                            "Contact project owner: df.avila.diaz@gmail.com"
                        )
                    }
                }
            },
        },
    },
    summary="Registro de usuarios — deshabilitado",
    description=(
        "Endpoint de registro de usuarios **intencionalmente deshabilitado**. "
        "La route existe en el código y siempre devuelve `403 Forbidden` con "
        "el mensaje correspondiente. Si en el futuro el observatorio decide "
        "abrir registro público, la route ya está lista en el contrato del "
        "API y sólo requiere reemplazar el cuerpo de la función por la "
        "lógica de creación. La provisión actual de cuentas admin se hace "
        "por CLI (`api/scripts/create_admin.py`); contacto: "
        "`df.avila.diaz@gmail.com`."
    ),
)
async def register(body: UserCreate, session: AsyncSession = Depends(get_session)):
    raise HTTPException(
        status_code=403,
        detail=(
            "Registration is currently disabled. Admin users are created via CLI "
            "(see api/scripts/create_admin.py). Contact project owner: "
            "df.avila.diaz@gmail.com"
        ),
    )


@router.post(
    "/token",
    response_model=Token,
    responses={
        200: {
            "description": "Token JWT bearer emitido. Vigencia: `ACCESS_TOKEN_EXPIRE_MINUTES` (default 30 minutos).",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {
            "model": HTTPError401,
            "description": "Credenciales incorrectas (usuario inexistente o password no coincide).",
            "content": {"application/json": {"example": {"detail": "Incorrect username or password"}}},
        },
    },
    summary="Obtener JWT por OAuth2 password flow",
    description=(
        "Autenticación por OAuth2 password flow. Recibe `username` y "
        "`password` como `application/x-www-form-urlencoded` y devuelve un "
        "JWT bearer con vigencia `ACCESS_TOKEN_EXPIRE_MINUTES` (default "
        "30 minutos). El token debe enviarse en endpoints autenticados como "
        "`Authorization: Bearer <token>`. Algoritmo de firma: `HS256` "
        "(simétrico, secret en variable de entorno `SECRET_KEY`)."
    ),
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.username})
    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        200: {
            "description": "Perfil del usuario autenticado.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "admin",
                        "email": "admin@datos-itam.org",
                        "is_active": True,
                        "is_admin": True,
                        "created_at": "2026-04-20T16:43:00Z",
                    }
                }
            },
        },
        401: {
            "model": HTTPError401,
            "description": "Token ausente, expirado, inválido, o usuario inactivo.",
        },
    },
    summary="Perfil del usuario autenticado",
    description=(
        "Devuelve el perfil del usuario asociado al JWT enviado en el "
        "header `Authorization`. Útil para que un cliente confirme la "
        "vigencia del token y obtenga su flag `is_admin`. No incluye el "
        "`hashed_password` ni datos sensibles."
    ),
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
