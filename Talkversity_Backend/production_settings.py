import dj_database_url
# 含入原本的settings.py所有設定
from .settings import *

DATABASES = {
    'default': dj_database_url.config(
        default='mysql://b29c884b1564b2:31ff28df@us-cdbr-east-03.cleardb.com/heroku_e5cef95f274af75?reconnect=true')
}


STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = 'staticfiles'  # 設定網站正式上線時靜態檔案目錄位置
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # 設定HTTP連線方式
ALLOWED_HOSTS = ['*']  # 讓所有的網域都能瀏覽本網站
DEBUG = True  # 關閉除錯模式
