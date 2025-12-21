# How to push this

Use the token for `dkorolev` on https://pypi.org/manage/account/.

```
python3 -m venv myenv
python setup.py bdist_wheel
twine upload --verbose dist/*
```
