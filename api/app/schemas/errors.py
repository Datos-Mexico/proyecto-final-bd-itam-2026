"""Modelos reutilizables para responses de error HTTP.

Forma del payload (consistente con FastAPI HTTPException(status_code, detail)):

    {"detail": "mensaje legible"}

Los validation errors 422 emitidos por Pydantic siguen un shape distinto
(lista de errores estructurados) y no se modelan aquí — FastAPI los registra
automáticamente vía HTTPValidationError.
"""
from pydantic import BaseModel, Field


class HTTPError(BaseModel):
    detail: str


class HTTPError401(HTTPError):
    detail: str = Field(
        default="Could not validate credentials",
        description="Token inválido, ausente o usuario inactivo.",
        examples=["Could not validate credentials"],
    )


class HTTPError403(HTTPError):
    detail: str = Field(
        default="Admin privileges required",
        description="Usuario autenticado pero sin permisos suficientes para la operación.",
        examples=["Admin privileges required"],
    )


class HTTPError404(HTTPError):
    detail: str = Field(
        default="Recurso no encontrado",
        description="El recurso solicitado no existe.",
        examples=["Persona no encontrada"],
    )


class HTTPError409(HTTPError):
    detail: str = Field(
        default="Cannot delete: resource has active references",
        description="Estado inconsistente: el recurso tiene referencias FK activas que impiden la operación.",
        examples=["Cannot delete persona with active nombramientos"],
    )


class HTTPError429(HTTPError):
    detail: str = Field(
        default="Rate limit exceeded. Try again later.",
        description="Rate limit por IP excedido para este endpoint.",
        examples=["Rate limit exceeded. Try again later."],
    )
