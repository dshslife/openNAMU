from .tool.func import *

def login_oauth_2(platform = None, func = None):
    publish_url = load_oauth('publish_url')
    oauth_data = load_oauth(platform)
    api_url = {}
    data = {
        'client_id' : oauth_data['client_id'],
        'client_secret' : oauth_data['client_secret'],
        'redirect_uri' : publish_url + '/oauth/' + platform + '/callback',
        'state' : 'RAMDOMVALUE'
    }

    if platform == 'google':
        api_url['redirect'] = 'https://google/oauth2.0/authorize' # TODO: change to google url
        api_url['token'] = 'https://google/oauth2.0/token' # TODO: change to google url
        api_url['profile'] = 'https://google/v1/nid/me' # TODO: change to google url

    if func == 'init':
        if oauth_data['client_id'] == '' or oauth_data['client_secret'] == '':
            return easy_minify(flask.render_template(skin_check(), imp = [load_lang('login'), wiki_set(), custom(), other2([0, 0])], data = load_lang('oauth_disabled'), menu = [['user', load_lang('user')]]))
        elif publish_url == 'https://':
            return easy_minify(flask.render_template(skin_check(), imp = [load_lang('login'), wiki_set(), custom(), other2([0, 0])], data = load_lang('oauth_settings_not_found'), menu = [['user', load_lang('user')]]))

        referrer_re = re.compile(r'(?P<host>^(https?):\/\/([^\/]+))\/(?P<refer>[^\/?]+)')
        if flask.request.referrer != None:
            referrer = referrer_re.search(flask.request.referrer)
            if referrer.group('host') != load_oauth('publish_url'):
                return redirect('/')
            else:
                flask.session['referrer'] = referrer.group('refer')
        else:
            return redirect('/')
        flask.session['refer'] = flask.request.referrer

        if platform == 'google':
            return redirect(api_url['redirect']+'?response_type=code&client_id={}&redirect_uri={}&state={}'.format(data['client_id'], data['redirect_uri'], data['state'])) # TODO: change to google path and params

    elif func == 'callback':
        code = flask.request.args.get('code')
        state = flask.request.args.get('state')
        if code == None or state == None:
            return easy_minify(flask.render_template(skin_check(), imp = [load_lang('inter_error'), wiki_set(), custom(), other2([0, 0])], data = 
            '''<p>''' + load_lang('inter_error_detail') + '''</p>
            <hr>
            <code>ie_wrong_callback</code>
            <p>''' + load_lang('ie_wrong_callback') + '''</p>
            '''
            , menu = [['user', load_lang('user')]]))

        if platform == 'google': # TODO: change to google format
            token_access = api_url['token']+'?grant_type=authorization_code&client_id={}&client_secret={}&code={}&state={}'.format(data['client_id'], data['client_secret'], code, state) 
            token_result = urllib.request.urlopen(token_access).read().decode('utf-8')
            token_result_json = json.loads(token_result)

            headers = {'Authorization': 'Bearer {}'.format(token_result_json['access_token'])}
            profile_access = urllib.request.Request(api_url['profile'], headers = headers)
            profile_result = urllib.request.urlopen(profile_access).read().decode('utf-8')
            profile_result_json = json.loads(profile_result)

            stand_json = {'id' : profile_result_json['response']['id'], 'name' : profile_result_json['response']['name'], 'picture' : profile_result_json['response']['profile_image']}

        if flask.session['referrer'][0:6] == 'change':
            curs.execute('select * from oauth_conn where wiki_id = ? and provider = ?', [flask.session['id'], platform])
            oauth_result = curs.fetchall()
            if len(oauth_result) == 0:
                curs.execute('insert into oauth_conn (provider, wiki_id, sns_id, name, picture) values(?, ?, ?, ?, ?)', [platform, flask.session['id'], stand_json['id'], stand_json['name'], stand_json['picture']])
            else:
                curs.execute('update oauth_conn set name = ? picture = ? where wiki_id = ?', [stand_json['name'], stand_json['pricture'], flask.session['id']])
            conn.commit()
        elif flask.session['referrer'][0:5] == 'login':
            curs.execute('select * from oauth_conn where provider = ? and sns_id = ?', [platform, stand_json['id']])
            curs_result = curs.fetchall()
            if len(curs_result) == 0:
                return re_error('/error/2')
            else:
                flask.session['state'] = 1
                flask.session['id'] = curs_result[0][2]
        return redirect(flask.session['refer'])