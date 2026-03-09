---
name: good-skill
description: "A well-designed skill with proper structure, clear workflow, and appropriate configuration"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
---

# Good Skill Example

This is an example of a well-designed skill that passes all architecture checks.

## Input

- task: string - The task to execute
- context: object - Execution context

## Output

- result: string - Execution result
- status: string - Success or failure

## Workflow

1. Read input parameters
2. Execute main logic
3. Return results

## Examples

```yaml
task: example-task
context: {}
```

## Error Handling

- Invalid input: Return error with validation message
- Execution failure: Log error and return failure status
