CWE_EVALUATOR_USR_PROMPT = """A CWE vulnerability has been injected into student code. Please evaluate how effective this injection is as a teaching tool.

Course context:
{course_level_description}

Assignment objectives:
{assignment_objectives}

CWE: {cwe_id}

Original student code:
```
{original_code}
```

CWE-injected version:
```
{modified_code}
```

Evaluate this injection based on the 4 criteria listed in your instructions."""