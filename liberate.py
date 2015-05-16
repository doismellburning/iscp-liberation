import lxml.html
import os
import pprint
import requests


username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]

LOGIN_URL = "https://www.iscp.ac.uk/Default.aspx"

def sign_in(u, p):

    raw = requests.get(LOGIN_URL)

    session_id = raw.cookies["ASP.NET_SessionId"]


    html = lxml.html.fromstring(raw.text)

    viewstate = html.cssselect("input#__VIEWSTATE")[0].value
    viewstate_generator = html.cssselect("input#__VIEWSTATEGENERATOR")[0].value

    payload = {
        "ctl00$cphMain$Logon1$_resolution" : "1440x900",
        "ctl00$cphMain$Logon1$_email" : u,
        "ctl00$cphMain$Logon1$_password": p,
        "ctl00$cphMain$Logon1$_login": "Log in",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstate_generator,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    cookies = {
        "ASP.NET_SessionId": session_id,
    }

    session = requests.session()
    r = session.post(LOGIN_URL, data=payload, headers=headers, cookies=cookies)

    assert "unread messages" in r.content

    return session, cookies

def get_courses(session, cookies):
    r = session.get("https://www.iscp.ac.uk/evidence/courselist.aspx", cookies=cookies)

    html = lxml.html.fromstring(r.text)

    def extract_course(xlink):
        y = xlink.findall('div')
        if len(y) > 2:
            return y[2].text
        else:
            return None

    return [extract_course(e) for e in html.cssselect(".xlink")]

s,c = sign_in(username, password)

pprint.pprint(get_courses(s, c))
