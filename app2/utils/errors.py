from fastapi import HTTPException

class CustomError(HTTPException):
    """ Custom error class for standardized error responses. """
    def __init__(self, status_code: int, message: str, details: dict = None):
        super().__init__(status_code=status_code, detail={"message": message, "errors": details or {}})

# Common errors
def error_400(message="Bad Request", details=None):
    raise CustomError(400, message, details)

def error_401(message="Unauthorized"):
    raise CustomError(401, message)

def error_403(message="Forbidden"):
    raise CustomError(403, message)

def error_404(message="Not Found"):
    raise CustomError(404, message)

def error_500(message="Internal Server Error"):
    raise CustomError(500, message)