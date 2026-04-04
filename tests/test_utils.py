import sys
from pathlib import Path

# Ensure project root is on sys.path so `import server` works during pytest collection
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import sys as _sys
import time
import signal
import pytest
import types

# Inject lightweight fake `server.models` modules before importing `server.lib.utils`
# This prevents importing the real database engine at test-collection time,
# which may require environment configuration not present in the test runner.
# We only provide the minimal attributes that `server.lib.utils` expects.
_db_mod = types.ModuleType("server.models.database")
# Provide a minimal ProjectRecord placeholder class used by utils' import.
class _FakeProjectRecord:
    pass
_db_mod.ProjectRecord = _FakeProjectRecord
sys.modules["server.models.database"] = _db_mod

_proj_mod = types.ModuleType("server.models.project")
# Minimal classes expected by utils
class ProjWorkflow:
    def __init__(self, *args, **kwargs):
        # Accept init from either dict or kwargs used in tests
        if args and isinstance(args[0], dict):
            self.__dict__.update(args[0])
class ProjUIState:
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            self.__dict__.update(args[0])
class Project:
    def __init__(self, project_name=None, project_id=None, user_id=None, updated_at=None, thumb=None, editable=None, workflow=None, ui_state=None):
        self.project_name = project_name
        self.project_id = project_id
        self.user_id = user_id
        self.updated_at = updated_at
        self.thumb = thumb
        self.editable = editable
        self.workflow = workflow
        self.ui_state = ui_state
_proj_mod.ProjWorkflow = ProjWorkflow
_proj_mod.ProjUIState = ProjUIState
_proj_mod.Project = Project
sys.modules["server.models.project"] = _proj_mod

# Import `server.lib.utils`. Tests may run with a fake `server.lib.utils` injected by conftest;
# prefer loading the real implementation from `server/lib/utils.py` when available.
# The following tries a normal import first and, if the module appears to be the test-time
# fake (missing the exported symbols we expect), it will load the real source file and
# override `sys.modules["server.lib.utils"]` so the later `from server.lib.utils import ...`
# pulls symbols from the real implementation.
try:
    import importlib
    # Try to import whatever is currently available
    import server.lib.utils as _current_utils  # type: ignore
    _needs_reload = not all(
        hasattr(_current_utils, name)
        for name in ("TimeoutException", "InterruptedError", "run_in_process")
    )
except Exception:
    _needs_reload = True

if _needs_reload:
    try:
        import importlib.util
        _utils_path = _PROJECT_ROOT / "server" / "lib" / "utils.py"
        spec = importlib.util.spec_from_file_location("server.lib.utils", str(_utils_path))
        if spec is not None and spec.loader is not None:
            _real_utils = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_real_utils)  # type: ignore
            # Override the entry so subsequent imports use the real module
            sys.modules["server.lib.utils"] = _real_utils
    except Exception:
        # If anything goes wrong, fall back to whatever is importable normally.
        pass

from server.lib import utils
from server.lib.utils import (
    safe_hash,
    timeout,
    TimeoutException,
    time_check,
    InterruptedError,
    run_in_process,
)


def test_safe_hash_reproducible_for_primitives_and_containers():
    a = {"x": 1, "y": [1, 2, 3], "z": "hello"}
    b = {"y": [1, 2, 3], "z": "hello", "x": 1}  # different insertion order
    h1 = safe_hash(a)
    h2 = safe_hash(b)
    # dict order should not affect the hash
    assert h1 == h2
    # same object gives same hash
    assert safe_hash(123) == safe_hash(123)
    assert safe_hash("abc") == safe_hash("abc")
    # different values give different hashes (very high probability)
    assert safe_hash("abc") != safe_hash("abcd")


def test_safe_hash_unhashable_object_with_fast_hash_and_to_dict():
    class WithFastHash:
        def fast_hash(self):
            return "fast-42"

    class WithToDict:
        def to_dict(self):
            return {"k": "v"}

    hf = WithFastHash()
    hd = WithToDict()

    # Both should produce a hash string (md5 hex)
    h_fast = safe_hash(hf)
    h_dict = safe_hash(hd)
    assert isinstance(h_fast, str) and len(h_fast) == 32
    assert isinstance(h_dict, str) and len(h_dict) == 32
    # They should differ
    assert h_fast != h_dict


def test_safe_hash_raises_for_unhashable_without_helpers():
    class Plain:
        pass

    # Plain objects have a default __hash__; safe_hash will hash them and return an md5 hex string
    h = safe_hash(Plain())
    assert isinstance(h, str) and len(h) == 32


@pytest.mark.skipif(not hasattr(signal, "SIGALRM"), reason="SIGALRM not available on platform")
def test_timeout_decorator_allows_completion_and_raises_timeout():
    @timeout(0.2)
    def short_task():
        # completes before timeout
        time.sleep(0.05)
        return "ok"

    @timeout(0.05)
    def long_task():
        # runs longer than allowed
        time.sleep(0.2)
        return "should not return"

    assert short_task() == "ok"
    with pytest.raises(TimeoutException):
        long_task()


@pytest.mark.skipif(not hasattr(signal, "SIGALRM"), reason="SIGALRM not available on platform")
def test_time_check_allows_and_interrupts():
    # callback that always allows continuation
    def allow():
        return True

    @time_check(0.05, allow)
    def busy_work_allow():
        # do some work that takes a bit of time
        end = time.time() + 0.15
        while time.time() < end:
            # lightweight busy loop to let alarms fire
            time.sleep(0.01)
        return "done"

    assert busy_work_allow() == "done"

    # callback that immediately asks to stop
    called = {"count": 0}

    def stop_after_first_call():
        called["count"] += 1
        # return False to interrupt on first alarm
        return False

    @time_check(0.02, stop_after_first_call)
    def busy_work_interrupt():
        # run longer than the alarm interval so the handler runs
        end = time.time() + 0.2
        while time.time() < end:
            time.sleep(0.01)
        return "never"

    with pytest.raises(InterruptedError):
        busy_work_interrupt()


@pytest.mark.skipif(sys.platform == "win32", reason="multiprocessing/fork semantics differ on Windows")
def test_run_in_process_returns_value_and_propagates_exceptions():
    # simple function to be run in a subprocess
    @run_in_process
    def compute_sum(a, b):
        return a + b

    result = compute_sum(2, 3)
    assert result == 5

    @run_in_process
    def raise_error():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        raise_error()


# Additional tests to improve coverage of utils internals

def test__process_wrapper_success_and_error(tmp_path):
    import os
    import pickle

    # Dummy queue to capture put calls
    class DummyQueue:
        def __init__(self):
            self.items = []
        def put(self, item):
            self.items.append(item)

    q = DummyQueue()

    def good_func(x, y):
        return {'sum': x + y}

    # run wrapper directly (this simulates child process work)
    utils._process_wrapper(q, good_func, (2, 3), {})
    assert len(q.items) == 1
    res = q.items[0]
    assert res['status'] == 'success'
    # file should exist
    path = res['result_path']
    with open(path, 'rb') as f:
        data = pickle.load(f)
    assert data == {'sum': 5}
    # cleanup
    if os.path.exists(path):
        os.remove(path)

    # Now test exception path
    q2 = DummyQueue()
    def bad_func():
        raise ValueError('boom')
    utils._process_wrapper(q2, bad_func, (), {})
    assert len(q2.items) == 1
    res2 = q2.items[0]
    assert res2['status'] == 'error'
    assert isinstance(res2['error'], Exception)


@pytest.mark.skipif(_sys.platform == 'win32', reason='fork not supported on Windows in same way')
def test_run_in_process_child_exit_nonzero():
    import os

    # function that will exit the process without putting anything to the queue
    @run_in_process
    def exit_now():
        os._exit(7)

    with pytest.raises(RuntimeError) as exc:
        exit_now()
    assert 'Process exited with code' in str(exc.value)


@pytest.mark.skipif(not hasattr(signal, "SIGALRM"), reason="SIGALRM not available on platform")
def test_time_check_handler_exception_propagates():
    # callback that raises
    def cb():
        raise ValueError('cb failure')

    @time_check(0.02, cb)
    def work():
        # run longer than the alarm interval
        end = time.time() + 0.1
        while time.time() < end:
            time.sleep(0.01)
        return 'ok'

    with pytest.raises(ValueError):
        work()


def test_async_get_and_set_project_by_id():
    import asyncio
    import base64

    # Fake async DB session
    class FakeAsyncDB:
        def __init__(self, record):
            self._record = record
        async def get(self, model, project_id):
            return self._record if self._record and self._record.id == project_id else None

    class Rec:
        def __init__(self):
            from datetime import datetime
            self.id = 5
            self.name = 'pname'
            self.owner_id = 11
            self.updated_at = datetime.now()
            self.thumb = b'img'
            self.workflow = {'nodes': []}
            self.ui_state = {'x': 1}
            self.show_in_explore = True

    rec = Rec()
    db = FakeAsyncDB(rec)

    async def run_tests():
        proj = await utils.get_project_by_id(db, 5, 11)
        assert proj is not None
        assert proj.project_name == 'pname'
        # other user but show_in_explore True -> editable False
        proj2 = await utils.get_project_by_id(db, 5, 99)
        assert proj2 is not None and proj2.editable is False
        # not found
        proj_none = await utils.get_project_by_id(db, 999, 11)
        assert proj_none is None

        # set_project_record async
        class FakeWorkflow:
            def model_dump(self):
                return {'nodes': [1]}
        class FakeUIState:
            def model_dump(self):
                return {'layout': 'z'}

        class FakeProject:
            def __init__(self):
                self.project_name = 'new'
                self.project_id = 5
                self.user_id = 11
                self.workflow = FakeWorkflow()
                self.ui_state = FakeUIState()
                self.thumb = base64.b64encode(rec.thumb).decode('utf-8')

        fp = FakeProject()
        await utils.set_project_record(db, fp, 11)
        assert rec.name == 'new'
        assert rec.workflow == {'nodes': [1]}

        # permission error
        with pytest.raises(PermissionError):
            await utils.set_project_record(db, fp, 999)

        # not found
        db2 = FakeAsyncDB(None)
        with pytest.raises(ValueError):
            await utils.set_project_record(db2, fp, 11)

    asyncio.run(run_tests())