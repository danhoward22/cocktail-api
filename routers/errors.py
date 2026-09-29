from http import HTTPStatus

class APIError(Exception):
    def __init__(self, status_code: int, message: str, fields: dict[str, str] | None = None):
        self.status_code = status_code
        self.code = HTTPStatus(status_code).name
        self.message = message
        self.fields = fields

def error_body(status_code: int, message: str, fields: dict[str, str] | None = None) -> dict:
    body = {"code": HTTPStatus(status_code).name, "message": message}
    if fields:
        body["fields"] = fields
    return {"error": body}