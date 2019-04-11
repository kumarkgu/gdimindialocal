import sharepy
import os
from base.utils import base_util as bu
from base.utils import fileobjects as fo
from base.utils.Logger import Logger


class SharePoint:
    def __init__(self, **kwargs):
        self.session = None
        self.sessfile = kwargs.get(
            "sessionfile",
            "C:/Users/{0}/Documents/temp/{1}.txt".format(
                bu.current_user(),
                os.getpid()
            )
        )
        self.sessdir = self._set_sessionfiledir(self.sessfile)
        self.log = kwargs.get("log", Logger("Sharepoint").getlog())

    @staticmethod
    def _set_sessionfiledir(filename):
        t_dir = os.path.basename(filename)
        fo.make_base_dir(filename=filename)
        return t_dir

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def _authenticate(self, url, username=None, password=None):
        self.session = sharepy.connect(site=url, username=username,
                                       password=password)

    def disconnect(self):
        if self.session is not None:
            self.log.info("Disconnecting From Sharepoint Online")
            self.session = None

    def connect(self, url, **kwargs):
        t_user = kwargs.get("username", None)
        t_pass = kwargs.get("password", None)
        self._authenticate(url=url, username=t_user, password=t_pass)
        return self.session


# from office365.sharepoint.client_context import ClientContext
# from office365.runtime.auth.authentication_context import
# AuthenticationContext
# from office365.runtime.client_request import ClientRequest
# from office365.runtime.utilities.request_options import RequestOptions
# import json


# def authenticate(url, username, password):
#     ctx_auth = AuthenticationContext(url=url)
#     if ctx_auth.acquire_token_for_user(username=username, password=password):
#         request = ClientRequest(ctx_auth)
#         options = RequestOptions("{0}/_api/web".format(url))
#         headers = {
#             "Accept": "application/json",
#             "Content-Type": "application/json"
#         }
#         options.headers = headers
#         data = request.execute_query_direct(options)
#         s = json.loads(data.content)
#         web_title = s['Title']
#         print("Web Title: {}".format(web_title))
#     else:
#         print(ctx_auth.get_last_error())


# def clientauthenticate(url, usrname, passwd):
#     ctx_auth = AuthenticationContext(url=url)
#     if ctx_auth.acquire_token_for_user(username=usrname, password=passwd):
#         ctx = ClientContext(url=url, auth_context=ctx_auth)
#         web = ctx.web
#         ctx.load(web)
#         ctx.execute_query()
#         print("Web title: {0}".format(web.properties['Title']))
#     else:
#         print(ctx_auth.get_last_error())


# def main_prog():
#     url = "https://jll2.sharepoint.com/sites/16062/"
# #    clientauthenticate(url, 'gunjan.kumar', 'Efghi141176#')
#     # authenticate(url, 'gunjan.kumar', 'Efghi141176#')


# main_prog()

