---
name: add-regression-tests-and-changelog
description: use this skill to add regression tests for fixed bugs and record each fix in the changelog
---
1. For each bug fix made in the code, write a dedicated test function in a regression test file (e.g., tests/test_regressions.py).
2. Each test function should reproduce the bug scenario and assert the correct fixed behavior.
3. Ensure the regression test file imports the necessary modules and runs without errors.
4. Add a bullet point entry under the '## Unreleased' heading in CHANGELOG.md for each fix, using the format: '- fix(<function name>): <short description>'.
5. Confirm that the changelog file is updated without removing or altering existing entries.
6. Run the full test suite to verify all tests pass, including the new regression tests.
7. Do not modify existing test files except to add new test files for regressions.
