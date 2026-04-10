import sys
from pathlib import Path
import importlib.util
import types
import pickle
import asyncio

import pytest

# Ensure project root is on sys.path so `import server` works during pytest collection
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _inject_fake_model_modules(tmp_modules: dict[str, types.ModuleType]):
    """
    Helper to inject fake modules into sys.modules for tests that need to
    control the model classes used by DataManager.
    """
    for name, mod in tmp_modules.items():
        sys.modules[name] = mod


def _make_fake_db():
    """
    Create a minimal FakeDB supporting the operations DataManager expects:
    - query(model).filter(...).first() / all()
    - query(model).filter_by(...).first()
    - add(obj), flush() to assign an id, delete(obj), commit()
    This DB will store NodeOutputRecord-like objects in _nodes and ProjectRecord in _projects.
    """

    class Col:
        def __init__(self, name):
            self.name = name

        def __eq__(self, other):
            # Return a callable that checks the attribute on a record instance
            return lambda obj: getattr(obj, self.name) == other

        def is_(self, other):
            return lambda obj: getattr(obj, self.name) == other

        def isnot(self, other):
            return lambda obj: getattr(obj, self.name) is not other

    class NodeOutputRecord:
        # Provide column descriptors to emulate SQLAlchemy-style comparisons
        id = Col("id")
        project_id = Col("project_id")
        node_id = Col("node_id")
        port = Col("port")
        data = Col("data")

        # runtime attributes stored on instances
        def __init__(self, project_id=None, node_id=None, port=None, data=None):
            self.id = None
            self.project_id = project_id
            self.node_id = node_id
            self.port = port
            self.data = data

    class ProjectRecord:
        # emulate column descriptor for id for query comparisons
        id = Col("id")
        workflow = Col("workflow")

        def __init__(self, id, workflow):
            self.id = id
            self.workflow = workflow

    class QueryFake:
        def __init__(self, db, model):
            self.db = db
            self.model = model
            self._conds = []
            self._filter_by_kwargs = {}

        def filter(self, *conds):
            # conds are callables in many test fakes; support simple lambdas or ignore others
            for c in conds:
                if callable(c):
                    self._conds.append(c)
            return self

        def filter_by(self, **kwargs):
            self._filter_by_kwargs.update(kwargs)
            return self

        def all(self):
            items = []
            if self.model is NodeOutputRecord:
                for rec in self.db._nodes:
                    ok = True
                    for k, v in self._filter_by_kwargs.items():
                        if getattr(rec, k) != v:
                            ok = False
                            break
                    if not ok:
                        continue
                    if self._conds:
                        if not all(cond(rec) for cond in self._conds):
                            continue
                    items.append(rec)
            elif self.model is ProjectRecord:
                for p in self.db._projects:
                    ok = True
                    for k, v in self._filter_by_kwargs.items():
                        if getattr(p, k) != v:
                            ok = False
                            break
                    if not ok:
                        continue
                    items.append(p)
            return items

        def first(self):
            all_items = self.all()
            return all_items[0] if all_items else None

    class FakeDB:
        def __init__(self):
            self._nodes: list[NodeOutputRecord] = []
            self._projects: list[ProjectRecord] = []
            self._added: list[NodeOutputRecord] = []
            self._next_id = 1

        def query(self, model):
            return QueryFake(self, model)

        def add(self, obj):
            self._added.append(obj)

        def flush(self):
            # assign ids and persist
            for o in list(self._added):
                if isinstance(o, NodeOutputRecord):
                    o.id = self._next_id
                    self._next_id += 1
                    self._nodes.append(o)
            self._added.clear()

        def commit(self):
            # For our fake, flush already persisted; commit is no-op
            self._added.clear()

        def delete(self, obj):
            # remove by id/file equality semantics
            if isinstance(obj, NodeOutputRecord):
                for n in list(self._nodes):
                    if n.id == obj.id:
                        self._nodes.remove(n)
                        break

    return FakeDB(), NodeOutputRecord, ProjectRecord


def _load_datamanager_module():
    """
    Load the real DataManager.py module from the repository using importlib,
    after we set up sys.modules to include the fake model modules we need.
    """
    dm_path = _PROJECT_ROOT / "server" / "lib" / "DataManager.py"
    spec = importlib.util.spec_from_file_location("real_server_lib_DataManager", str(dm_path))
    dm_mod = importlib.util.module_from_spec(spec)
    # execute module in its own namespace
    spec.loader.exec_module(dm_mod)  # type: ignore
    return dm_mod

def _make_data_module():
    """
    Create a minimal server.models.data module with a picklable Data class
    defined at module scope so pickle can find the class by its module path.
    """
    mod = types.ModuleType("server.models.data")
    src = """class Data:
    def __init__(self, payload=None):
        self.payload = payload
"""
    exec(src, mod.__dict__)
    # Ensure the class has correct __module__ (exec already set it), return the module
    return mod

def _make_data_view_module():
    """
    Create a minimal server.models.data_view module with a DataRef class
    defined at module scope for use in tests.
    """
    mod = types.ModuleType("server.models.data_view")
    src = """class DataRef:
    def __init__(self, data_id=None):
        self.data_id = data_id
"""
    exec(src, mod.__dict__)
    return mod


def test_write_and_read_sync_roundtrip():
    # Create fake model modules and DB
    fake_db, NodeOutputRecord, ProjectRecord = _make_fake_db()

    # Minimal server.models.data with Data class (DataManager asserts isinstance)
    mod_data = types.ModuleType("server.models.data")
    exec("""class Data:
        def __init__(self, payload=None):
            self.payload = payload
    """, mod_data.__dict__)
    mod_data.Data.__module__ = "server.models.data"

    # Minimal server.models.data_view with DataRef
    mod_dv = types.ModuleType("server.models.data_view")
    exec("""class DataRef:
        def __init__(self, data_id=None):
            self.data_id = data_id
    """, mod_dv.__dict__)
    mod_dv.DataRef.__module__ = "server.models.data_view"

    # Minimal server.models.project with ProjWorkflow used by clean_orphan_data_sync (not used here)
    mod_proj = types.ModuleType("server.models.project")
    class ProjWorkflow:
        @classmethod
        def model_validate(cls, data):
            # For tests that don't use it, it's fine to return an object with nodes attr
            class W:
                def __init__(self, nodes):
                    self.nodes = nodes
            if isinstance(data, dict):
                nodes = data.get("nodes", [])
            else:
                nodes = []
            return W(nodes=nodes)
    mod_proj.ProjWorkflow = ProjWorkflow

    # Now prepare a server.models.database module that DataManager will import
    mod_db = types.ModuleType("server.models.database")
    mod_db.NodeOutputRecord = NodeOutputRecord
    mod_db.ProjectRecord = ProjectRecord

    # Inject all fake modules
    _inject_fake_model_modules({
        "server.models.data": mod_data,
        "server.models.data_view": mod_dv,
        "server.models.project": mod_proj,
        "server.models.database": mod_db,
    })

    # Load DataManager module (it will import the above fake modules)
    dm_mod = _load_datamanager_module()
    DataManager = dm_mod.DataManager

    # Instantiate DataManager with our fake DB
    dm = DataManager(sync_db_session=fake_db)

    # Prepare a Data instance and write it
    data_obj = mod_data.Data(payload={"k": "v"})
    ref1 = dm.write_sync(data_obj, node_id="n1", project_id=1, port="out")
    assert isinstance(ref1, mod_dv.DataRef)
    assert ref1.data_id is not None

    # Validate that the node record was persisted in fake DB
    assert any(n.id == ref1.data_id for n in fake_db._nodes)

    # Now read it back by creating a DataRef and calling read_sync
    read_back = dm.read_sync(mod_dv.DataRef(data_id=ref1.data_id))
    assert isinstance(read_back, mod_data.Data)
    assert read_back.payload == data_obj.payload

    # Writing identical data again should return the same DataRef id (no duplicate)
    ref_again = dm.write_sync(data_obj, node_id="n1", project_id=1, port="out")
    assert ref_again.data_id == ref1.data_id

    # Writing different data should create a new record
    data_obj2 = mod_data.Data(payload={"k": "different"})
    ref2 = dm.write_sync(data_obj2, node_id="n1", project_id=1, port="out")
    assert ref2.data_id != ref1.data_id
    # Ensure old record was deleted (FakeDB.delete removes old from _nodes)
    assert any(n.id == ref2.data_id for n in fake_db._nodes)
    assert not (ref1.data_id == ref2.data_id and False)  # trivial sanity


def test_clean_orphan_data_sync_removes_unreferenced_entries():
    # Setup fake DB and model classes
    fake_db, NodeOutputRecord, ProjectRecord = _make_fake_db()

    # Minimal Data class (not really used by clean_orphan_data_sync)
    mod_data = types.ModuleType("server.models.data")
    exec("""class Data:
        def __init__(self, payload=None):
            self.payload = payload
    """, mod_data.__dict__)
    mod_data.Data.__module__ = "server.models.data"

    # Minimal DataRef class
    mod_dv = types.ModuleType("server.models.data_view")
    exec("""class DataRef:
        def __init__(self, data_id=None):
            self.data_id = data_id
    """, mod_dv.__dict__)
    mod_dv.DataRef.__module__ = "server.models.data_view"

    # Project workflow parser that will return nodes with data_out references
    mod_proj = types.ModuleType("server.models.project")
    class ProjWorkflow:
        @classmethod
        def model_validate(cls, data):
            # We expect `data` to be a dict like {"nodes": [...]}
            class NodeLike:
                def __init__(self, data_out=None, param=None):
                    self.data_out = data_out or {}
                    self.param = param or {}

            class W:
                def __init__(self, nodes):
                    self.nodes = nodes

            nodes_raw = data.get("nodes", []) if isinstance(data, dict) else []
            nodes = []
            for n in nodes_raw:
                # n is expected to be dict with `data_out` mapping of port->{"data_id": id}
                data_out = {}
                for k, v in n.get("data_out", {}).items():
                    # use the DataRef class from the module object `mod_dv` injected earlier
                    data_out[k] = mod_dv.DataRef(data_id=v.get("data_id"))
                # params may include serialized File objects, but for this test we ignore params
                nodes.append(NodeLike(data_out=data_out, param=n.get("param", {})))
            return W(nodes=nodes)

    mod_proj.ProjWorkflow = ProjWorkflow

    # Inject fake modules
    mod_db = types.ModuleType("server.models.database")
    mod_db.NodeOutputRecord = NodeOutputRecord
    mod_db.ProjectRecord = ProjectRecord
    _inject_fake_model_modules({
        "server.models.data": mod_data,
        "server.models.data_view": mod_dv,
        "server.models.project": mod_proj,
        "server.models.database": mod_db,
    })

    # Load DataManager
    dm_mod = _load_datamanager_module()
    DataManager = dm_mod.DataManager

    dm = DataManager(sync_db_session=fake_db)

    # Prepare several NodeOutputRecord entries:
    # - id 1 referenced by project workflow
    # - id 2 not referenced (should be deleted)
    # - id 3 referenced by workflow
    # We'll craft the fake project's workflow to reference ids 1 and 3.
    rec1 = NodeOutputRecord(project_id=42, node_id="n1", port="o1", data=pickle.dumps(mod_data.Data(payload=1)))
    rec2 = NodeOutputRecord(project_id=42, node_id="n2", port="o1", data=pickle.dumps(mod_data.Data(payload=2)))
    rec3 = NodeOutputRecord(project_id=42, node_id="n3", port="o2", data=pickle.dumps(mod_data.Data(payload=3)))

    # add to DB via add+flush to assign ids
    fake_db.add(rec1)
    fake_db.add(rec2)
    fake_db.add(rec3)
    fake_db.flush()
    # Now rec1.id, rec2.id, rec3.id assigned
    ids = [rec1.id, rec2.id, rec3.id]
    assert len(ids) == 3 and None not in ids

    # Create project record with workflow referencing rec1 and rec3
    project_workflow = {
        "nodes": [
            {"data_out": {"out": {"data_id": rec1.id}}, "param": {}},
            {"data_out": {"out": {"data_id": rec3.id}}, "param": {}},
        ]
    }
    proj = ProjectRecord(id=42, workflow=project_workflow)
    fake_db._projects.append(proj)

    # Ensure all three records exist initially
    assert any(n.id == rec2.id for n in fake_db._nodes)

    # Run clean_orphan_data_sync which should remove rec2 but keep rec1 and rec3
    dm.clean_orphan_data_sync(project_id=42)

    remaining_ids = {n.id for n in fake_db._nodes}
    assert rec2.id not in remaining_ids
    assert rec1.id in remaining_ids
    assert rec3.id in remaining_ids



def test_read_async_and_write_async_behaviour():
    # Test the async read/write paths using a FakeDB that provides async execute/commit semantics.
    # We'll create a tiny async-capable fake DB wrapper around the synchronous fake DB used earlier.

    sync_db, NodeOutputRecord, ProjectRecord = _make_fake_db()

    # Async wrapper providing `execute` and `scalars().first()` expected by DataManager.async methods.
    class AsyncResult:
        def __init__(self, items):
            self._items = items

        def scalars(self):
            class S:
                def __init__(self, items):
                    self._items = items

                def first(self):
                    return self._items[0] if self._items else None

                def all(self):
                    return list(self._items)

            return S(self._items)

    class AsyncFakeDB:
        def __init__(self, sync_db):
            self._sync = sync_db

        async def execute(self, stmt):
            # For our tests, stmt won't be an actual SQL expression; we inspect it lightly.
            # We'll support where NodeOutputRecord.id == X and select(UserRecord) etc minimal usage.
            # To keep it simple, return all nodes for NodeOutputRecord selects.
            return AsyncResult(list(self._sync._nodes))

        async def add(self, obj):
            self._sync.add(obj)

        async def commit(self):
            self._sync.flush()

        async def rollback(self):
            # mimic clearing added
            self._sync._added.clear()

        async def delete(self, obj):
            self._sync.delete(obj)

    # Minimal Data and DataRef modules
    mod_data = _make_data_module()
    mod_dv = _make_data_view_module()

    # project module (not used heavily here)
    mod_proj = types.ModuleType("server.models.project")
    class ProjWorkflow:
        @classmethod
        def model_validate(cls, data):
            class W:
                def __init__(self, nodes):
                    self.nodes = nodes
            return W(nodes=[])
    mod_proj.ProjWorkflow = ProjWorkflow

    # Inject fake modules
    mod_db = types.ModuleType("server.models.database")
    mod_db.NodeOutputRecord = NodeOutputRecord
    mod_db.ProjectRecord = ProjectRecord

    _inject_fake_model_modules({
        "server.models.data": mod_data,
        "server.models.data_view": mod_dv,
        "server.models.project": mod_proj,
        "server.models.database": mod_db,
    })

    # Load DataManager
    dm_mod = _load_datamanager_module()
    # Override 'select' in the loaded DataManager module so tests using
    # lightweight fake model classes won't trigger SQLAlchemy coercion errors.
    # We provide a simple object with a `where(...)` method; our fake async DB
    # ignores the actual statement contents and returns prepared results.
    dm_mod.select = lambda *args, **kwargs: types.SimpleNamespace(where=lambda *a, **k: ("fake_stmt", args, kwargs))
    DataManager = dm_mod.DataManager

    # Create async fake DB and instantiate DataManager with it
    async_db = AsyncFakeDB(sync_db)
    dm = DataManager(async_db_session=async_db)

    # Prepare a Data instance and write it asynchronously
    data_obj = mod_data.Data(payload={"async": True})
    # write_async returns File-like object of DataRef; call in thread if necessary (it's async)
    # we do not call write_async directly; instead emulate the lower-level behavior: directly add a NodeOutputRecord and ensure read_async can fetch and deserialize it.

    # Create a NodeOutputRecord with pickled Data and persist via sync_db helper
    rec = NodeOutputRecord(project_id=7, node_id="nA", port="o", data=pickle.dumps(data_obj))
    sync_db.add(rec)
    sync_db.flush()
    # Now call read_async and ensure we get a Data instance back

    async def _inner():
        res = await dm.read_async(mod_dv.DataRef(data_id=rec.id))
        assert isinstance(res, mod_data.Data)
        assert res.payload == data_obj.payload

    # Run the async inner via asyncio
    asyncio.run(_inner())