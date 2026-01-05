# Claude Code Project Instructions

## Security Guidelines

### Logging Best Practices

**IMPORTANT:** Follow these rules when adding logging statements:

1. **Never log user-provided input directly** - This creates log injection vulnerabilities
   - Bad: `logger.info(f'Processing {user_input}')`
   - Good: Sanitize first or don't log user input at all

2. **Remove debug logging before raising PRs** - Debug `logger.info()`, `console.log()`, and `print()` statements should be removed before committing

3. **If logging user input is necessary:**
   - Use parameterized logging: `logger.info('Value: %s', sanitized_value)`
   - Strip newlines: `value.replace('\n', ' ').replace('\r', ' ')`
   - Truncate length: `value[:100]`
   - Validate against allowed values where possible

4. **Use appropriate log levels:**
   - `logger.error()` - Errors that need attention
   - `logger.warning()` - Unexpected but handled situations
   - `logger.info()` - Important operational events (not debug)
   - `logger.debug()` - Debug information (disabled in production)

## Pre-PR Checklist

Before raising a PR, ensure:
- [ ] No debug logging statements remain (`console.log`, `print`, debug `logger.info`)
- [ ] No user-provided values are logged without sanitization
- [ ] Code passes `ruff check`
