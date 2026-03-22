---
name: review-pr
description: Code review best practices for pull requests
---

# PR Code Review Skill

## Overview

Follow these guidelines when reviewing pull requests to ensure quality code reviews.

## Review Checklist

### 1. Correctness
- Does the code do what it's supposed to do?
- Are edge cases handled properly?
- Is there proper error handling?

### 2. Security
- Are there any security vulnerabilities?
- Is user input properly validated?
- Are secrets handled securely?

### 3. Performance
- Are there any obvious performance issues?
- Are database queries optimized?
- Is caching used where appropriate?

### 4. Code Style
- Does the code follow project conventions?
- Are variable/function names descriptive?
- Is there appropriate documentation?

### 5. Testing
- Are there adequate tests?
- Do tests cover happy path and edge cases?
- Are tests maintainable?

## Review Comments

### DO:
- Be constructive and specific
- Point to exact lines that need changes
- Explain WHY something should change
- Suggest alternative approaches
- Acknowledge good work

### DON'T:
- Be vague ("this doesn't look right")
- Make it personal
- Focus on style over substance
- Review more than 300 lines at once

## Example Review Comment

```
// Instead of:
if (x) doSomething();

// Consider:
if (isValid(x)) {
    doSomething();
}

// Why: The original is hard to read and the method name
// makes the intent clearer.
```
