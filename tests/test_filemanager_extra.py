import sys
from pathlib import Path
import importlib.util
import types

import pytest

# Ensure project root is on sys.path so `import server` works during pytest collection
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _load_filemanager_module():
    fm_path = _PROJECT_ROOT / "server" / "lib" / "FileManager.py"
    spec = importlib.util.spec_from_file_location("real_server_lib_FileManager", str(fm_path))
    fm_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fm_mod)  # type: ignore
    return fm_mod


def test_write_sync_insufficient_storage(fake_env):
    """
    If a user has insufficient storage quota, write_sync should raise InsufficientStorageError.
    """
    FakeDB = fake_env["FakeDB"]
    DBModule = fake_env["DBModule"]

    # Prepare fake DB with a user with very small quota and a project
    db = FakeDB()
    db._users.append(DBModule.UserRecord(1, username="alice", file_total_space=10))  # 10 bytes
    db._projects.append(DBModule.ProjectRecord(10, name="proj10", owner_id=1))

    # Load FileManager (it will use the fake minio from fake_env)
    fm_mod = _load_filemanager_module()
    FileManager = fm_mod.FileManager

    fm = FileManager(sync_db_session=db)

    content = b"this content is longer than 10 bytes"
    # InsufficientStorageError is defined in server.models.exception and imported by FileManager
    from server.models.exception import InsufficientStorageError

    with pytest.raises(InsufficientStorageError):
        fm.write_sync(
            filename="big.txt",
            content=content,
            format="txt",
            node_id="n1",
            project_id=10,
            user_id=1,
        )


def test_write_sync_minio_put_error(fake_env, monkeypatch):
    """
    If the MinIO client raises its S3Error during upload, FileManager.write_sync should convert it to IOError.
    """
    FakeDB = fake_env["FakeDB"]
    DBModule = fake_env["DBModule"]
    MinioModule = __import__("minio")  # fake_env injected minio module

    # Prepare fake DB with normal user and project
    db = FakeDB()
    db._users.append(DBModule.UserRecord(2, username="bob", file_total_space=10 ** 6))
    db._projects.append(DBModule.ProjectRecord(20, name="proj20", owner_id=2))

    # Load FileManager module
    fm_mod = _load_filemanager_module()
    FileManager = fm_mod.FileManager

    fm = FileManager(sync_db_session=db)

    # Patch the minio client's put_object to raise S3Error
    def raise_s3error(*args, **kwargs):
        raise MinioModule.S3Error("Simulated minio failure", code="InternalError")

    monkeypatch.setattr(fm.minio_client, "put_object", raise_s3error, raising=False)

    with pytest.raises(IOError):
        fm.write_sync(
            filename="fail.txt",
            content=b"hello",
            format="txt",
            node_id="n1",
            project_id=20,
            user_id=2,
        )


def test_delete_sync_permission_denied(fake_env):
    """
    Deleting a file that belongs to another user should raise PermissionError.
    """
    FakeDB = fake_env["FakeDB"]
    DBModule = fake_env["DBModule"]

    db = FakeDB()
    # user 10 exists
    db._users.append(DBModule.UserRecord(10, username="owner", file_total_space=10 ** 6))
    db._users.append(DBModule.UserRecord(11, username="attacker", file_total_space=10 ** 6))
    # project
    db._projects.append(DBModule.ProjectRecord(100, name="proj100", owner_id=10))

    # create a file record that belongs to user 10
    fr = DBModule.FileRecord(
        file_key="key-xyz",
        filename="secret.txt",
        format="txt",
        user_id=10,
        project_id=100,
        node_id="nX",
        file_size=5,
    )
    db._files.append(fr)

    fm_mod = _load_filemanager_module()
    FileManager = fm_mod.FileManager
    fm = FileManager(sync_db_session=db)

    # Use the real pydantic File model to pass into delete_sync
    from server.models.file import File as ModelFile

    with pytest.raises(PermissionError):
        fm.delete_sync(
            ModelFile(key="key-xyz", filename="secret.txt", format="txt", size=5),
            user_id=11,
        )


def test_cleanup_soft_deleted_files_task(fake_env, monkeypatch):
    """
    The cleanup task should permanently delete files that are soft-deleted in DB.
    We monkeypatch the database session provider to return our prepared FakeDB instance.
    """
    FakeDB = fake_env["FakeDB"]
    DBModule = fake_env["DBModule"]
    minio_mod = __import__("minio")

    # Prepare a FakeDB instance with a soft-deleted file
    db = FakeDB()
    # Add a user and project so FileManager instantiation and logging work
    db._users.append(DBModule.UserRecord(50, username="owner50", file_total_space=10 ** 6))
    db._projects.append(DBModule.ProjectRecord(500, name="proj500", owner_id=50))

    # Add a file record marked as deleted
    file_rec = DBModule.FileRecord(
        file_key="to_delete",
        filename="old.txt",
        format="txt",
        user_id=50,
        project_id=500,
        node_id="n_del",
        file_size=10,
    )
    # mark as soft-deleted
    file_rec.is_deleted = True
    db._files.append(file_rec)

    # Ensure the fake DB module's get_session yields our db
    db_mod = fake_env["DBModule"]
    monkeypatch.setattr(db_mod, "get_session", lambda: iter([db]), raising=False)

    # Provide a close() on the fake DB so the task's finally block can call it.
    monkeypatch.setattr(db, "close", lambda: None, raising=False)

    # The cleanup task composes expressions like
    #   FileRecord.is_deleted.is_(True) | (FileRecord.project_id.is_(None))
    # so the `is_()` result must support `|`. Our lightweight Col returns callables,
    # which don't support `|`. Provide a small helper that wraps a predicate and
    # implements __or__ to allow combining filters.
    class Filterable:
        def __init__(self, fn):
            self.fn = fn

        def __call__(self, obj):
            return self.fn(obj)

        def __or__(self, other):
            if isinstance(other, Filterable):
                return Filterable(lambda obj: self.fn(obj) or other.fn(obj))
            elif callable(other):
                return Filterable(lambda obj: self.fn(obj) or other(obj))
            else:
                return Filterable(lambda obj: self.fn(obj) or bool(other))

    class ColLike:
        def __init__(self, name):
            self.name = name

        def is_(self, val):
            return Filterable(lambda obj: getattr(obj, self.name) == val)

        def isnot(self, val):
            return Filterable(lambda obj: getattr(obj, self.name) is not val)

    # Monkeypatch FileRecord column descriptors on the fake DB module so the
    # boolean composition in the cleanup task works with our FakeDB records.
    monkeypatch.setattr(db_mod.FileRecord, "is_deleted", ColLike("is_deleted"), raising=False)
    monkeypatch.setattr(db_mod.FileRecord, "project_id", ColLike("project_id"), raising=False)

    # Replace the Minio implementation so that remove_object behaves (no exception)
    class SharedMinio:
        def __init__(self, *args, **kwargs):
            # a shared in-memory store (not used for this test)
            self.store = {}

        def bucket_exists(self, bucket):
            return True

        def make_bucket(self, bucket):
            pass

        def remove_object(self, bucket_name, object_name):
            # simulate successful removal
            if object_name not in self.store:
                # simulate NoSuchKey behavior by raising S3Error with that code,
                # the cleanup task treats NoSuchKey specially (still deletes DB record).
                raise minio_mod.S3Error("NoSuchKey", code="NoSuchKey")

        # Other methods not needed for this test
        def put_object(self, *a, **k):
            pass

        def get_object(self, *a, **k):
            pass

        def stat_object(self, *a, **k):
            pass

    # Monkeypatch the minio.Minio constructor used by FileManager to our SharedMinio
    monkeypatch.setattr(minio_mod, "Minio", SharedMinio, raising=False)

    # Load FileManager module and invoke the cleanup task function body.
    fm_mod = _load_filemanager_module()

    # The cleanup task was decorated by celery; try to call the original function if exposed,
    # otherwise call .run() if available.
    task_obj = getattr(fm_mod, "cleanup_soft_deleted_files_task")

    # Execute the underlying function
    if hasattr(task_obj, "__wrapped__"):
        # If it's a decorated Celery task, __wrapped__ should be the original function
        task_obj.__wrapped__()  # type: ignore
    elif hasattr(task_obj, "run"):
        task_obj.run()  # type: ignore
    else:
        # fallback: call whatever it is (some environments might not wrap)
        task_obj()

    # After running cleanup, the fake DB should have had its deleted file removed
    # FakeDB.delete removes file records matching file_key
    assert not any(f.file_key == "to_delete" for f in db._files)