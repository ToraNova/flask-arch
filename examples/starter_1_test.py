import pytest
import os
import re
import tempfile
import shutil

# hacky way to use a different upload_dir when testing
tmpd = tempfile.mkdtemp()
os.environ['UPLOAD_DIR'] = tmpd

from werkzeug.datastructures import FileStorage
from starter_1 import create_app

@pytest.fixture()
def app():
    db_fd, db_file = tempfile.mkstemp()
    db_uri = 'sqlite:///%s' % db_file
    app = create_app({
        'TESTING': True,
        'DBURI': db_uri,
    })
    yield app
    os.close(db_fd)
    os.unlink(db_file)

@pytest.fixture()
def client(app):
    return app.test_client()

def parse_csrf(resp):
    mt = re.search(b'"csrf_token" value="(\\S+)"', resp.data)
    assert mt
    csrf = mt.group(1).decode()
    return csrf

def login(client, email, passw):
    resp = client.get('/auth/login')
    csrf = parse_csrf(resp)

    resp = client.post('/auth/login', data={'email':email, 'password':passw, 'csrf_token':csrf}, follow_redirects=True)
    assert resp.status_code == 200

def logout(client):
    resp = client.get('/auth/logout', follow_redirects=True)
    assert resp.status_code == 200

#TODO: allow multi-testing by fixing 'is already defined for this MetaData instance'
def test_all(client):
    login(client, 'admin@test.d', 'hunter2')

    # test obtain profile picture
    resp = client.get('/auth/profile')
    mt = re.search(b'src="/auth/file\\?filename=(\\S+\\.png)"', resp.data)
    assert mt
    profimg_name = mt.group(1).decode()
    resp = client.get(f'/auth/file?filename={profimg_name}')
    assert resp.status_code == 200

    test_file = FileStorage(stream=open('doomer.jpg', "rb"),)
    resp = client.get('/update_avatar')
    csrf = parse_csrf(resp)
    resp = client.post('/update_avatar', data={'profile_img':test_file, 'csrf_token':csrf}, content_type='multipart/form-data', follow_redirects=True)
    assert b'invalid file size' in resp.data

    resp = client.get(f'/auth/file?filename={profimg_name}')
    assert resp.status_code == 200

    test_file = FileStorage(stream=open('wojak.jpg', "rb"),)
    resp = client.get('/update_avatar')
    csrf = parse_csrf(resp)
    resp = client.post('/update_avatar', data={'profile_img':test_file, 'csrf_token':csrf}, content_type='multipart/form-data', follow_redirects=True)
    assert resp.status_code == 200
    csrf = parse_csrf(resp)

    resp = client.post('/crop_avatar', data={'x': 0, 'y': 0, 'w': 150, 'h': 150, 'csrf_token':csrf}, follow_redirects=True)
    mt = re.search(b'src="/auth/file\\?filename=(\\S+\\.png)"', resp.data)
    assert mt
    new_profimg_name = mt.group(1).decode()
    assert new_profimg_name != profimg_name

    resp = client.get(f'/auth/file?filename={profimg_name}')
    assert resp.status_code == 404
    assert b'Not Found' in resp.data

    resp = client.get(f'/auth/file?filename={new_profimg_name}')
    assert resp.status_code == 200

    resp = client.get('/role/list')
    assert b'&#34;project.view&#34;: 1' in resp.data

    resp = client.get('/role/insert')
    csrf = parse_csrf(resp)

    resp = client.post('/role/insert', data={'name':'NEW_ROLE_TEST', 'privileges':'{"NEW_ROLE_PRIV": 1}', 'csrf_token':csrf}, follow_redirects=True)
    assert b'NEW_ROLE_TEST' in resp.data and b'NEW_ROLE_PRIV' in resp.data

    assert resp.status_code == 200

    resp = client.get('/role/update')
    assert resp.status_code == 400

    resp = client.get('/role/delete')
    assert resp.status_code == 400

    resp = client.get('/project/list')
    assert resp.status_code == 200

    resp = client.get('/role/update?id=1')
    csrf = parse_csrf(resp)

    resp = client.post('/role/update?id=1', data={'privileges':'{"user.view": 1, "user.add": 1, "user.mod": 1, "user.del": 1, "role.view": 1, "role.insert": 1, "role.update": 1, "role.delete": 1, "project.view": 0, "project.insert": 1, "project.update": 1, "project.delete": 1}', 'csrf_token': csrf}, follow_redirects=True)
    assert resp.status_code == 200

    resp = client.get('/role/update?id=2')
    csrf = parse_csrf(resp)
    resp = client.post('/role/update?id=2', data={'privileges':'{}', 'csrf_token': csrf}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'&#34;project.view&#34;' not in resp.data
    csrf = parse_csrf(resp)

    resp = client.get('/role/update?id=2')
    csrf = parse_csrf(resp)
    resp = client.post('/role/update?id=2', data={'privileges':'{"project.view":1, "project.insert":1, "project.update":1}', 'csrf_token': csrf}, follow_redirects=True)
    assert resp.status_code == 200

    resp = client.get('/project/list')
    assert resp.status_code == 403

    resp = client.post('/role/delete?id=3', data={'csrf_token': csrf}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'NEW_ROLE_TEST' not in resp.data and b'NEW_ROLE_PRIV' not in resp.data

    resp = client.post('/role/update?id=1', data={'privileges':'{"user.view": 1, "user.add": 1, "user.mod": 1, "user.del": 1, "role.view": 1, "role.insert": 1, "role.update": 1, "role.delete": 1, "project.view": 1, "project.insert": 1, "project.update": 1, "project.delete": 1}', 'csrf_token': csrf}, follow_redirects=True)
    assert resp.status_code == 200

    resp = client.get('/project/list')
    assert resp.status_code == 200

    # MULTI-FILE UPLOAD
    resp = client.get('/project/insert')
    csrf = parse_csrf(resp)

    invalid_file = FileStorage(stream=open('dev_run.sh', "rb"),)
    resp = client.post('/project/insert', data={'name':'UPLOAD_TEST', 'csrf_token': csrf, 'project_files':[invalid_file]}, content_type='multipart/form-data', follow_redirects=True)
    assert resp.status_code == 400
    assert b'invalid file name' in resp.data

    invalid_file = FileStorage(stream=open('dev_run.sh', "rb"),)

    resp = client.get('/project/insert')
    csrf = parse_csrf(resp)

    test_file = FileStorage(stream=open('doomer.jpg', "rb"),)
    resp = client.post('/project/insert', data={'name':'UPLOAD_TEST', 'csrf_token': csrf, 'project_files':[test_file]}, content_type='multipart/form-data', follow_redirects=True)
    assert b'UPLOAD_TEST' in resp.data
    assert b'<td>new</td>' in resp.data

    resp = client.get('/project/view?id=1')
    mt = re.search(b'\\.jpg">(\\S+\\.jpg)</a>', resp.data)
    assert mt
    filename = mt.group(1).decode()

    resp = client.get(f'/project/file?id=1&filename={filename}')
    assert resp.status_code == 200

    resp = client.get('/project/update?id=1')
    csrf = parse_csrf(resp)

    test_file = FileStorage(stream=open('wojak.jpg', "rb"),)
    resp = client.post('/project/update?id=1', data={'project_files':[test_file], 'status':'updated', 'csrf_token':csrf}, follow_redirects=True, content_type='multipart/form-data')
    assert resp.status_code == 200
    assert b'status: updated' in resp.data
    mt = re.findall(b'\\.jpg">(\\S+\\.jpg)</a>', resp.data)
    assert len(mt) == 2

    resp = client.get('/project/update?id=1')
    csrf = parse_csrf(resp)

    resp = client.post('/project/update?id=1', data={filename:'delete_file', 'status':'updated', 'csrf_token':csrf}, follow_redirects=True, content_type='multipart/form-data')
    assert resp.status_code == 200
    mt = re.findall(b'\\.jpg">(\\S+\\.jpg)</a>', resp.data)
    assert len(mt) == 1
    assert filename not in mt
    left_over = mt[0]

    logout(client)

    login(client, 'user@test.d', 'asdasd')

    resp = client.get('/role/list')
    assert resp.status_code == 403
    assert b'403 Forbidden' in resp.data

    resp = client.get('/user/list')
    assert resp.status_code == 403
    assert b'403 Forbidden' in resp.data

    resp = client.get('/project/list')
    assert resp.status_code == 200

    resp = client.get('/project/view?id=1', follow_redirects=True)
    assert b'cannot view, no ownership' in resp.data

    resp = client.get('/project/insert')
    csrf = parse_csrf(resp)

    test_file = FileStorage(stream=open('doomer.jpg', "rb"),)
    resp = client.post('/project/insert', data={'name':'NEW_TEST', 'csrf_token': csrf, 'project_files':[test_file]}, content_type='multipart/form-data', follow_redirects=True)
    assert b'NEW_TEST' in resp.data
    assert b'UPLOAD_TEST' in resp.data

    resp = client.get('/project/view?id=2')
    mt = re.search(b'\\.jpg">(\\S+\\.jpg)</a>', resp.data)
    assert mt

    resp = client.get('/project/update?id=2')
    assert resp.status_code == 200
    csrf = parse_csrf(resp)

    resp = client.get('/project/update?id=1', follow_redirects=True)
    assert resp.status_code == 400

    resp = client.post('/project/update?id=1', data={left_over:'delete', 'csrf_token':csrf}, content_type='multipart/form-data', follow_redirects=True)
    assert resp.status_code == 400
    assert b'cannot modify, no ownership'

    resp = client.get('/project/delete?id=2')
    assert b'403 Forbidden' in resp.data

    resp = client.get('/project/delete?id=1', follow_redirects=True)
    assert b'403 Forbidden' in resp.data

    resp = client.post('/project/delete?id=1', data={'csrf_token':csrf}, follow_redirects=True)
    assert resp.status_code == 403
    assert b'cannot delete, no ownership'

    logout(client)

    # dont with testing, remove temporary upload directory
    shutil.rmtree(tmpd)
