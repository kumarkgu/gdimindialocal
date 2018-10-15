from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
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



def main_prog():
    url = "https://jll2.sharepoint.com/sites/16062/"
#    clientauthenticate(url, 'gunjan.kumar', 'Efghi141176#')
    # authenticate(url, 'gunjan.kumar', 'Efghi141176#')


main_prog()

