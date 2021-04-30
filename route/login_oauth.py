from .tool.func import *

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def login_oauth_2(conn):
    curs = conn.cursor()

    ip = ip_check()
    if ip_or_user(ip) == 0:
        return redirect('/user')

    if ban_check(None, 'login') == 1:
        return re_error('/ban')

    if flask.request.method == 'GET':
        flow = InstalledAppFlow.from_client_secrets_file(
            '/config/client_secrets.json',
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'])

        flow.run_local_server()
        credentials = flow.credentials
        if not credentials:
            return re_error('/error/10')

        service = build('calendar', 'v3', credentials=credentials)

        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        flask.session['id'] = user_info['email']

        ua_plus(oauth_return_code, ip, user_agent, get_time())
        conn.commit()

        return redirect('/user')
