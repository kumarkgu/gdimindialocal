from sharepoint import SharePointSite
import requests
import urllib.request as ur
import time
from urllib.request import Request, urlopen

from requests_ntlm import HttpNtlmAuth

# def test_using_sharepoint(pwuser, pwpass, pwurl):
#     # https://jll2.sharepoint.com/sites/16062/Lists/Accounts/AllItems.aspx
#     print("Before Opener")
#     # opener = basic_auth_opener(server_url, pwuser, pwpass)
#     opener = basic_auth_opener(pwurl, pwuser, pwpass)
#     print("Opener Done")
#     site = SharePointSite(pwurl, opener=opener)
#     print("Site Opened")
#     for sp_list in site.lists:
#         print ("Id: {}, Title: {}, Name: {}.".format(sp_list.id,
#                                                      sp_list.meta['Title']))


def test_using_sharepoint2(pwuser, pwpass, pwurl):
    print("Before Opener")
    opener = ur.build_opener()
    # opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    response = opener.open(pwurl)
    time.sleep(10)
    print('READ CONTENTS:', response.read())
    print('URL          :', response.geturl())
    print("Opener Done")
    site = SharePointSite(pwurl, opener=opener)
    print("Site Opened")
    for sp_list in site.lists:
        print ("Id: {}, Title: {}, Name: {}.".format(sp_list.id,
                                                     sp_list.meta['Title']))


def test_using_requests(pwuser, pwpass, pwurl):
    # response = requests.get(pwurl + pwsite, auth=HttpNtlmAuth(pwuser, pwpass))
    # vheaders = {
    #     'User-Agent': 'Mozilla/5.0',
    #     'accept': 'application/json;odata=verbose'
    # }
    vheaders = {
        'accept': 'application/json;odata=verbose'
    }
    response = requests.get(pwurl, headers=vheaders)
    print (response.status_code)
    print (response.json())


# def test_using_urllib_request(pwurl):
#     req = Request(pwurl, headers={'User-Agent': 'Mozilla/5.0'})
#     print(req)

vuser = 'AP\Gunjan.Kumar'
vpass = 'Abc$e141176#'
# vurl = 'https://jll2.sharepoint.com/sites/16062/Lists/Accounts/AllItems.aspx'
# vurl = 'https://jll2.sharepoint.com/sites/16062/Lists/Accounts/'
vurl = 'https://jll2.sharepoint.com/sites/16062/'
# _api/web/lists
# https://jll2.sharepoint.com/sites/16062/SitePages/Home.aspx
# test_using_requests(vuser, vpass, vurl)
# test_using_sharepoint(vuser, vpass, vurl)
test_using_sharepoint2(vuser, vpass, vurl)
# test_using_urllib_request(vurl)
