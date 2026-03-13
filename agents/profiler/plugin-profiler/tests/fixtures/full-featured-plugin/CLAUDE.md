# Full Featured Plugin - Project Guidelines

## Design Philosophy

This plugin follows these core principles:

1. **External State Management**: All workflow state is stored in YAML artifact files
2. **Complete Traceability**: Every requirement maps to implementation
3. **Test-Driven Development**: Tests before code, always

## Architecture

The plugin uses a three-layer architecture:
- **Layer 1**: Skills (user-facing commands)
- **Layer 2**: SubAgents (implementation logic)
- **Layer 3**: Knowledge libs (shared standards)

## Quality Standards

- Minimum test coverage: 80%
- Maximum skill length: 400 lines
- All commands must have examples
