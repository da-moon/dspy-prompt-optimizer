# AGENTS.md

This file provides comprehensive instructions for AI agents working on this Python codebase. Follow these guidelines strictly to maintain code quality and consistency.

## Python Coding Standards

### Type Annotations (MANDATORY)
- ALL functions, methods, and class attributes MUST have complete type annotations
- Use `-> None` for procedures that don't return values
- Use `Final[T]` for immutable class attributes and constants
- Use `Optional[T]` or `T | None` for nullable types (prefer `T | None` for Python 3.10+)
- Use `Union[T, U]` or `T | U` for multiple possible types
- Never use bare `Any` without explicit justification in comments
- Use `TypeVar` for generic types when appropriate

Example:
```python
from typing import Final, Optional, Union
from decimal import Decimal

class PaymentProcessor:
    MAX_AMOUNT: Final[Decimal] = Decimal('10000.00')
    
    def __init__(self, gateway: PaymentGateway) -> None:
        self._gateway: Final[PaymentGateway] = gateway
        self._processed_count: int = 0
    
    def process(self, amount: Optional[Decimal]) -> Union[PaymentResult, None]:
        # Implementation
        pass
```

### Code Style Requirements

#### Naming Conventions (Strictly Enforced)
- Classes: `PascalCase` (e.g., `PaymentProcessor`, `UserAccount`)
- Functions/methods: `snake_case` (e.g., `process_payment`, `validate_input`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`)
- Private attributes/methods: `_leading_underscore` (e.g., `_internal_state`, `_validate_token`)
- Protected attributes: `_single_underscore` for subclass access
- Name mangling: `__double_underscore` only when necessary to avoid conflicts
- Use descriptive names only - NO abbreviations (e.g., `user_manager` not `usr_mgr`)

#### Import Organization (Mandatory Order)
```python
# 1. Standard library imports (alphabetical)
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Final

# 2. Third-party packages (alphabetical)
import requests
from loguru import logger
from pydantic import BaseModel

# 3. Local application imports (alphabetical)
from myproject.core import models
from myproject.core.exceptions import PaymentError
from myproject.utils import helpers
```

#### Docstrings (Required for ALL public functions/classes/modules)
Use Google-style docstrings with complete type information:
```python
def process_payment(amount: Decimal, token: str, retry_count: int = 3) -> PaymentResult:
    """Process a single payment transaction with retry logic.

    This function validates the payment amount and token, then attempts to
    process the payment through the configured gateway. If the initial
    attempt fails, it will retry up to the specified number of times.

    Args:
        amount: Payment amount in decimal format. Must be positive and
            not exceed the maximum allowed amount.
        token: Payment authorization token from the payment provider.
            Must be a non-empty string.
        retry_count: Maximum number of retry attempts if processing fails.
            Defaults to 3. Must be non-negative.

    Returns:
        PaymentResult object containing transaction details including
        transaction ID, status, and timestamp.

    Raises:
        ValueError: If amount is negative, zero, or exceeds maximum limit.
        TypeError: If token is not a string or retry_count is not an integer.
        PaymentError: If payment processing fails after all retry attempts.
        NetworkError: If unable to connect to payment gateway.

    Example:
        >>> processor = PaymentProcessor(gateway)
        >>> result = processor.process_payment(Decimal('99.99'), 'tok_123')
        >>> print(result.transaction_id)
        'txn_456789'
    """
```

### Error Handling Pattern (Mandatory Implementation)

ALL public methods must implement this exact pattern:
```python
def process_data(self, data: Any, options: Optional[Dict[str, Any]] = None) -> ProcessResult:
    """Process input data with comprehensive error handling."""
    
    # 1. Input validation - fail fast with specific error messages
    if data is None:
        raise ValueError("Input data cannot be None")
    
    if options is None:
        options = {}
    
    # 2. Type checking with detailed error messages
    if not isinstance(data, (str, bytes, dict)):
        raise TypeError(
            f"Expected data to be str, bytes, or dict, got {type(data).__name__}"
        )
    
    # 3. Business rule validation
    if isinstance(data, str) and len(data) == 0:
        raise ValueError("String data cannot be empty")
    
    # 4. Business logic with specific exception handling
    try:
        validated_data = self._validate_data(data)
        processed_result = self._process_internal(validated_data, options)
        return self._finalize_result(processed_result)
        
    except ValidationError as e:
        # Handle known validation errors
        logger.warning(f"Data validation failed: {e}")
        raise ProcessingError(f"Invalid data format: {e}") from e
        
    except NetworkError as e:
        # Handle network-related errors
        logger.error(f"Network error during processing: {e}")
        raise ProcessingError(f"Network failure: {e}") from e
        
    except Exception as e:
        # Log unexpected errors with full context before re-raising
        logger.exception(f"Unexpected error processing data: {data!r}")
        raise RuntimeError(f"Processing failed due to unexpected error: {e}") from e
```

### Complexity Rules (Strictly Enforced)

#### Method Complexity Limits
- **Maximum 10 lines per method** (excluding docstring and type annotations)
- **Maximum 3 levels of indentation** (use early returns and guard clauses)
- **Maximum 4 parameters per function** (use dataclasses or config objects for more)
- **Cyclomatic complexity ≤ 5** (use helper methods to reduce branching)

#### Refactoring Techniques
```python
# ❌ BAD: Too complex, too many levels
def process_order(self, order: Order) -> bool:
    if order is not None:
        if order.items:
            for item in order.items:
                if item.quantity > 0:
                    if item.price > 0:
                        # Process item
                        return True
    return False

# ✅ GOOD: Early returns, helper methods
def process_order(self, order: Order) -> bool:
    """Process an order if it's valid."""
    if not self._is_valid_order(order):
        return False
    
    return self._process_valid_order(order)

def _is_valid_order(self, order: Order) -> bool:
    """Check if order is valid for processing."""
    return (order is not None and 
            order.items and 
            self._all_items_valid(order.items))

def _all_items_valid(self, items: List[OrderItem]) -> bool:
    """Check if all items in the list are valid."""
    return all(item.quantity > 0 and item.price > 0 for item in items)
```

#### Class Design Principles
- **Single Responsibility Principle**: Each class should have exactly one reason to change
- **Maximum 5 public methods per class** (excluding `__init__`, `__str__`, `__repr__`)
- **Maximum 7 attributes per class** (use composition for complex state)
- **Prefer composition over inheritance** (favor "has-a" over "is-a" relationships)
- **Use dependency injection** for all external dependencies

### Code Organization Standards

#### File Structure Template
```python
"""Module docstring describing the purpose and main classes/functions.

This module provides payment processing functionality including
validation, transaction handling, and error recovery.
"""

# Imports (following the mandatory order)
import os
from decimal import Decimal
from typing import Final, Optional

from loguru import logger

from myproject.core.exceptions import PaymentError

# Module-level constants
DEFAULT_TIMEOUT: Final[int] = 30
MAX_RETRY_ATTEMPTS: Final[int] = 3

# Type aliases for clarity
PaymentToken = str
TransactionId = str

class PaymentProcessor:
    """Handles payment processing operations with retry logic."""

    # Class constants
    MAX_AMOUNT: Final[Decimal] = Decimal('10000.00')
    
    def __init__(self, gateway: PaymentGateway, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Initialize payment processor with gateway and configuration."""
        self._gateway: Final[PaymentGateway] = gateway
        self._timeout: Final[int] = timeout
        self._processed_count: int = 0

    def process_payment(self, amount: Decimal, token: PaymentToken) -> PaymentResult:
        """Process a payment transaction."""
        self._validate_amount(amount)
        self._validate_token(token)
        return self._execute_payment(amount, token)

    def _validate_amount(self, amount: Decimal) -> None:
        """Validate payment amount is within acceptable range."""
        if amount <= 0:
            raise ValueError(f"Amount must be positive, got {amount}")
        if amount > self.MAX_AMOUNT:
            raise ValueError(f"Amount {amount} exceeds maximum {self.MAX_AMOUNT}")

    def _validate_token(self, token: PaymentToken) -> None:
        """Validate payment token format and content."""
        if not token or not isinstance(token, str):
            raise ValueError("Payment token must be a non-empty string")
        if len(token) < 10:
            raise ValueError("Payment token too short")

    def _execute_payment(self, amount: Decimal, token: PaymentToken) -> PaymentResult:
        """Execute the actual payment transaction."""
        try:
            return self._gateway.charge(amount, token, timeout=self._timeout)
        except GatewayError as e:
            raise PaymentError(f"Payment failed: {e}") from e
```

## Project Structure (Mandatory Layout)

```
src/
└── myproject/
    ├── __init__.py              # Package initialization
    ├── core/                    # Core business logic (no external dependencies)
    │   ├── __init__.py
    │   ├── models.py           # Domain models and entities
    │   ├── services.py         # Business services and use cases
    │   ├── exceptions.py       # Custom exception classes
    │   └── interfaces.py       # Abstract base classes and protocols
    ├── infrastructure/         # External dependencies and adapters
    │   ├── __init__.py
    │   ├── database/           # Database adapters
    │   ├── external_apis/      # Third-party API clients
    │   └── messaging/          # Message queue adapters
    ├── api/                    # API layer (REST, GraphQL, etc.)
    │   ├── __init__.py
    │   ├── routes/             # Route handlers
    │   ├── middleware/         # Request/response middleware
    │   └── schemas/            # Request/response schemas
    ├── utils/                  # Shared utilities (pure functions)
    │   ├── __init__.py
    │   ├── helpers.py          # General helper functions
    │   ├── validators.py       # Input validation utilities
    │   └── formatters.py       # Data formatting utilities
    └── config/                 # Configuration management
        ├── __init__.py
        ├── settings.py         # Application settings
        └── environments/       # Environment-specific configs
tests/
├── unit/                       # Unit tests (fast, isolated)
├── integration/                # Integration tests (with external systems)
├── fixtures/                   # Test data and fixtures
└── conftest.py                # Pytest configuration
```

## Design Patterns (Recommended Implementations)

### Null Object Pattern
```python
from abc import ABC, abstractmethod

class User(ABC):
    """Abstract user interface."""
    
    @abstractmethod
    def get_id(self) -> str:
        """Get user ID."""
        pass
    
    @abstractmethod
    def has_permission(self, action: str) -> bool:
        """Check if user has permission for action."""
        pass

class AuthenticatedUser(User):
    """Represents an authenticated user."""
    
    def __init__(self, user_id: str, permissions: set[str]) -> None:
        self._user_id: Final[str] = user_id
        self._permissions: Final[set[str]] = permissions
    
    def get_id(self) -> str:
        return self._user_id
    
    def has_permission(self, action: str) -> bool:
        return action in self._permissions

class NullUser(User):
    """Represents absence of a user - no permissions, empty ID."""
    
    def get_id(self) -> str:
        return ""
    
    def has_permission(self, action: str) -> bool:
        return False
```

### Builder Pattern for Complex Objects
```python
from typing import List, Optional

class OrderBuilder:
    """Builds Order objects step by step with validation."""

    def __init__(self) -> None:
        self._customer: Optional[Customer] = None
        self._items: List[OrderItem] = []
        self._shipping_address: Optional[Address] = None
        self._billing_address: Optional[Address] = None

    def with_customer(self, customer: Customer) -> 'OrderBuilder':
        """Set the customer for this order."""
        if customer is None:
            raise ValueError("Customer cannot be None")
        self._customer = customer
        return self

    def with_items(self, items: List[OrderItem]) -> 'OrderBuilder':
        """Set the items for this order."""
        if not items:
            raise ValueError("Order must have at least one item")
        self._items = items.copy()  # Defensive copy
        return self

    def with_shipping_address(self, address: Address) -> 'OrderBuilder':
        """Set the shipping address."""
        if address is None:
            raise ValueError("Shipping address cannot be None")
        self._shipping_address = address
        return self

    def build(self) -> Order:
        """Build and validate the final Order object."""
        if self._customer is None:
            raise ValueError("Order requires a customer")
        if not self._items:
            raise ValueError("Order requires at least one item")
        if self._shipping_address is None:
            raise ValueError("Order requires a shipping address")
        
        return Order(
            customer=self._customer,
            items=self._items,
            shipping_address=self._shipping_address,
            billing_address=self._billing_address or self._shipping_address
        )
```

## Agent Instructions

### When Creating New Code
1. **Type annotations**: Add complete type annotations to EVERY function, method, and class attribute
2. **Docstrings**: Include comprehensive Google-style docstrings for ALL public APIs
3. **Input validation**: Validate ALL inputs at function boundaries with specific error messages
4. **Naming**: Use descriptive variable names (no single letters except `i`, `j`, `k` in short loops)
5. **Function size**: Keep functions small and focused (maximum 10 lines of implementation)
6. **Error handling**: Handle errors explicitly with proper exception chaining - no bare `except:` blocks
7. **Immutability**: Use `Final` for constants and prefer immutable data structures
8. **Dependencies**: Inject dependencies rather than creating them inside classes

### When Modifying Existing Code
1. **Consistency**: Maintain existing code style and patterns exactly
2. **Type safety**: Preserve and enhance all type annotations
3. **Documentation**: Update docstrings if behavior changes
4. **Dependencies**: Don't introduce new dependencies without explicit approval
5. **Scope**: Keep modifications minimal and focused on the specific requirement
6. **Testing**: Ensure changes don't break existing functionality
7. **Backwards compatibility**: Maintain API compatibility unless explicitly changing it

### Post-Change Linting and Formatting (MANDATORY)
After making ANY code changes, run the following commands in this EXACT order:

1. **Type checking with pyright (strict mode)**:
   ```bash
   poetry run pyright --project pyrightconfig.strict.json .
   ```
   Fix ALL type errors before proceeding.

2. **Type checking with mypy**:
   ```bash
   poetry run mypy .
   ```
   Fix ALL mypy errors before proceeding.

3. **Code formatting with black**:
   ```bash
   poetry run black .
   ```
   This ensures consistent code formatting across the project.

**IMPORTANT**: 
- Never skip any of these steps
- Fix all issues reported by pyright and mypy
- Re-run the linters after fixes to ensure no regressions
- Only consider code complete when all checks pass

### Code Quality Checklist (Must verify ALL items)
Before considering any code complete, ensure:
- [ ] All functions have complete type annotations (parameters and return types)
- [ ] All public functions have comprehensive Google-style docstrings
- [ ] All inputs are validated with specific error messages
- [ ] Error cases are handled explicitly with proper exception chaining
- [ ] No methods exceed 10 lines of implementation
- [ ] No more than 3 levels of indentation anywhere
- [ ] All variable names are descriptive and follow naming conventions
- [ ] No commented-out code remains
- [ ] No TODO comments without associated issue references
- [ ] All imports follow the mandatory ordering
- [ ] All classes follow single responsibility principle
- [ ] All magic numbers are replaced with named constants

## Prohibited Practices (Never Do These)

### Code Quality Violations
- **Never** use `# type: ignore` comments (fix the underlying type issue instead)
- **Never** create methods longer than 10 lines of implementation
- **Never** use generic exception handling without specific logging and re-raising
- **Never** skip input validation on public methods
- **Never** use mutable default arguments (`def func(items=[]):`)
- **Never** create circular imports between modules
- **Never** use global variables (use dependency injection or configuration objects)
- **Never** write code without complete type hints
- **Never** use abbreviations in variable names (`usr` → `user`, `cfg` → `config`)

### Anti-Patterns to Avoid
```python
# ❌ NEVER DO THIS
def bad_function(data=[], config={}):  # Mutable defaults
    # type: ignore  # Ignoring type issues
    try:
        result = process(data)  # No input validation
        return result
    except:  # Bare except
        pass  # Silent failure

# ❌ NEVER DO THIS
class BadClass:
    def do_everything(self, a, b, c, d, e, f):  # Too many parameters
        if a:
            if b:
                if c:
                    if d:  # Too many nesting levels
                        # 20 lines of code here  # Too long
                        pass

# ✅ ALWAYS DO THIS
def good_function(data: List[str], config: Optional[Dict[str, Any]] = None) -> ProcessResult:
    """Process data with proper validation and error handling."""
    if not data:
        raise ValueError("Data list cannot be empty")
    
    if config is None:
        config = {}
    
    try:
        return self._process_validated_data(data, config)
    except ProcessingError as e:
        logger.error(f"Processing failed: {e}")
        raise ProcessingError(f"Failed to process data: {e}") from e
```

## File Handling Patterns (Standard Implementation)

```python
from pathlib import Path
from typing import Dict, Any, Optional
import json

def read_json_config(file_path: Path, encoding: str = 'utf-8') -> Dict[str, Any]:
    """Read and parse JSON configuration from file.

    Args:
        file_path: Path to the JSON configuration file
        encoding: File encoding to use for reading

    Returns:
        Parsed configuration as a dictionary

    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        ValueError: If the file content is not valid JSON
        PermissionError: If the file cannot be read due to permissions
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    try:
        content = file_path.read_text(encoding=encoding)
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file {file_path}: {e}") from e
    except PermissionError as e:
        raise PermissionError(f"Cannot read config file {file_path}: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error reading {file_path}: {e}") from e

def write_json_config(data: Dict[str, Any], file_path: Path, encoding: str = 'utf-8') -> None:
    """Write configuration data to JSON file.

    Args:
        data: Configuration data to write
        file_path: Path where to write the configuration
        encoding: File encoding to use for writing

    Raises:
        ValueError: If data cannot be serialized to JSON
        PermissionError: If the file cannot be written due to permissions
    """
    if not isinstance(data, dict):
        raise TypeError(f"Data must be a dictionary, got {type(data).__name__}")
    
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        json_content = json.dumps(data, indent=2, ensure_ascii=False)
        file_path.write_text(json_content, encoding=encoding)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Cannot serialize data to JSON: {e}") from e
    except PermissionError as e:
        raise PermissionError(f"Cannot write to {file_path}: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error writing to {file_path}: {e}") from e
```

## String Formatting Standards

### Preferred Formatting Methods
```python
# ✅ ALWAYS USE: f-strings for all string formatting
name = "Alice"
age = 30
message = f"Hello {name}, you are {age} years old"

# ✅ USE: f-strings with format specifiers
price = 123.456
formatted_price = f"Price: ${price:.2f}"

# ✅ USE: repr() for debug output and logging
data = {"key": "value"}
logger.debug(f"Processing data: {data!r}")

# ✅ USE: Multi-line f-strings for complex formatting
result = (
    f"User {user.name} (ID: {user.id}) "
    f"has {len(user.orders)} orders "
    f"totaling ${user.total_spent:.2f}"
)

# ❌ NEVER USE: % formatting or .format()
message = "Hello %s" % name  # Don't do this
message = "Hello {}".format(name)  # Don't do this
```

## Logging Standards

```python
from loguru import logger
from typing import Any, Dict

def process_user_data(user_id: str, data: Dict[str, Any]) -> bool:
    """Process user data with comprehensive logging."""
    logger.info(f"Starting processing for user {user_id}")
    
    try:
        # Log important steps
        logger.debug(f"Validating data for user {user_id}: {data!r}")
        validated_data = self._validate_data(data)
        
        logger.debug(f"Processing validated data for user {user_id}")
        result = self._process_data(validated_data)
        
        logger.info(f"Successfully processed data for user {user_id}")
        return result
        
    except ValidationError as e:
        logger.warning(f"Validation failed for user {user_id}: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing user {user_id}")
        raise RuntimeError(f"Processing failed for user {user_id}: {e}") from e
```

## Final Quality Standards

### Code Review Criteria
Every piece of code must meet these standards:
1. **Type Safety**: 100% type annotation coverage with no `Any` types unless justified
2. **Documentation**: Complete docstrings for all public APIs with examples
3. **Error Handling**: Comprehensive error handling with specific exception types
4. **Testability**: Code structure that enables easy unit testing
5. **Readability**: Self-documenting code with clear intent
6. **Performance**: Efficient algorithms and data structures
7. **Security**: Input validation and secure coding practices

### Performance Guidelines
- Use generators for large data processing
- Prefer list comprehensions over loops for simple transformations
- Use `dataclasses` or `pydantic` models for structured data
- Cache expensive computations when appropriate
- Use `functools.lru_cache` for pure functions with repeated calls

### Security Considerations
- Validate all external inputs
- Use parameterized queries for database operations
- Sanitize data before logging
- Don't log sensitive information (passwords, tokens, etc.)
- Use secure random generators for cryptographic operations

Remember: **Quality over speed** - write it correctly the first time. When in doubt, be explicit rather than implicit. Every line of code should have a clear, single purpose and be easily testable.

## Project-Specific CLI Information

This project uses a subcommand-based CLI structure with the following commands:
- `poetry run dspy-prompt-optimizer -- self` - Self-refinement optimization
- `poetry run dspy-prompt-optimizer -- example` - Example-based optimization  
- `poetry run dspy-prompt-optimizer -- metric` - Metric-based optimization
- `poetry run dspy-prompt-optimizer -- generate-examples` - Generate examples for two-phase approach

When creating documentation or examples, always use `poetry run dspy-prompt-optimizer -- [subcommand]` format.