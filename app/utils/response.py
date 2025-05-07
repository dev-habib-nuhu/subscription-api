from flask import jsonify


def success_response(data=None, status=200, message="success"):
    response = {"status": "success", "message": message, "data": data}

    return jsonify(response), status


def error_response(message="error", status=400, errors=None):
    response = {
        "statuse": "error",
        "message": message,
        "errors": errors if errors else [],
    }
    return jsonify(response), status
