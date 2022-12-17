from flask import Flask, request, make_response, render_template, redirect, session, url_for
from functools import wraps
from linkedinauth import login_to_linkedin
import requests
import pickle
import json

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
if __name__ == '__main__':
    app.run(debug=True)

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        with open('users.json') as users:
            users = json.load(users)
        auth = request.authorization
        if auth and auth.username in users.keys() and users[auth.username] == auth.password:
            return f(*args, **kwargs)
        return make_response('Credentials Error', 401, {'WWW-Authenticate' : 'Basic realm="Login Required'})
    return decorated

@app.route('/')
@auth_required
def login():
    '''
    function to authenticate access to api service, redirects to linked in login page upon success.
    '''
    return redirect("/linkedinlogin")

@app.route('/linkedinlogin')
@auth_required
def linkedinlogin():
    '''
    renders linked in login page
    '''
    form_data = request.form
    return render_template('signin.html', form=form_data)

@app.route('/signin', methods=['POST'])
@auth_required
def signin():
    '''
    function to call selenium func to login to linkedin and get cookie data, redirects to get data page upon success and to this login page upon failure
    '''
    login_response = login_to_linkedin(request.form['username'],request.form['password'])
    if login_response == "Success":
        session['username'] = request.form['username']
        form_data = request.form

        return render_template('get_data.html', form=form_data)
    elif login_response == "Login Error":
        return redirect("/linkedinlogin")

@app.route('/getdata', methods=['POST'])
@auth_required
def getdata():
    '''
    decides which details to fetch based on button clicked, personal details or connection details.
    '''
    if request.form['submit_button'] == 'Personal':
        return redirect("/get_personal_data")
    elif request.form['submit_button'] == 'Connections':
        page = 1
        return redirect(url_for("get_connection_data", page = page))
    else:
        pass

@app.route('/get_personal_data')
@auth_required
def get_personal_data():
    cookie_string, csrf_token = get_cookie()
    userdata = {}
    email = "https://www.linkedin.com/voyager/api/voyagerContactsDashSupportedEmail?decorationId=com.linkedin.voyager.dash.deco.contacts.SupportedEmail-1"
    payload={}
    headers_new = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
        'Accept': 'application/vnd.linkedin.normalized+json+2.1',
        'csrf-token': csrf_token,
        'Cookie': cookie_string  
    }
    response = requests.request("GET", email, headers=headers_new, data=payload)
    userdata['email'] = json.loads(response.text)['data']['emailAddress']

    # user_id = "neeraj-vk-001066132"
    # place = f"https://www.linkedin.com/voyager/api/identity/dash/profiles?decorationId=com.linkedin.voyager.dash.deco.identity.profile.WebTopCardCore-10&memberIdentity={user_id}&q=memberIdentity"
    # response = requests.request("GET", place, headers=headers_new, data=payload)
    # userdata['place'] = json.loads(response.text)

    return render_template('user_data.html', data=userdata)


@app.route('/get_connection_data', methods=['GET', 'POST'])
@auth_required
def get_connection_data():
    cookie_string, csrf_token = get_cookie()
    if "pageno" in request.form:
        page = request.form['pageno']
    else:
        page = request.args['page']

    pageno = ((int(page) - 1) * 10)
    url = f"https://www.linkedin.com/voyager/api/relationships/dash/connections?decorationId=com.linkedin.voyager.dash.deco.web.mynetwork.ConnectionList-15&count=10&q=search&sortType=FIRSTNAME_LASTNAME&start={pageno}"
    payload={}
    headers_new = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
        'Accept': 'application/vnd.linkedin.normalized+json+2.1',
        'csrf-token': csrf_token,
        'Cookie': cookie_string  
    }
    response = requests.request("GET", url, headers=headers_new, data=payload)
    response_obj = json.loads(response.text)['included']
    user_data = []
    for user in response_obj:
        if "firstName" in user:
            user = {
                "firstName" : user.get("firstName"),
                "lastName" : user.get("lastName"),
                "headline" : user.get("headline"),
                "publicIdentifier" : user.get("publicIdentifier"),
                "memorialized" : user.get("memorialized")
            }
            user_data.append(user)
    
    return render_template('connection_data.html', data=user_data)

def get_cookie():
    '''
    returns cookies and csrf token for auth
    '''
    username = session.get("username")
    cookie_name = f"{username}.pkl"
    cookies = pickle.load(open(cookie_name, "rb"))
    bcookie = next((cookie for cookie in cookies if cookie['name'] == 'bcookie'), None)
    bcookie_val = bcookie['value']
    bscookie = next((cookie for cookie in cookies if cookie['name'] == 'bscookie'), None)
    bscookie_val = bscookie['value']
    jsession = next((cookie for cookie in cookies if cookie['name'] == 'JSESSIONID'), None)
    jsession_val = jsession['value']
    li_at = next((cookie for cookie in cookies if cookie['name'] == 'li_at'), None)
    li_at_val = li_at['value']
    cookie_string = f'bcookie={bcookie_val}; bscookie={bscookie_val}; JSESSIONID={jsession_val}; li_at={li_at_val};'
    csrf_token = jsession_val.strip('"')
    return cookie_string, csrf_token
