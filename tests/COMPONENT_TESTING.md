# Component Testing Guide

This guide explains how to write isolated component tests for NiceGUI components in this project.

## Overview

Component tests allow you to test UI components in isolation without requiring the full page context. This makes tests:
- **Faster** - Only the component under test is rendered
- **More focused** - Test specific component behavior without page-level interference
- **Easier to debug** - Failures are isolated to the component being tested
- **More maintainable** - Changes to pages don't break component tests

## Fixtures Available

### `component_page`

Factory fixture for creating minimal test pages with isolated components.

**Usage:**
```python
async def test_my_component(user: User, component_page):
    @component_page('/test-path')
    def setup():
        # Create and return your component
        component = MyComponent(arg1="test", arg2=123)
        return component
    
    await user.open('/test-path')
    # ... your test assertions
```

### `test_user`

Provides a test user instance for components that require user context.

**Usage:**
```python
async def test_with_user(user: User, component_page, test_user):
    @component_page('/test-user-component')
    def setup():
        component = UserDependentComponent(test_user)
        return component
```

### `sample_consent_entry`

Provides a sample consent entry from the database for testing consent-related components.

**Usage:**
```python
async def test_consent_component(user: User, component_page, test_user, sample_consent_entry):
    if not sample_consent_entry:
        return  # Skip if no data available
    
    @component_page('/test-consent')
    def setup():
        component = ConsentEntryComponent(sample_consent_entry, test_user)
        return component
```

## Testing Patterns

### Simple Component (No Dependencies)

```python
async def test_simple_component(user: User, component_page):
    """Test a component that doesn't need database or user context."""
    
    @component_page('/test-simple')
    def setup():
        with ui.column():
            component = SimpleComponent(prop1="value1", prop2="value2")
            return component
    
    await user.open('/test-simple')
    await user.should_see("expected text")
```

### Component with Database Dependencies

```python
async def test_db_component(user: User, component_page, test_user):
    """Test a component that needs database access."""
    from controller import some_controller
    
    @component_page('/test-db')
    def setup():
        # Fetch or create test data
        data = some_controller.get_data(test_user)
        
        with ui.column():
            component = DBComponent(data, test_user)
            return component
    
    await user.open('/test-db')
    
    # Assert component rendered with test data
    await user.should_see("expected data content")
    
    # Verify component shows user-specific state
    await user.should_see(test_user.username)
    
    # Assert database interaction occurred
    assert data is not None, "Expected data to be fetched from database"
    assert data.user_id == test_user.id
```

### Multiple Components

```python
async def test_multiple_components(user: User, component_page):
    """Test multiple instances of a component."""
    
    @component_page('/test-multiple')
    def setup():
        with ui.column().classes("gap-4"):
            for i in range(3):
                MyComponent(id=i, label=f"Item {i}")
    
    await user.open('/test-multiple')
    await user.should_see("Item 0")
    await user.should_see("Item 1")
    await user.should_see("Item 2")
```

### Component with User Interactions

```python
async def test_interactions(user: User, component_page):
    """Test component interactions like clicks and input."""
    
    @component_page('/test-interaction')
    def setup():
        component = InteractiveComponent()
        component.button.mark("test-button")
        component.input.mark("test-input")
        return component
    
    await user.open('/test-interaction')
    
    # Type in input
    user.find("test-input").type("hello")
    
    # Click button
    user.find("test-button").click()
    
    # Verify result
    await user.should_see("expected result")
```

## Best Practices

1. **Use descriptive test paths**: Make the component test page path descriptive (e.g., `/test-consent-entry-toggle`)

2. **Mark elements for testing**: Use `.mark("identifier")` on UI elements to make them easier to find:
   ```python
   button = ui.button("Click me").mark("my-test-button")
   ```

3. **Handle missing data gracefully**: When using database fixtures, check if data exists:
   ```python
   if not sample_consent_entry:
       return  # or use pytest.skip()
   ```

4. **Keep setup functions focused**: The setup function should only create the component being tested and minimal context

5. **Use appropriate containers**: Wrap components in `ui.column()` or `ui.row()` if they need container context

6. **Test one thing at a time**: Each test should verify a single behavior or aspect of the component

7. **Clean up after async operations**: The `async_test_cleanup` fixture automatically adds a small delay after each test to allow async operations to complete

## Example Test Files

- `test_consent_entry_component.py` - Tests for components with database dependencies
- `test_faq_element_component.py` - Tests for simple components without dependencies

## Running Component Tests

Run all component tests:
```bash
poetry run pytest tests/test_*_component.py
```

Run specific component test:
```bash
poetry run pytest tests/test_consent_entry_component.py
```

Run with verbose output:
```bash
poetry run pytest tests/test_consent_entry_component.py -v
```

## Troubleshooting

### Component doesn't render
- Ensure the component's `__init__` and `content()` methods are properly called
- Check if the component requires a specific container (e.g., must be inside a `ui.column()`)

### Elements not found
- Use `.mark("identifier")` on elements and find them with `user.find("identifier")`
- Add `await user.should_see("text")` to wait for rendering

### Database data not available
- Check that the `in_memory_database` fixture has seeded the required data
- Use `test_user` fixture for a guaranteed user instance
- Handle `None` cases when data might not exist

### Async timing issues
- The `async_test_cleanup` fixture adds a 0.1s delay after each test
- Add explicit waits with `await user.should_see()` when needed
- Use `retries` parameter: `await user.should_see("text", retries=5)`
