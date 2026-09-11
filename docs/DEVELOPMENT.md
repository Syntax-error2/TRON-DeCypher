# Development Guide

## Adding Modules and Plugins

To ensure maintainability, follow these guidelines when adding new features:

1. **Keep it small**: Use small modules and classes with a single responsibility.
2. **Type Hints**: Always use strong type hints. Mypy is enforced.
3. **Plugins**: New analysis capabilities should be implemented as plugins within the `app.plugins` framework.
   - Implement the base plugin interface.
   - Register the plugin with the Plugin Registry.
4. **Services**: Business logic belongs in `app.services`, not in UI components or models.
5. **UI**: UI components should strictly handle presentation. They must communicate with the rest of the application via Services.
6. **No Circular Imports**: Keep the dependency graph clean.
7. **Error Handling**: Use safe error handling. Do not swallow exceptions blindly.
