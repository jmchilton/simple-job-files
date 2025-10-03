from os import environ, makedirs
from os.path import (
    dirname,
    exists,
    getsize,
)
from urllib.parse import unquote, urljoin

# Too big a dependency for just this...
from galaxy.util import in_directory
from webob import (
    exc,
    Request,
    Response,
)

BUFFER_SIZE = 4096
JOB_FILES_ROOT_DIRECTORY = environ.get("JOB_FILES_ROOT_DIRECTORY", None)


class JobFilesApp:

    def __init__(self, root_directory=JOB_FILES_ROOT_DIRECTORY, allow_multiple_downloads=False):
        self.root_directory = root_directory
        self.served_files = []
        self.allow_multiple_downloads = allow_multiple_downloads

    def __call__(self, environ, start_response):
        req = Request(environ)
        params = req.params.mixed()
        method = req.method
        if method == "POST":
            resp = self._post(req, params)
        elif method == "PUT":
            resp = self._put(req, params)
        elif method == "GET":
            resp = self._get(req, params)
        elif method == "HEAD":
            resp = self._head(req, params)
        else:
            raise Exception("Unhandled request method %s" % method)
        return resp(environ, start_response)

    def _post(self, request, params):
        path = unquote(params['path'])
        if not in_directory(path, self.root_directory):
            raise AssertionError("{} not in {}".format(path, self.root_directory))
        parent_directory = dirname(path)
        if not exists(parent_directory):
            makedirs(parent_directory)
        _copy_to_path(params["file"].file, path)
        return Response(body='')

    def _get(self, request, params):
        path = unquote(params['path'])
        if path in self.served_files and not self.allow_multiple_downloads:  # emulate Galaxy not allowing the same request twice...
            raise Exception("Same file copied multiple times...")
        if not in_directory(path, self.root_directory):
            raise AssertionError("{} not in {}".format(path, self.root_directory))
        self.served_files.append(path)
        return _file_response(path)

    def _put(self, request, params):
        path = unquote(params['path'])
        if not in_directory(path, self.root_directory):
            raise AssertionError("{} not in {}".format(path, self.root_directory))
        parent_directory = dirname(path)
        if not exists(parent_directory):
            makedirs(parent_directory)
        _copy_to_path(request.body_file, path)
        return Response(status=201, headers={'Location': urljoin(request.path_url, path)

    def _head(self, request, params):
        path = unquote(params['path'])
        if path in self.served_files and not self.allow_multiple_downloads:
            # emulate Galaxy not allowing the same request twice...
            raise Exception("Same file copied multiple times...")
        if not in_directory(path, self.root_directory):
            raise AssertionError("{} not in {}".format(path, self.root_directory))
        return _file_header(path)


def _copy_to_path(object, path):
    """
    Copy file-like object to path.
    """
    output = open(path, 'wb')
    _copy_and_close(object, output)


def _copy_and_close(object, output):
    try:
        while True:
            buffer = object.read(BUFFER_SIZE)
            if not buffer:
                break
            output.write(buffer)
    finally:
        output.close()


def _file_response(path):
    resp = Response()
    if exists(path):
        resp.app_iter = _FileIterator(path)
    else:
        raise exc.HTTPNotFound("No file found with path %s." % path)
    return resp


def _file_header(path):
    resp = Response()
    if exists(path):
        resp.content_length = getsize(path)
    else:
        raise exc.HTTPNotFound("No file found with path %s." % path)
    return resp


class _FileIterator:

    def __init__(self, path):
        self.input = open(path, 'rb')

    def __iter__(self):
        return self

    def __next__(self):
        buffer = self.input.read(1024)
        if buffer == b"":
            raise StopIteration
        return buffer
