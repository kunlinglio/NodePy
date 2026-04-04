import sys
from pathlib import Path
import io
import time
import pickle

import pytest

# Ensure project root is on sys.path so `import server` works
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# The previous test file injected many fake modules at import time and performed
# module-level imports of the production code. That pollutes sys.modules and
# caused other tests to import lightweight mocks unexpectedly.
#
# Refactor: provide a fixture `fake_env` that registers lightweight fake modules
# using pytest's monkeypatch. Tests will import production modules (FileManager,
# CacheManager) inside test functions after the fixture has been applied.
#
# This keeps global import state clean and avoids interfering with unrelated tests.

@pytest.fixture
def fake_env(monkeypatch):
    """Set up lightweight fake external dependencies in sys.modules for tests."""
    # --- Fake minio ---
    minio_mod = type(sys)("minio")
    class S3Error(Exception):
        def __init__(self, *args, code=None, **kwargs):
            super().__init__(*args)
            self.code = code
    minio_mod.S3Error = S3Error

    class _FakeMinioClient:
        def __init__(self, *args, **kwargs):
            self.store = {}
            self.buckets = set()

        def bucket_exists(self, bucket):
            return bucket in self.buckets

        def make_bucket(self, bucket):
            self.buckets.add(bucket)

        def put_object(self, bucket_name, object_name, data, length, metadata=None):
            if hasattr(data, "read"):
                data.seek(0)
                content = data.read()
            else:
                content = data
            self.store[object_name] = bytes(content)

        def get_object(self, bucket_name, object_name):
            if object_name not in self.store:
                raise S3Error("NoSuchKey", code="NoSuchKey")
            return io.BytesIO(self.store[object_name])

        def remove_object(self, bucket_name, object_name):
            if object_name not in self.store:
                raise S3Error("NoSuchKey", code="NoSuchKey")
            del self.store[object_name]

        def stat_object(self, bucket_name, object_name):
            if object_name not in self.store:
                raise S3Error("NoSuchKey", code="NoSuchKey")
            return {"size": len(self.store[object_name])}

    minio_mod.Minio = _FakeMinioClient
    monkeypatch.setitem(sys.modules, "minio", minio_mod)

    # --- Fake server.models.schema ---
    schema_mod = type(sys)("server.models.schema")
    class ColType:
        @staticmethod
        def from_ptype(dtype):
            return f"coltype({str(dtype)})"
    class Schema:
        class Type:
            FILE = "file"
    schema_mod.ColType = ColType
    schema_mod.Schema = Schema
    monkeypatch.setitem(sys.modules, "server.models.schema", schema_mod)

    # --- Fake server.models.data_view ---
    dmv_mod = type(sys)("server.models.data_view")
    class DataRef:
        def __init__(self, data_id=None):
            self.data_id = data_id
    dmv_mod.DataRef = DataRef
    monkeypatch.setitem(sys.modules, "server.models.data_view", dmv_mod)

    # --- Fake server.lib.DataManager (used by FileManager.clean_orphan_file_sync) ---
    dlm_mod = type(sys)("server.lib.DataManager")
    class DataManager:
        def __init__(self, *args, **kwargs):
            pass
        def read_sync(self, data_ref):
            class D:
                def extract_schema(self):
                    class S:
                        type = "other"
                    return S()
                payload = None
            return D()
    dlm_mod.DataManager = DataManager
    monkeypatch.setitem(sys.modules, "server.lib.DataManager", dlm_mod)

    # --- Fake server.models.database (minimal) ---
    db_mod = type(sys)("server.models.database")
    from datetime import datetime

    class Col:
        def __init__(self, name):
            self.name = name
        def __eq__(self, other):
            return lambda obj: getattr(obj, self.name) == other
        def is_(self, other):
            return lambda obj: getattr(obj, self.name) == other
        def isnot(self, other):
            return lambda obj: getattr(obj, self.name) is not other

    class FileRecord:
        filename = Col("filename")
        file_key = Col("file_key")
        format = Col("format")
        user_id = Col("user_id")
        project_id = Col("project_id")
        node_id = Col("node_id")
        file_size = Col("file_size")
        is_deleted = Col("is_deleted")
        last_modify_time = Col("last_modify_time")

        def __init__(self, file_key, filename, format, user_id, project_id, node_id, file_size):
            self.file_key = file_key
            self.filename = filename
            self.format = format
            self.user_id = user_id
            self.project_id = project_id
            self.node_id = node_id
            self.file_size = file_size
            self.last_modify_time = datetime.now()
            self.is_deleted = False
            self.id = id(self)

    class UserRecord:
        id = Col("id")
        username = Col("username")
        file_total_space = Col("file_total_space")
        def __init__(self, id, username="u", file_total_space=10**9):
            self.id = id
            self.username = username
            self.file_total_space = file_total_space

    class ProjectRecord:
        id = Col("id")
        name = Col("name")
        def __init__(self, id, name="p", owner_id=None, workflow=None, ui_state=None):
            self.id = id
            self.name = name
            self.owner_id = owner_id
            self.workflow = workflow or {"nodes": []}
            self.ui_state = ui_state or {}
            self.thumb = None
            self.updated_at = datetime.now()

    db_mod.FileRecord = FileRecord
    db_mod.UserRecord = UserRecord
    db_mod.ProjectRecord = ProjectRecord

    class QueryFake:
        def __init__(self, db, model):
            self.db = db
            self.model = model
            self._conds = []
            self._entities = None

        def with_entities(self, *ents):
            self._entities = ents
            return self

        def filter(self, *conds):
            for c in conds:
                if callable(c):
                    self._conds.append(c)
                else:
                    pass
            return self

        def all(self):
            items = []
            if self.model is FileRecord:
                for f in self.db._files:
                    if all(cond(f) for cond in self._conds):
                        if self._entities:
                            vals = tuple(getattr(f, e.name) for e in self._entities)
                            items.append(vals)
                        else:
                            items.append(f)
            elif self.model is UserRecord:
                for u in self.db._users:
                    if all(cond(u) for cond in self._conds):
                        items.append(u)
            elif self.model is ProjectRecord:
                for p in self.db._projects:
                    if all(cond(p) for cond in self._conds):
                        items.append(p)
            return items

        def first(self):
            all_items = self.all()
            return all_items[0] if all_items else None

    class FakeDB:
        def __init__(self):
            self._files = []
            self._users = []
            self._projects = []
            self._added = []

        def query(self, model):
            return QueryFake(self, model)

        def add(self, obj):
            self._added.append(obj)

        def commit(self):
            for o in self._added:
                if isinstance(o, FileRecord):
                    self._files.append(o)
            self._added.clear()

        def rollback(self):
            self._added.clear()

        def delete(self, obj):
            if isinstance(obj, FileRecord):
                for f in self._files:
                    if f.file_key == obj.file_key:
                        self._files.remove(f)
                        break

    db_mod.get_session = lambda: iter([FakeDB()])
    monkeypatch.setitem(sys.modules, "server.models.database", db_mod)

    # --- Mock server.models.project (lightweight) ---
    proj_mod = type(sys)("server.models.project")
    class ProjWorkflow:
        def __init__(self, nodes=None):
            self.nodes = nodes or []
        @classmethod
        def model_validate(cls, data):
            if isinstance(data, dict):
                nodes = data.get("nodes", [])
            else:
                nodes = []
            return ProjWorkflow(nodes=nodes)

    class ProjUIState:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs or {})

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

    proj_mod.ProjWorkflow = ProjWorkflow
    proj_mod.ProjUIState = ProjUIState
    proj_mod.Project = Project
    monkeypatch.setitem(sys.modules, "server.models.project", proj_mod)

    # Yield a tuple containing the created fake Minio client class for tests that
    # wish to instantiate or introspect it.
    yield {"MinioClient": _FakeMinioClient, "FakeDB": FakeDB, "DBFileRecord": FileRecord, "DBUserRecord": UserRecord, "DBProjectRecord": ProjectRecord}

    # monkeypatch will undo sys.modules changes automatically