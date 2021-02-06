import os
import sys
import tempfile
import time
import datetime
import pytest
import pathlib

os.chdir("auto_trader_client")
sys.path.append(os.getcwd())
import auto_trader_client.src.order_monitor as om


def test_check_new_file_valid_file():
    """Returns new files"""
    with tempfile.TemporaryDirectory() as tmp:
        obj = om.OrderMonitor(tmp)
        num_files = 5
        files = ["".join(["test", str(x), ".json"]) for x in range(num_files)]
        for f in files:
            pathlib.Path(os.path.join(tmp, f)).touch()
        assert obj._check_new_files() == files


def test_check_new_file_old_files():
    """Function does not return old files"""
    with tempfile.TemporaryDirectory() as tmp:
        num_files = 5
        files = ["".join(["test", str(x), ".json"]) for x in range(num_files)]
        for f in files:
            pathlib.Path(os.path.join(tmp, f)).touch()
        time.sleep(.001)
        obj = om.OrderMonitor(tmp)
        print("killing time")
        assert obj._check_new_files() == []


def test_is_new_order_file_valid():
    """_is_new_order_file method returns True for valid file"""
    with tempfile.TemporaryFile(suffix=".json") as tmp:
        obj = om.OrderMonitor(tempfile.gettempdir())
        assert os.path.basename(tmp.name) not in obj._directory_content
        assert os.path.splitext(os.path.basename(tmp.name))[-1] == obj._order_ext
        assert obj._is_new_order_file(os.path.basename(tmp.name)) is True


def test_is_new_order_file_invalid_ext():
    """_is_new_order_file method returns False for invalid extensions"""
    extensions = [".jsn", "json", ".jsons", ".py", ".txt", ""]
    for ext in extensions:
        with tempfile.TemporaryFile(suffix=ext) as tmp:
            obj = om.OrderMonitor(tempfile.gettempdir())
            assert os.path.splitext(os.path.basename(tmp.name))[-1] != obj._order_ext
            assert obj._is_new_order_file(os.path.basename(tmp.name)) is False


def test_is_new_order_file_directory_not_file():
    """_is_new_order_file method returns False if file-like is directory"""
    with tempfile.TemporaryDirectory(suffix=".json") as tmp:
        obj = om.OrderMonitor(tempfile.gettempdir())
        assert os.path.isdir(tmp) is True
        assert obj._is_new_order_file(os.path.basename(tmp)) is False


def test_is_new_order_file_already_exists():
    """_is_new_order_file method returns for exisiting file"""
    with tempfile.TemporaryFile(suffix=".json") as tmp:
        obj = om.OrderMonitor(tempfile.gettempdir())
        obj._directory_content.add(os.path.basename(tmp.name))
        assert os.path.basename(tmp.name) in obj._directory_content
        assert obj._is_new_order_file(os.path.basename(tmp.name)) is False


def test_get_creation_time(monkeypatch):
    """Test POSIX systems that use os.path.getmtime"""
    with tempfile.TemporaryFile() as tmp:
        tempdir = tempfile.gettempdir()

        # POSIX systems
        monkeypatch.setattr(os, "name", "posix")
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(tmp.name), tz=datetime.timezone.utc)
        obj = om.OrderMonitor(tempdir)
        dt = obj._get_creation_time(tempdir, tmp.name)
        assert dt == mtime

        # Windows Systems
        monkeypatch.setattr(os, "name", "nt")
        ctime = datetime.datetime.fromtimestamp(os.path.getctime(tmp.name),
                                                tz=datetime.timezone.utc)
        obj = om.OrderMonitor(tempdir)
        dt = obj._get_creation_time(tempdir, tmp.name)
        assert dt == ctime

        # Other systems
        monkeypatch.setattr(os, "name", "other")
        with pytest.raises(OSError):
            obj = om.OrderMonitor(tempdir)
            dt = obj._get_creation_time(tempdir, tmp.name)
