---
name: enforce-type-annotations
description: use this skill to ensure all public functions in a package have complete type annotations on parameters and return values
---
1. For each Python source file in the target package, parse the AST or source code.
2. Identify all public functions: those whose names do not start with an underscore.
3. For each public function, check if every parameter has a type annotation.
4. Check if the function has a return type annotation.
5. If any annotation is missing, add a placeholder or inferred type annotation if possible.
6. Save the modified source file only if changes were made.
7. Verify that the code still parses and type checks (optionally run mypy or similar).
