# MoodReads Scripts

This directory contains various utility scripts for the MoodReads project.

## Interface Validation

The `validate_interfaces.py` script checks that method calls in the codebase match the expected method signatures. This helps catch interface errors early.

### Usage

```bash
# Run validation
python scripts/validate_interfaces.py

# Run with verbose logging
python scripts/validate_interfaces.py --verbose

# Skip validation (useful for debugging)
python scripts/validate_interfaces.py --skip
```

### Pre-commit Hook

The validation script is run as a pre-commit hook. If you need to bypass validation for a specific commit, you can use:

```bash
# Skip validation for a single commit
SKIP_VALIDATION=1 git commit -m "Your commit message"
```

This is useful when:
- You're making experimental changes
- The validation is taking too long
- You're experiencing recursion errors with certain libraries

### Troubleshooting

If you encounter recursion errors during validation, it's likely because the script is trying to analyze a complex external library. The script has been configured to:

1. Skip directories like `.moodreads-env`, `.git`, etc.
2. Skip files larger than 500KB
3. Handle recursion errors gracefully

If you still encounter issues, please report them or use the `SKIP_VALIDATION` environment variable as a workaround. 