"""Error handling for OpenFisca MCP tools."""

from typing import Any


class MCPError(Exception):
    """Base error for MCP tool errors."""

    def __init__(
        self,
        error_type: str,
        message: str,
        code: int = 400,
        details: dict[str, Any] | None = None,
        suggestions: list[str] | None = None,
    ):
        self.error_type = error_type
        self.message = message
        self.code = code
        self.details = details or {}
        self.suggestions = suggestions or []
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "type": self.error_type,
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "suggestions": self.suggestions,
            }
        }


class ValidationError(MCPError):
    def __init__(self, message: str, details: dict[str, Any] | None = None, suggestions: list[str] | None = None):
        super().__init__("validation_error", message, 400, details, suggestions)


class NotFoundError(MCPError):
    def __init__(self, message: str, details: dict[str, Any] | None = None, suggestions: list[str] | None = None):
        super().__init__("not_found_error", message, 404, details, suggestions)


class ConnectionError(MCPError):
    def __init__(self, message: str, details: dict[str, Any] | None = None, suggestions: list[str] | None = None):
        super().__init__(
            "connection_error", message, 503, details,
            suggestions or ["Check that the OpenFisca server is running"],
        )


def format_api_error(response_data: dict, status_code: int) -> MCPError:
    if "error" in response_data and isinstance(response_data["error"], str):
        message = response_data["error"]
        if status_code == 404:
            return NotFoundError(message)
        return ValidationError(message)

    field_errors = {k: v for k, v in response_data.items() if "/" in k or k != "error"}
    if field_errors:
        first_path = next(iter(field_errors.keys()))
        return ValidationError(
            message=f"Validation error at {first_path}: {field_errors[first_path]}",
            details={"field_errors": field_errors},
            suggestions=["Check the field path and value format"],
        )

    return ValidationError("API returned an error", details={"raw_response": response_data})
