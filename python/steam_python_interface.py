#!/usr/bin/python3.4
import requests


#URL Declarations
#Base URL's
host = "steamcommunity.com"
common_logon = "https://" + host + "/login/";
url_mainsite = "http://" + host + "/"
url_mainsite_secure = "https://" + host + "/"

#Security and Logon
url_ref = common_logon + "home/?goto=market%2F";
url_get_rsa = common_logon + "getrsakey/"
url_do_login = common_logon + "dologin/"
url_do_logout = common_logon + "logout/"
url_market = common_logon + "market/"

#Buy and Sell
url_buy_listing = url_mainsite_secure + "market/buylisting/"
url_search = _market + "search/render/?query={0}&start={1}&count={2}";

#Captcha
url_get_captcha = "https://" + _host + "/public/captcha.php?gid=";
url_refresh_captcha = "https://" + _host + "/actions/RefreshCaptcha/?count=1";
