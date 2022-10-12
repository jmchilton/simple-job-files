import io
from contextlib import contextmanager
from pathlib import Path

import requests
from webtest.http import StopableWSGIServer

from simplejobfiles.app import JobFilesApp


def exercise_server(application_url, target_path: Path):
    test_file = target_path / "test_file"
    output_test = target_path / "output_test"

    test_file.write_text("moo cow")
    assert not output_test.exists()

    url = application_url
    response = requests.get(url, dict(path=str(test_file)))
    response.raise_for_status()
    assert response.text == "moo cow"
    files = {'file': io.BytesIO(b"moo dog")}
    requests.post(url, data=dict(path=str(output_test)), files=files)
    assert output_test.read_text() == "moo dog"


def test_app(tmp_path: Path):
    app = JobFilesApp(tmp_path, allow_multiple_downloads=False)
    with server_for_test_app(app) as server:
        url = server.application_url
        exercise_server(url, tmp_path)


@contextmanager
def server_for_test_app(app, **kwd):
    server = StopableWSGIServer.create(app, **kwd)
    try:
        server.wait()
        yield server
    finally:
        server.shutdown()