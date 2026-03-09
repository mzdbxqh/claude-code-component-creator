---
name: data-processor
description: "Process and transform data with various algorithms and filtering options"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
---

# Data Processor

Process and transform data using various algorithms.

## Input

- data: array - Input data to process
- options: object - Processing options

## Output

- processed_data: array - Processed result
- statistics: object - Processing statistics

## Workflow

1. Validate input data
2. Apply transformations
3. Filter results
4. Return processed data
