# CLAUDE.md - Project Context & Guidelines

This file provides essential context for Claude Code to understand the project
structure, coding standards, and workflow requirements.

## 🚀 Quick Start

### Environment Setup

```bash
# Activate Python environment
poetry shell

# Install dependencies
poetry install

# Run the application
poetry run python main.py
```

### Essential Commands

```bash
# Type checking & linting (in order)
poetry run pyright --project pyrightconfig.strict.json .
poetry run mypy .
poetry run pylint -j`nproc` prompt_optimizer
poetry run sourcery review --verbose --no-summary . | cat

# Testing
poetry run pytest .
poetry run pytest -xvs .  # Stop on first failure with verbose output

# Code formatting
poetry run black .
poetry run isort .

# Pre-commit hooks
pre-commit install
pre-commit run --all-files

# Build & Deploy
poetry build
poetry publish --dry-run
```

## 🔧 Development Workflow

### Linting Requirements (MANDATORY)

Execute Python linters in this **exact order** and fix **ALL** issues:

1. **pyright** (strict mode) - MUST fix all type errors
2. **mypy** - MUST fix all type checking issues
3. **pylint** - Fix unless conflicts with type checkers
4. **sourcery** - Apply improvements where feasible

**Critical Rules:**

- ❌ NEVER use `# type: ignore` comments
- ❌ NEVER add pylint disable comments without justification
- ❌ NEVER skip type annotations or imports
- ✅ Re-run each linter after fixes to ensure no regressions
- ✅ Provide summary of fixes for each tool

### Git Workflow

```bash
# Feature development
git checkout -b feature/description
# Make changes, then run all linters
# Commit only after all checks pass
git commit -m "type(scope): description"  # conventional commits

# Working with issues
# Use /project:fix-github-issue <issue_number> command
```

## 🐍 Python Coding Standards

### Architecture Principles

#### 1. **Single Responsibility Principle (SRP)**

- Each class/module has ONE reason to change
- Each method has a clear, singular purpose
- Files organized by feature, not technical layer

#### 2. **Object-Oriented Best Practices**

```python
# ✅ Good: Encapsulated class with clear responsibilities
class PaymentProcessor:
    """Handles payment processing logic."""

    def __init__(self, gateway: PaymentGateway) -> None:
        self._gateway: Final[PaymentGateway] = gateway
        self._logger: Final[Logger] = get_logger(__name__)

    def process_payment(self, amount: Decimal, token: str) -> PaymentResult:
        """Process a single payment transaction."""
        self._validate_amount(amount)
        self._validate_token(token)
        # Implementation...
```

#### 3. **Type Safety & Annotations**

**MANDATORY Type Annotations:**

- Variable annotations: `count: int = 0`
- Function parameters: `def process(data: List[str]) -> None:`
- Return types: Always annotate, use `-> None` for procedures
- Class attributes: Annotate in `__init__`
- Use `Final` for immutable attributes
- Use `Optional[T]` or `T | None` for nullable types

```python
# ✅ Comprehensive typing example
from typing import List, Optional, Dict, Callable, Final
from decimal import Decimal

class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository: Final[OrderRepository] = repository
        self._validators: List[Callable[[Order], bool]] = []

    def find_order(self, order_id: str) -> Optional[Order]:
        """Find order by ID, returns None if not found."""
        if not isinstance(order_id, str):
            raise TypeError(f"Expected str, got {type(order_id)}")

        result = self._repository.get(order_id)
        return result if result is not None else None
```

#### 4. **Error Handling & Validation**

```python
# ✅ Comprehensive error handling
def process_data(data: Any) -> ProcessedData:
    """Process input data with full validation."""
    # Input validation - fail fast
    if data is None:
        raise ValueError("Data cannot be None")

    if not isinstance(data, (dict, list)):
        raise TypeError(f"Expected dict or list, got {type(data)}")

    try:
        # Processing logic
        result = transform_data(data)
        logger.info(f"Successfully processed {len(data)} items")
        return result

    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise  # Re-raise with context

    except Exception as e:
        logger.error(f"Unexpected error in process_data: {e}")
        raise RuntimeError(f"Processing failed: {e}") from e
```

#### 5. **Logging Standards**

```python
from loguru import logger

# Configure at module level
logger = logger.bind(module=__name__)

class DataProcessor:
    def process(self, items: List[Item]) -> None:
        logger.info(f"Starting processing of {len(items)} items")

        for i, item in enumerate(items):
            logger.trace(f"Processing item {i}: {item.id}")
            try:
                self._process_item(item)
            except Exception as e:
                logger.error(f"Failed to process item {item.id}: {e}")
                raise

        logger.info("Processing completed successfully")
```

### Code Organization

#### Package Structure

```
project/
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── core/           # Core business logic
│       │   ├── __init__.py
│       │   ├── models.py   # Domain models
│       │   └── services.py # Business services
│       ├── api/            # API layer
│       │   ├── __init__.py
│       │   └── routes.py
│       └── utils/          # Shared utilities
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── pyproject.toml
└── CLAUDE.md
```

#### Module Organization

- **Package-by-Feature**: Group related functionality together
- **Layered Architecture**: Clear separation between layers
- **Component-Based**: Reusable, self-contained components

### Testing Standards

```python
# ✅ Test example with proper structure
import pytest
from unittest.mock import Mock, patch

class TestPaymentProcessor:
    """Test suite for PaymentProcessor."""

    @pytest.fixture
    def processor(self) -> PaymentProcessor:
        """Create processor with mock gateway."""
        gateway = Mock(spec=PaymentGateway)
        return PaymentProcessor(gateway)

    def test_process_payment_success(self, processor: PaymentProcessor) -> None:
        """Test successful payment processing."""
        # Arrange
        amount = Decimal("100.00")
        token = "valid_token"

        # Act
        result = processor.process_payment(amount, token)

        # Assert
        assert result.success is True
        assert result.transaction_id is not None
```

### Complexity Management

#### Low Cyclomatic Complexity

- Methods should have cyclomatic complexity ≤ 10
- Break complex logic into smaller methods
- Use early returns to reduce nesting

```python
# ❌ High complexity
def process_order(order: Order) -> Result:
    if order.status == "pending":
        if order.payment_status == "paid":
            if order.items:
                for item in order.items:
                    if item.in_stock:
                        # Process...

# ✅ Low complexity
def process_order(order: Order) -> Result:
    if not self._is_processable(order):
        return Result.failure("Order not processable")

    return self._process_items(order.items)

def _is_processable(self, order: Order) -> bool:
    return (order.status == "pending" and
            order.payment_status == "paid" and
            bool(order.items))
```

## 📋 Project-Specific Configuration

### Dependencies

- Python version: 3.11+
- Package manager: Poetry
- Testing: pytest
- Type checking: mypy, pyright
- Linting: pylint, ruff
- Code analysis: sourcery

### Environment Variables

```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
LOG_LEVEL=INFO
```

### Common Issues & Solutions

- **Import errors**: Ensure `PYTHONPATH` includes project root
- **Type errors**: Run `poetry run mypy --install-types`
- **Poetry issues**: Try `poetry lock --no-update`

## 🤖 Claude-Specific Instructions

### Response Style

- Be concise and direct
- Explain non-trivial commands before running
- Ask before making structural changes
- Commit only when explicitly requested

### Code Generation Rules

1. Always use type annotations
2. Include comprehensive error handling
3. Add logging for important operations
4. Write self-documenting code
5. Follow PEP 8 and project conventions

### When Working on Tasks

1. Read relevant files first without writing code
2. Understand the full context
3. Plan the approach
4. Implement with all quality checks
5. Run all linters before marking complete
6. Update this file if new patterns emerge

## 📚 Quick Reference

### Type Checking Commands

```bash
# Strict type checking
poetry run pyright --project pyrightconfig.strict.json .
poetry run mypy --strict .

# Fix type stubs
poetry run mypy --install-types
```

### Debugging Commands

```bash
# Run with debugger
poetry run python -m pdb main.py

# Profile performance
poetry run python -m cProfile -o profile.stats main.py

# Memory profiling
poetry run python -m memory_profiler main.py
```

### Documentation

```bash
# Generate docs
poetry run sphinx-build -b html docs docs/_build

# Serve docs locally
poetry run python -m http.server --directory docs/_build
```

---

**Remember**: Quality > Speed. Always ensure code passes ALL checks before
proceeding.
