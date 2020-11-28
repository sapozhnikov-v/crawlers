import datetime
import hashlib
import json
import random
import string

from instagram_web_api import Client, ClientError, ClientLoginError, ClientCompatPatch


class MyClient(Client):

    @staticmethod
    def _extract_rhx_gis(html):
        options = string.ascii_lowercase + string.digits
        text = ''.join([random.choice(options) for _ in range(8)])
        return hashlib.md5(text.encode()).hexdigest()

    def login(self):
        """Login to the web site."""
        if not self.username or not self.password:
            raise ClientError('username/password is blank')

        time = str(int(datetime.datetime.now().timestamp()))
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{time}:{self.password}"

        params = {'username': self.username, 'enc_password': enc_password, 'queryParams': '{}', 'optIntoOneTap': False}
        self._init_rollout_hash()
        login_res = self._make_request('https://www.instagram.com/accounts/login/ajax/', params=params)
        if not login_res.get('status', '') == 'ok' or not login_res.get('authenticated'):
            raise ClientLoginError('Unable to login')

        if self.on_login:
            on_login_callback = self.on_login
            on_login_callback(self)
        return login_res

    def user_feed(self, user_id, **kwargs):
        """
        Get user feed

        :param user_id:
        :param kwargs:
            - **count**: Number of items to return. Default: 12
            - **end_cursor**: For pagination. Taken from:

                .. code-block:: python

                    info.get('data', {}).get('user', {}).get(
                        'edge_owner_to_timeline_media', {}).get(
                        'page_info', {}).get('end_cursor')
            - **extract**: bool. Return a simple list of media
        :return:
        """
        count = kwargs.pop('count', 12)
        if count > 50:
            raise ValueError('count cannot be greater than 50')

        end_cursor = kwargs.pop('end_cursor', None) or kwargs.pop('max_id', None)

        variables = {
            'id': user_id,
            'first': int(count),
        }
        if end_cursor:
            variables['after'] = end_cursor
        query = {
            'query_hash': '56a7068fea504063273cc2120ffd54f3',
            'variables': json.dumps(variables, separators=(',', ':'))
        }
        info = self._make_request(self.GRAPHQL_API_URL, query=query)

        if not info.get('data', {}).get('user') or \
                not info.get('data', {}).get('user', {}).get('edge_owner_to_timeline_media', {}).get('count', 0):
            # non-existent accounts do not return media at all
            # private accounts return media with just a count, no nodes
            raise ClientError('Not Found', 404)

        if self.auto_patch:
            [ClientCompatPatch.media(media['node'], drop_incompat_keys=self.drop_incompat_keys)
             for media in info.get('data', {}).get('user', {}).get(
                'edge_owner_to_timeline_media', {}).get('edges', [])]

        if kwargs.pop('extract', True):
            return info.get('data', {}).get('user', {}).get(
                'edge_owner_to_timeline_media', {}).get('edges', [])
        return info
