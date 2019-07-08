# How to run tests with coverage
`pip install -r requirements-test.txt`

`pytest --cov-report html:cov_html --cov-report annotate:cov_annotate --cov=../freeplane_schema .`