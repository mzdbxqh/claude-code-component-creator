---
name: data-transformer
description: "Transform and process data using various algorithms and filtering methods"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
---

# Data Transformer

Transform and process data using various algorithms.

## Input

- data: array - Data to transform
- options: object - Transformation options

## Output

- transformed_data: array - Transformation result
- stats: object - Processing statistics

## Workflow

1. Validate input
2. Apply transformations
3. Filter output
4. Return results
