---
name: test
description: Testing best practices and patterns
---

# Testing Skill

## Overview

Follow these guidelines to write effective, maintainable tests.

## Testing Principles

### 1. Test Structure (AAA Pattern)
```
Arrange: Set up test data and conditions
Act: Execute the code under test
Assert: Verify the expected outcome
```

### 2. Test Naming
- Use descriptive names that explain what/why
- Format: `test_<unit>_<scenario>_<expected_result>`
- Example: `test_user_login_with_invalid_password_returns_error`

### 3. Test Coverage Goals
- Aim for meaningful coverage, not 100%
- Prioritize critical paths and edge cases
- Don't test trivial getters/setters

## Types of Tests

### Unit Tests
- Test individual functions/methods
- Fast, isolated, no dependencies
- Mock external dependencies

### Integration Tests
- Test component interactions
- May use real databases/services
- Slower than unit tests

### End-to-End Tests
- Test complete user flows
- Use real browser/client
- Slowest, most comprehensive

## Best Practices

1. **One assertion per test** (when practical)
2. **Tests should be deterministic** - no random values or timing dependencies
3. **Independent tests** - no shared state between tests
4. **Descriptive failures** - assertion messages explain what went wrong
5. **Keep tests fast** - slow tests get skipped
6. **Follow F.I.R.S.T principles**:
   - Fast
   - Independent
   - Repeatable
   - Self-validating
   - Timely

## Test Example

```python
def test_calculate_total_with_discount():
    # Arrange
    cart = ShoppingCart()
    cart.add_item(Item("book", price=10.00))
    cart.add_item(Item("pen", price=2.00))

    # Act
    total = calculate_total(cart, discount=0.1)

    # Assert
    assert total == 10.80, "Total should be 10.80 after 10% discount"
```
