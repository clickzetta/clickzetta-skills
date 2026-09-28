# Converter outputs from Apache Ossie

These Ossie files are copied unchanged from the test fixtures of the Apache Ossie converters
(https://github.com/apache/ossie, `converters/`, commit `fc6c9df`) and are licensed under the
Apache License, Version 2.0. They are used by `tests/converters/run_converter_smoke.sh` to check
that files written by other tools import into ClickZetta.

| File | Source in apache/ossie |
|---|---|
| databricks_fixtureA.ossie.yaml | converters/databricks/tests/fixtures/fixtureA_ossie.yaml |
| databricks_fixtureB.ossie.yaml | converters/databricks/tests/fixtures/fixtureB_ossie.yaml |
| databricks_tpcds.ossie.yaml | converters/databricks/tests/fixtures/tpcds_ossie.yaml |
| omni_fixtureA.ossie.yaml | converters/omni/tests/fixtures/fixtureA_ossie.yaml |
| nvidia_sales.ossie.yaml | converters/nvidia/tests/fixtures/sales.ossie.yaml |
| gooddata_tpcds.ossie.yaml | converters/gooddata/tests/fixtures/ossie_tpcds.yaml |
| orionbelt_obml.ossie.yaml | converters/orionbelt/tests/fixtures/obml_as_ossie.yaml |
| orionbelt_tpcds.ossie.yaml | converters/orionbelt/tests/fixtures/tpcds_ossie.yaml |
