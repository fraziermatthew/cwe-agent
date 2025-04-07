LO_GEN_USR_PROMPT = """Generate one multiple-choice question and one open-ended question about the following vulnerable code.

CWE: {cwe_id} - {cwe_title}

CWE-injected code:
```
{modified_code}
```

Course level: {course_level_description}

The questions should test understanding of the vulnerability, not just code comprehension."""