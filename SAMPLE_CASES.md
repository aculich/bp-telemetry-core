# Blueplane Telemetry Core - Sample Test Cases

## Overview

These sample cases are designed to showcase the key strengths and value proposition of Blueplane Telemetry Core. Each case demonstrates different aspects of AI-assisted coding that are valuable to track and analyze.

## Why These Cases Matter

### 1. **Acceptance Rate Tracking**
Understanding which AI suggestions you accept vs. reject reveals:
- What types of changes are most valuable
- Where AI assistance is most effective
- Patterns in your workflow preferences

### 2. **Tool Usage Patterns**
Tracking which tools are used most reveals:
- Your preferred coding patterns
- Areas where AI helps most
- Efficiency opportunities

### 3. **Productivity Metrics**
Measuring time, tokens, and changes reveals:
- Actual productivity improvements
- Cost-effectiveness of AI assistance
- Areas for workflow optimization

### 4. **Conversation Flow Analysis**
Understanding conversation structure reveals:
- How you interact with AI assistants
- Context window management patterns
- Multi-turn problem-solving approaches

## Sample Case 1: Refactoring with Multiple Tools

**Goal**: Demonstrate tool variety and acceptance patterns

**Scenario**: Refactor a Python class to use dependency injection

**Expected Events**:
- SessionStart
- UserPromptSubmit (request refactoring)
- PreToolUse / PostToolUse (ReadFile - read existing code)
- PreToolUse / PostToolUse (Edit - refactor class)
- PreToolUse / PostToolUse (ReadFile - verify changes)
- UserPromptSubmit (request tests)
- PreToolUse / PostToolUse (Edit - add tests)
- Stop

**What This Reveals**:
- Tool usage distribution (ReadFile vs Edit)
- Acceptance rate for refactoring suggestions
- Multi-step problem solving patterns
- Time spent on different phases

## Sample Case 2: Bug Fix with Rejection Pattern

**Goal**: Demonstrate rejection tracking and iteration

**Scenario**: Fix a bug, reject first suggestion, accept second

**Expected Events**:
- SessionStart
- UserPromptSubmit (describe bug)
- PreToolUse / PostToolUse (Edit - first attempt, REJECTED)
- UserPromptSubmit (clarify requirements)
- PreToolUse / PostToolUse (Edit - second attempt, ACCEPTED)
- Stop

**What This Reveals**:
- Rejection patterns (what gets rejected and why)
- Iteration cycles (how many attempts before acceptance)
- Context refinement patterns
- Acceptance delay metrics

## Sample Case 3: Multi-File Feature Addition

**Goal**: Demonstrate complex multi-file operations

**Scenario**: Add a new feature across multiple files

**Expected Events**:
- SessionStart
- UserPromptSubmit (describe feature)
- PreToolUse / PostToolUse (Edit - file1.py)
- PreToolUse / PostToolUse (Edit - file2.py)
- PreToolUse / PostToolUse (Edit - file3.py)
- PreToolUse / PostToolUse (ReadFile - verify integration)
- UserPromptSubmit (request documentation)
- PreToolUse / PostToolUse (Edit - README.md)
- Stop

**What This Reveals**:
- Multi-file change patterns
- File type preferences (.py, .md, etc.)
- Cross-file dependency awareness
- Documentation habits

## Sample Case 4: Code Review and Optimization

**Goal**: Demonstrate analysis and improvement patterns

**Scenario**: Review code and optimize performance

**Expected Events**:
- SessionStart
- UserPromptSubmit (request code review)
- PreToolUse / PostToolUse (ReadFile - read code)
- UserPromptSubmit (request optimizations)
- PreToolUse / PostToolUse (Edit - optimize)
- PreToolUse / PostToolUse (Edit - add comments)
- Stop

**What This Reveals**:
- Code review patterns
- Optimization acceptance rates
- Documentation addition patterns
- Quality improvement metrics

## Sample Case 5: Quick Fix (High Acceptance)

**Goal**: Demonstrate high-value, quick interactions

**Scenario**: Quick syntax fix or small improvement

**Expected Events**:
- SessionStart
- UserPromptSubmit (quick fix request)
- PreToolUse / PostToolUse (Edit - fix, ACCEPTED immediately)
- Stop

**What This Reveals**:
- High-confidence changes (immediate acceptance)
- Quick turnaround patterns
- Low-latency interactions
- High-value suggestions

## Sample Case 6: Learning and Exploration

**Goal**: Demonstrate learning patterns and context building

**Scenario**: Learn a new library or pattern

**Expected Events**:
- SessionStart
- UserPromptSubmit (ask about library)
- PreToolUse / PostToolUse (ReadFile - read docs)
- UserPromptSubmit (request example)
- PreToolUse / PostToolUse (Edit - create example)
- UserPromptSubmit (request explanation)
- PreToolUse / PostToolUse (Edit - add comments)
- Stop

**What This Reveals**:
- Learning patterns
- Documentation reading habits
- Example-driven learning
- Knowledge building workflows

## Sample Case 7: Test-Driven Development

**Goal**: Demonstrate TDD patterns

**Scenario**: Write tests first, then implementation

**Expected Events**:
- SessionStart
- UserPromptSubmit (request test)
- PreToolUse / PostToolUse (Edit - write test)
- UserPromptSubmit (request implementation)
- PreToolUse / PostToolUse (Edit - implement)
- PreToolUse / PostToolUse (ReadFile - verify test passes)
- Stop

**What This Reveals**:
- TDD adoption patterns
- Test-first vs code-first preferences
- Test quality metrics
- Development methodology preferences

## Sample Case 8: Context Window Management

**Goal**: Demonstrate PreCompact hook usage

**Scenario**: Long conversation requiring context compaction

**Expected Events**:
- SessionStart
- Multiple UserPromptSubmit events
- Multiple PreToolUse / PostToolUse events
- PreCompact (context window compaction)
- More interactions after compaction
- Stop

**What This Reveals**:
- Context window usage patterns
- When compaction happens
- Conversation length patterns
- Context management efficiency

## Recommended Test Sequence

For a comprehensive showcase, run these in order:

1. **Quick Fix** (Case 5) - Establish baseline
2. **Bug Fix with Rejection** (Case 2) - Show iteration
3. **Refactoring** (Case 1) - Show tool variety
4. **Multi-File Feature** (Case 3) - Show complexity
5. **Code Review** (Case 4) - Show analysis patterns

This sequence demonstrates:
- ✅ High acceptance scenarios
- ✅ Rejection and iteration patterns
- ✅ Tool variety
- ✅ Complex multi-file operations
- ✅ Analysis and review patterns

## Metrics to Observe

After running these cases, check:

```bash
# Overall metrics
blueplane metrics

# Session details
blueplane sessions

# Analyze specific session
blueplane analyze <session_id>
```

**Key Metrics to Look For**:
- Acceptance rate (should vary by case type)
- Tool usage distribution (ReadFile vs Edit)
- Average latency per tool
- Tokens used per session
- Lines changed per session
- Conversation turn count
- Context compaction frequency

## Expected Insights

These cases should reveal:

1. **Productivity Patterns**: Which types of tasks are fastest?
2. **Acceptance Patterns**: What gets accepted vs rejected?
3. **Tool Preferences**: Which tools are used most?
4. **Workflow Patterns**: How do you structure conversations?
5. **Efficiency Metrics**: Time, tokens, changes per task type

## Sweet Spot Use Cases

The "sweet spot" for this tool is understanding:

1. **What Works**: Which AI suggestions do you actually use?
2. **What Doesn't**: What gets rejected and why?
3. **How You Work**: Your actual workflow patterns
4. **Productivity Impact**: Real metrics on AI assistance value
5. **Optimization Opportunities**: Where can you improve?

These sample cases are designed to generate data that answers these questions.

