from rest_framework.views import exception_handler
import logging
from inventory_api.exceptions import InventoryError, PermissionDeniedError, ValidationError, NotFoundError, BusinessRuleError

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    logger = logging.getLogger('inventory')
    logger.error(f'Exception: {exc} | Context: {context}')
    if response is not None:
        response.data['status_code'] = response.status_code
        response.data['detail'] = str(exc)
    return response
