CWE_INJECTOR_USR_PROMPT = """The following code was written by a student in the context of this university course and assignment:

Course description:
{course_description}

Assignment description:
{assignment_description}

CWE to inject:
- CWE ID: {cwe_id}
- Title: {cwe_title}
- Description: {cwe_description}

Student code:
```
{student_code}
```

Inject the vulnerability now."""