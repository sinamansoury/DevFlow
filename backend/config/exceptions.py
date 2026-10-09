from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)


    if response is None:
        return None

    error_data = response.data

    if isinstance(error_data, dict) and "detail" in error_data:
        message = str(error_data["detail"])
        errors = None
    else:
        message = "درخواست نامعتبر است."
        errors = error_data

    response.data = {
        "success": False,
        "status_code": response.status_code,
        "message": message,
        "errors": errors,
    }

    return response

