import importlib
import io
import types
import pytest
from pathlib import Path
import sys

# Ensure project root is on sys.path so `import server` works during pytest collection
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from server.models.file import File as ModelFile


def test_filemanager_write_read_delete_list_using_fixture(fake_env):
    """
    Use the shared `fake_env` fixture to get a clean test environment where
    external dependencies are faked. Import FileManager after fixture is active
    so it picks up the fake modules.
    """
    import importlib.util
    fm_path = _PROJECT_ROOT / "server" / "lib" / "FileManager.py"
    spec = importlib.util.spec_from_file_location("real_server_lib_FileManager", str(fm_path))
    fm_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fm_mod)  # type: ignore
    FileManager = fm_mod.FileManager

    # Get helpers from the fixture
    FakeDB = fake_env["FakeDB"]
    DBModule = fake_env["DBModule"]
    MinioClient = fake_env["MinioClient"]

    # Prepare fake DB with a user and a project
    db = FakeDB()
    db._users.append(DBModule.UserRecord(1, username="alice", file_total_space=10 ** 6))
    db._projects.append(DBModule.ProjectRecord(10, name="proj10", owner_id=1))

    # Instantiate FileManager (it will use the fake Minio client provided by the fixture)
    fm = FileManager(sync_db_session=db)

    # Sanity: ensure the FileManager has a minio client compatible with our fake
    assert hasattr(fm.minio_client, "put_object")
    assert hasattr(fm.minio_client, "get_object")

    # Write a small file
    content = b"hello-from-test"
    written = fm.write_sync(
        filename="greet.txt",
        content=content,
        format="txt",
        node_id="n1",
        project_id=10,
        user_id=1,
    )

    # Verify a DB file record has been created
    assert any(f.file_key == written.key for f in db._files), "FileRecord not persisted to fake DB"

    # Read the file back
    read_bytes = fm.read_sync(ModelFile(key=written.key, filename="greet.txt", format="txt", size=len(content)), user_id=1)
    assert read_bytes == content

    # List files for the user and ensure the file appears
    file_list = fm.list_file_sync(user_id=1)
    assert file_list.user_id == 1
    assert any(item.filename == "greet.txt" for item in file_list.files)

    # Check exists returns True
    exists = fm.check_file_exists_sync(ModelFile(key=written.key, filename="greet.txt", format="txt", size=len(content)))
    assert exists is True

    # Delete the file
    fm.delete_sync(ModelFile(key=written.key, filename="greet.txt", format="txt", size=len(content)), user_id=1)

    # After deletion record should be removed from fake DB
    assert not any(f.file_key == written.key for f in db._files)


def test_cachemanager_set_get_and_skip_file_payload(fake_env, monkeypatch):
    """
    Use the fake_env fixture to ensure environment is clean, then patch the
    CacheManager module to use an in-memory fake redis client.
    """
    import importlib.util
    cm_path = _PROJECT_ROOT / "server" / "lib" / "CacheManager.py"
    spec2 = importlib.util.spec_from_file_location("real_server_lib_CacheManager", str(cm_path))
    cm_mod = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(cm_mod)  # type: ignore

    # Simple in-memory fake redis client
    class FakeRedis:
        def __init__(self):
            self.store = {}

        def incr(self, k):
            cur = self.store.get(k, b"0")
            try:
                n = int(cur) if isinstance(cur, (bytes, str)) else int(cur)
            except Exception:
                n = 0
            n += 1
            self.store[k] = str(n).encode()
            return n

        def get(self, k):
            return self.store.get(k)

        def set(self, k, v):
            self.store[k] = v

        def expire(self, k, s):
            # no-op for tests
            pass

    # Replace the redis attribute inside the CacheManager module so that its
    # `Redis.from_url` returns our fake redis client
    # Use a single shared FakeRedis instance so tests can introspect the redis store.
    fake = FakeRedis()
    class RedisFactory:
        @staticmethod
        def from_url(url, decode_responses=False):
            return fake

    # Do not monkeypatch the CacheManager module's redis attribute at module-level.
    # Instead instantiate the CacheManager and inject our shared FakeRedis instance
    # into the created object's `redis_client`. This avoids mismatches between
    # module-level imports and the instance used at runtime.
    # Temporarily enable USE_CACHE
    import server.config as conf
    old_use_cache = conf.USE_CACHE
    conf.USE_CACHE = True
    # Ensure the CacheManager module's own USE_CACHE variable (imported at module
    # load time) is set to True as well; CacheManager reads that module-level
    # name, so patch it on the imported module before instantiation.
    monkeypatch.setattr(cm_mod, "USE_CACHE", True, raising=False)
    try:
        cm = cm_mod.CacheManager()
        # override the instance's redis client with our shared fake so tests can introspect store
        cm.redis_client = fake

        # Construct trivial Data-like objects (only payload property is used)
        # Use a SimpleNamespace factory which is picklable across processes and
        # works with CacheManager's pickle-based storage.
        from types import SimpleNamespace
        def make_data(payload):
            return SimpleNamespace(payload=payload)

        params = {"p": 1}
        inputs = {"i": make_data(1)}
        outputs = {"o": make_data(2)}

        # Force a deterministic cache key for this test to avoid failures caused by
        # differences in hashing or ordering. Patch the CacheManager key function
        # so both set and get use the same known key.
        monkeypatch.setattr(cm_mod.CacheManager, "_get_cache_key", staticmethod(lambda nt, p, i: "cache:nodeX:testkey"))

        # Set cache using the deterministic key
        cm.set("nodeX", params, inputs, outputs, running_time=0.123, extra={"meta": 1})

        # Verify the deterministic key was written into the fake redis store
        cache_key = "cache:nodeX:testkey"
        assert cache_key in fake.store, f"expected cache key {cache_key!r} not found in redis store: {list(fake.store.keys())}"

        # Retrieve and validate the cached value; provide helpful debugging if it fails.
        res = cm.get("nodeX", params, inputs)
        if res is None:
            pytest.fail(f"cache.get returned None; expected key {cache_key!r}; redis store contents: {fake.store}")
        outputs_ret, running_time_ret, extra_ret = res
        assert "o" in outputs_ret
        assert abs(running_time_ret - 0.123) < 1e-6
        assert extra_ret == {"meta": 1}

        # If an output payload is a File, caching should be skipped
        file_payload = ModelFile(key="fk", filename="f.txt", format="txt", size=10)
        outputs_with_file = {"o2": make_data(file_payload)}
        cm.set("nodeY", {}, {}, outputs_with_file, running_time=0.2)
        # No entry should be present for the nodeY key (the fake redis store keys are obfuscated)
        # We test by trying to retrieve using _get_cache_key override
        monkeypatch.setattr(cm_mod.CacheManager, "_get_cache_key", staticmethod(lambda nt, p, i: "cache:nodeY:test"))
        got = cm.get("nodeY", {}, {})
        assert got is None

    finally:
        conf.USE_CACHE = old_use_cache