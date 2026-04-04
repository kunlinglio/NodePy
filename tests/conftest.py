"""
Shared pytest fixtures for NodePy tests.

Provides `fake_env` fixture that installs lightweight fake modules into
sys.modules (using pytest's monkeypatch) so tests that import production
modules (e.g. FileManager, CacheManager) can run without real external
dependencies like MinIO, Redis, or a real database.

The fixture yields a dict with helpers that tests may use:
    {
        "MinioClient": <fake Minio client class>,
        "FakeDB": <FakeDB class>,
        "DBModule": <the fake server.models.database module (types.ModuleType)>,
        "SchemaModule": <fake server.models.schema module>,
        "ProjectModule": <fake server.models.project module>,
        "DataManagerModule": <fake server.lib.DataManager module>,
    }

The monkeypatch fixture will automatically restore sys.modules entries
after each test, avoiding pollution of import state across tests.
"""
from pathlib import Path
import sys
import types
import io
from datetime import datetime
from typing import Any

import pytest


# Ensure project root is on sys.path for test collection/imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


@pytest.fixture
def fake_env(monkeypatch) -> dict[str, Any]:
    """
    Install lightweight fake modules that replicate the minimal API surface
    required by FileManager/CacheManager tests and some model imports.

    Returns a dict of helper objects for tests to use.
    """
    # Keep track of what we put into sys.modules via monkeypatch (monkeypatch will undo)
    # 1) Fake minio module and client
    minio_mod = types.ModuleType("minio")

    class S3Error(Exception):
        def __init__(self, *args, code=None, **kwargs):
            super().__init__(*args)
            self.code = code

    minio_mod.S3Error = S3Error

    class FakeMinioClient:
        def __init__(self, *args, **kwargs):
            self.store: dict[str, bytes] = {}
            self.buckets: set[str] = set()

        def bucket_exists(self, bucket: str) -> bool:
            return bucket in self.buckets

        def make_bucket(self, bucket: str) -> None:
            self.buckets.add(bucket)

        def put_object(self, bucket_name: str, object_name: str, data, length: int, metadata=None):
            # Accept file-like or raw bytes
            if hasattr(data, "read"):
                data.seek(0)
                content = data.read()
            else:
                content = data
            self.store[object_name] = bytes(content)

        def get_object(self, bucket_name: str, object_name: str):
            if object_name not in self.store:
                raise S3Error("NoSuchKey", code="NoSuchKey")
            # Return a file-like object which has .read()
            return io.BytesIO(self.store[object_name])

        def remove_object(self, bucket_name: str, object_name: str):
            if object_name not in self.store:
                raise S3Error("NoSuchKey", code="NoSuchKey")
            del self.store[object_name]

        def stat_object(self, bucket_name: str, object_name: str):
            if object_name not in self.store:
                raise S3Error("NoSuchKey", code="NoSuchKey")
            return {"size": len(self.store[object_name])}

    minio_mod.Minio = FakeMinioClient
    monkeypatch.setitem(sys.modules, "minio", minio_mod)

    # 2) Fake server.models.schema with commonly used symbols
    schema_mod = types.ModuleType("server.models.schema")

    class ColType:
        @staticmethod
        def from_ptype(dtype):
            # Return a simple sentinel representing column type
            return f"coltype({str(dtype)})"

    class Schema:
        class Type:
            INT = "int"
            FLOAT = "float"
            STR = "str"
            BOOL = "bool"
            TABLE = "Table"
            FILE = "File"
            DATETIME = "Datetime"
            MODEL = "Model"

        # Provide NO_SPECIFIED_COL constant used in some tests
        NO_SPECIFIED_COL = "__NO_SPECIFIED_COL__"

    schema_mod.ColType = ColType
    schema_mod.Schema = Schema
    monkeypatch.setitem(sys.modules, "server.models.schema", schema_mod)

    # 3) Fake server.models.data_view minimal types (includes TableView/ModelView/DataView)
    dmv_mod = types.ModuleType("server.models.data_view")

    class TableView:
        def __init__(self, cols=None, col_types=None):
            self.cols = cols or {}
            self.col_types = col_types or {}

    class ModelView:
        def __init__(self, model=None, metadata=None):
            self.model = model
            self.metadata = metadata

    class DataView:
        def __init__(self, type=None, value=None):
            self.type = type
            self.value = value

        def model_dump(self, **kwargs):
            # Minimal serialization used by some model code paths in tests
            return {"type": self.type, "value": self.value}

    class DataRef:
        def __init__(self, data_id: int | None = None):
            self.data_id = data_id

    dmv_mod.TableView = TableView
    dmv_mod.ModelView = ModelView
    dmv_mod.DataView = DataView
    dmv_mod.DataRef = DataRef
    monkeypatch.setitem(sys.modules, "server.models.data_view", dmv_mod)

    # 3b) Fake server.models.data - minimal Data class so modules that import `Data`
    # (e.g. CacheManager) can import without pulling in heavy production models.
    data_mod = types.ModuleType("server.models.data")

    class Data:
        def __init__(self, payload=None):
            self.payload = payload

        def extract_schema(self):
            # Return an object compatible with code expecting a `.type` attribute.
            class S:
                type = schema_mod.Schema.Type.TABLE
            return S()

    data_mod.Data = Data
    monkeypatch.setitem(sys.modules, "server.models.data", data_mod)

    # 4) Fake server.lib.DataManager (used by FileManager.clean_orphan_file_sync import)
    dlm_mod = types.ModuleType("server.lib.DataManager")

    class DataManager:
        def __init__(self, *args, **kwargs):
            pass

        def read_sync(self, data_ref=None):
            # Return an object similar to Data containing a file payload when needed.
            class D:
                def extract_schema(self):
                    class S:
                        type = schema_mod.Schema.Type.FILE
                    return S()

                payload = None

            return D()

    dlm_mod.DataManager = DataManager
    monkeypatch.setitem(sys.modules, "server.lib.DataManager", dlm_mod)

    # 5) Fake server.models.project (lightweight Project/ProjWorkflow/ProjUIState)
    proj_mod = types.ModuleType("server.models.project")

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

    # 6) Fake server.models.database minimal implementation and FakeDB
    db_mod = types.ModuleType("server.models.database")

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

    # QueryFake + FakeDB to emulate minimal query/filter/first/all semantics
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
            self._files: list[FileRecord] = []
            self._users: list[UserRecord] = []
            self._projects: list[ProjectRecord] = []
            self._added: list[FileRecord] = []

        def query(self, model):
            return QueryFake(self, model)

        def add(self, obj):
            self._added.append(obj)

        def commit(self):
            # persist FileRecord-like objects into _files
            for o in self._added:
                if isinstance(o, FileRecord):
                    self._files.append(o)
            self._added.clear()

        def rollback(self):
            self._added.clear()

        def delete(self, obj):
            if isinstance(obj, FileRecord):
                for f in list(self._files):
                    if f.file_key == obj.file_key:
                        self._files.remove(f)
                        break

    db_mod.get_session = lambda: iter([FakeDB()])
    monkeypatch.setitem(sys.modules, "server.models.database", db_mod)

    # 7) Provide a minimal server.lib.utils if tests import it early; but we prefer real utils.
    # (We don't inject utils here — tests that need utils will import the real module.)

    # 8) Provide the yield dictionary for tests
    ret = {
        "MinioClient": FakeMinioClient,
        "FakeDB": FakeDB,
        "DBModule": db_mod,
        "SchemaModule": schema_mod,
        "ProjectModule": proj_mod,
        "DataManagerModule": dlm_mod,
    }

    return ret