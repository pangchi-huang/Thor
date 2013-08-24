Thor
====

My pdf prototype tool

##Prerequisite

 1. [poppler][1]
 2. [poppler-data][2]

## Install

    python setup.py develop

## Test

 - Auto-test (watching .py)
  - `run_pyspecs.py`
 - Run all tests
  - `pyspecs_.py`

## TroubleShooting

 - If `Symbol not found: ___xmlStructuredErrorContext` error occured, try
    pip uninstall lxml
    STATIC_DEPS=true pip install lxml

  [1]: http://poppler.freedesktop.org/poppler-0.24.0.tar.xz
  [2]: http://poppler.freedesktop.org/poppler-data-0.4.6.tar.gz