import pytest
from arch_basic import create_app

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here

@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

# tests
def test_root(client):
    resp = client.get("/")
    assert b'myarch1/r1">route1' in resp.data
    assert b'myarch1/r2/0">route2' in resp.data
    assert b'myarch2/r1">route1' in resp.data
    assert b'myarch2/r2/1">route2' in resp.data

def test_get(client):
    resp = client.get("/myarch1/r1")
    assert b'MyArch1 - Route1' in resp.data

    resp = client.get("/myarch2/r1")
    assert b'MyArch2 - Route1' in resp.data

    a1r2 = client.get('/myarch1/r2/1')
    a2r2 = client.get('/myarch2/r2/1')
    assert a1r2.data == a2r2.data

    resp = client.get('/myarch1/r2/2')
    assert b'Route2 2' in resp.data

    resp = client.get('/myarch2/r2/101')
    assert b'Route2 101' in resp.data

    resp = client.get('/myarch1/missing-template')
    assert resp.status_code == 500
    assert b'template not found when rendering for missing: missing.html' in resp.data

    resp = client.get('/myarch2/reroute-test', follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'3' in resp.data

    resp = client.get('/reroute_to_arch', follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'MyArch1 - Route1' in resp.data

def test_post(client):
    resp = client.post('/myarch1/r2/1')
    assert resp.status_code == 402
    assert b'color:red">missing bar or password' in resp.data

    resp = client.post('/myarch1/r2/1', data={'bar':'a', 'password':'123'})
    assert resp.status_code == 401

    resp = client.post('/myarch1/r2/1337', data={'bar':'a', 'password':'myarch1'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'color:green">post successful' in resp.data
    assert b'Route2 1337' in resp.data

    resp = client.post('/myarch2/r2/1', data={'bar':'a', 'password':'321'})
    assert resp.status_code == 401

    resp = client.post('/myarch2/r2/1', data={'bar':'a', 'password':'myarch2'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'color:green">post successful' in resp.data
    assert b'Route2 1' in resp.data
    assert resp.request.path == '/myarch1/r2/1'
