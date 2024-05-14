import os
import sys

import pytest

from scrapegraphai.utils.sys_dynamic_import import dynamic_import, srcfile_import


def _create_sample_file(filepath: str, content: str):
    """creates a sample file at some path with some content"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def _delete_sample_file(filepath: str):
    """deletes a sample file at some path"""
    if os.path.exists(filepath):
        os.remove(filepath)


def test_srcfile_import_success():
    modpath = "example1.py"
    modname = "example1"

    _create_sample_file(modpath, "def foo(): return 'bar'")

    module = srcfile_import(modpath, modname)

    assert hasattr(module, "foo")
    assert module.foo() == "bar"
    assert modname in sys.modules

    _delete_sample_file(modpath)


def test_srcfile_import_missing_spec():
    modpath = "nonexistent1.py"
    modname = "nonexistent1"

    with pytest.raises(FileNotFoundError):
        srcfile_import(modpath, modname)


def test_srcfile_import_missing_spec_loader(mocker):
    modpath = "example2.py"
    modname = "example2"

    _create_sample_file(modpath, "")

    mock_spec = mocker.Mock(loader=None)

    mocker.patch("importlib.util.spec_from_file_location", return_value=mock_spec)

    with pytest.raises(ImportError) as error_info:
        srcfile_import(modpath, modname)

    assert "missing spec loader for module at" in str(error_info.value)

    _delete_sample_file(modpath)


def test_dynamic_import_success():
    print(sys.modules)
    modname = "playwright"
    assert modname not in sys.modules

    dynamic_import(modname)

    assert modname in sys.modules

    import playwright  # noqa: F401


def test_dynamic_import_module_already_imported():
    modname = "json"

    import json  # noqa: F401

    assert modname in sys.modules

    dynamic_import(modname)

    assert modname in sys.modules


def test_dynamic_import_import_error_with_custom_message():
    modname = "nonexistent2"
    message = "could not import module"

    with pytest.raises(ImportError) as error_info:
        dynamic_import(modname, message=message)

    assert str(error_info.value) == message
    assert modname not in sys.modules
