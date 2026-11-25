# Test cases and results

[PDF catalogue](test-cases.pdf) · [LaTeX source](test-cases.tex) · [Machine-readable results](results.json)

Run on **25 November 2026**: **36 passed**, zero failed. Each parameterized role/route combination is a separate test case. The PDF records steps, expected behavior, observed result and the source test name.

[Live demonstration and browser evidence](../final-verification.md)

```shell
python -m pytest -q --junitxml=tmp/final-qa/junit.xml
python scripts/build_test_catalog.py
cd docs/test-cases && tectonic test-cases.tex
```
