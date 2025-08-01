
class InventoryError(Exception):
    """Base class for inventory-related exceptions."""
    pass

class StockNotAvailableError(InventoryError):
    def __init__(self, product, message="Stock not available"):
        self.product = product
        self.message = message
        super().__init__(self.message)

class PermissionDeniedError(InventoryError):
    def __init__(self, message="Permission denied"):
        self.message = message
        super().__init__(self.message)

class ValidationError(InventoryError):
    def __init__(self, message="Validation error"):
        self.message = message
        super().__init__(self.message)

class NotFoundError(InventoryError):
    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)

class BusinessRuleError(InventoryError):
    def __init__(self, message="Business rule violation"):
        self.message = message
        super().__init__(self.message)
