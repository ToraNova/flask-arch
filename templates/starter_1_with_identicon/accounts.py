import os
import uuid
import datetime
from PIL import Image
from werkzeug.utils import secure_filename
from flask import redirect, url_for, current_app, request, render_template, flash
from flask_login import current_user, login_required
from .utils import resize_image, crop_image

def init_app(app, userm):

    @app.route('/crop_avatar', methods=['GET', 'POST'])
    @login_required
    def crop_avatar():
        if request.method == 'POST':
            try:
                uid = current_user.get_id()
                u = userm.select_user(uid)
                raw_path = u.get_file_path(u.avatar_raw)
                cropped_img = crop_image(raw_path, request.form.copy())

                tda = [u.avatar_raw]

                size_tuple = (30, 60, 150)
                sznm_tuple = ('s', 'm', 'l')

                for sznm, size in zip(sznm_tuple, size_tuple):
                    ts_now = int(datetime.datetime.now().timestamp())
                    store_name = secure_filename(f'{uuid.uuid4()}-{ts_now}_{sznm}.png')
                    path = os.path.join(u.get_store_dir(), store_name)

                    resized_img = resize_image(cropped_img, size)
                    resized_img.save(path)

                    tda.append(getattr(u, f'avatar_{sznm}'))
                    setattr(u, f'avatar_{sznm}', store_name)

                userm.update(u)
                userm.commit()

                try:
                    for tdf in tda:
                        u.remove_file(tdf)
                except Exception:
                    pass

                return redirect(url_for('auth.profile'))
            except Exception as e:
                userm.rollback()
                raise e

        return render_template('crop.html', img_url=url_for('auth.file', filename=current_user.avatar_raw))
