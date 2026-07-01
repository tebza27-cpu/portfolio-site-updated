from app import app
import traceback

with app.test_request_context('/projects'):
    try:
        response = app.full_dispatch_request()
        print('Response status:', response.status)
    except Exception:
        traceback.print_exc()
