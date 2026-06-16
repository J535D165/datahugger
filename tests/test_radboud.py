"""Offline unit tests for the Radboud Data Repository service.

The repository requires either anonymous access to large "Open access"
collections or HTTP Basic credentials for restricted ones, so it cannot be
exercised live in CI. These tests mock the HTTP session instead and cover the
URL routing, MANIFEST.txt listing, version (``_vN``) resolution and the auth
plumbing added to the base downloader.
"""

import pytest
import requests

import datahugger
from datahugger.resolvers import _resolve_service
from datahugger.services import RadboudDataRepositoryDataset

LANDING = "https://data.ru.nl/collections/di/dccn/COLL"
DIRECT = "https://public.data.ru.nl/dccn/COLL_v1/"

PROPFIND_XML = b"""<?xml version="1.0" encoding="utf-8"?>
<a:multistatus xmlns:a="DAV:">
  <a:response><a:href>/dccn/</a:href></a:response>
  <a:response><a:href>/dccn/COLL_v1/</a:href></a:response>
  <a:response><a:href>/dccn/COLL_v2/</a:href></a:response>
  <a:response><a:href>/dccn/OTHER_v1/</a:href></a:response>
</a:multistatus>
"""

MANIFEST = "aaa11 LICENSE.txt\nbbb22 sub/dir/data.csv\n\nccc33 name with spaces.txt\n"


class FakeResponse:
    def __init__(self, *, text=None, content=None, json_data=None, status=200):
        self.text = text
        self.content = content
        self._json = json_data
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code), response=self)

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json


class FakeSession:
    """Stand-in for ``requests.Session`` with scripted ``get``/``request``."""

    def __init__(self, get=None, request=None):
        self._get = get
        self._request = request
        self.auth = None

    def get(self, url, *args, **kwargs):
        return self._get(url, *args, **kwargs)

    def request(self, method, url, *args, **kwargs):
        return self._request(method, url, *args, **kwargs)


@pytest.fixture(autouse=True)
def _clear_creds(monkeypatch):
    monkeypatch.delenv("RDR_USERNAME", raising=False)
    monkeypatch.delenv("RDR_PASSWORD", raising=False)


@pytest.mark.parametrize(
    "url",
    [
        "https://data.ru.nl/collections/di/dccn/DSC_3011020.09_236",
        "https://data.donders.ru.nl/collections/di/dccn/DSC_3011020.09_236",
        "https://public.data.ru.nl/dccn/DSC_3010000.11_518_v1/",
        "https://webdav.data.donders.ru.nl/dccn/DSC_3010000.11_518_v1/",
    ],
)
def test_routing(url):
    assert _resolve_service(url) is RadboudDataRepositoryDataset


def test_files_from_manifest():
    svc = datahugger.info(DIRECT)
    svc._session = FakeSession(get=lambda url, *a, **k: FakeResponse(text=MANIFEST))

    files = svc.files
    assert [f["name"] for f in files] == [
        "LICENSE.txt",
        "sub/dir/data.csv",
        "name with spaces.txt",
    ]
    first = files[0]
    assert first["hash"] == "aaa11"
    assert first["hash_type"] == "sha256"
    assert first["size"] is None
    assert first["link"] == "https://public.data.ru.nl/dccn/COLL_v1/LICENSE.txt"
    # paths with spaces are percent-encoded in the link but not the name
    assert files[2]["link"].endswith("/name%20with%20spaces.txt")


def test_collection_url_direct_keeps_version():
    svc = datahugger.info(DIRECT)
    assert svc._collection_url() == "https://public.data.ru.nl/dccn/COLL_v1"


def test_version_resolution_via_propfind():
    svc = datahugger.info(LANDING)

    def fake_request(method, url, *a, **k):
        assert method == "PROPFIND"
        assert url == "https://public.data.ru.nl/dccn/"
        return FakeResponse(content=PROPFIND_XML)

    svc._session = FakeSession(request=fake_request)
    # highest _vN among collections sharing the COLL prefix
    assert svc._collection_url() == "https://public.data.ru.nl/dccn/COLL_v2"


def test_version_explicit_param_short_circuits():
    svc = datahugger.info(LANDING, params={"version": "3"})
    # no session interaction needed when the version is given explicitly
    assert svc._collection_url() == "https://public.data.ru.nl/dccn/COLL_v3"


def test_auth_precedence(monkeypatch):
    anon = datahugger.info(DIRECT)
    assert anon._auth() is None
    assert anon._base_host == RadboudDataRepositoryDataset.PUBLIC_BASE

    monkeypatch.setenv("RDR_USERNAME", "envuser")
    monkeypatch.setenv("RDR_PASSWORD", "envpass")
    from_env = datahugger.info(DIRECT)
    assert from_env._auth() == ("envuser", "envpass")
    assert from_env._base_host == RadboudDataRepositoryDataset.WEBDAV_BASE

    # explicit params override the environment
    from_param = datahugger.info(DIRECT, params={"username": "u", "password": "p"})
    assert from_param._auth() == ("u", "p")


def test_session_carries_auth():
    authed = datahugger.info(DIRECT, params={"username": "u", "password": "p"})
    assert authed.session.auth == ("u", "p")

    anon = datahugger.info(DIRECT)
    assert anon.session.auth is None


def test_download_translates_401_to_credentials_error(tmp_path):
    svc = datahugger.info(DIRECT)
    svc._session = FakeSession(get=lambda url, *a, **k: FakeResponse(status=401))
    with pytest.raises(PermissionError, match="credentials"):
        svc.download_file(
            "https://public.data.ru.nl/dccn/COLL_v1/secret.dat",
            str(tmp_path),
            "secret.dat",
        )


def test_existing_service_session_is_anonymous():
    """Regression guard for the base-class session/auth change."""
    from datahugger.services import ZenodoDataset

    svc = datahugger.info("https://zenodo.org/record/6614829")
    assert isinstance(svc, ZenodoDataset)
    assert svc.session.auth is None
