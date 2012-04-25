import webapp2
import cgi
import string
import re

form = """
<form method = "post">
    What is your birthday?
    <label>Month <input type="text" name="month" value=%(month)s> </label>
    <label>Day <input type="text" name="day" value=%(day)s> </label>
    <label>Year <input type="text" name="year" value=%(year)s> </label>
    <div style="color:red">%(error)s</div>
    <br>
    <br>
    <input type="submit">
</form>
"""
rot_form = """
<form method="post">
    <textarea name="text" style="height: 100px; width: 200px;">%(placeholder)s</textarea>
    <input type="submit">
</form>
"""

header = """
<!DOCTYPE HTML>
<html>
<head>
    <title>Sign Up</title>
    <link type="text/css" rel="stylesheet" href="/stylesheets/bootstrap.css" />
    <style>
        body { margin-top: 60px }
    </style>
</head>
<body>
    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="i-bar"></span>
            <span class="i-bar"></span>
            <span class="i-bar"></span>
          </a>
          <a class="brand" href="#">Udacity-CS253</a>
          <div class="nav-collapse">
            <ul class="nav">
              <li class="active"><a href="#">Signup</a></li>
              <li><a href="#about">About</a></li>
              <li><a href="#contact">Contact</a></li>
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>

    <div class="container">
"""

footer = """
    </div>
</body>
</html>
"""

signup_form = """
<form method="post">
    <label>Username
        <input type="text" name="username" value=%(user_username)s>
    </label>
    <label>Password
        <input type="password" name="password" value=%(user_password)s>
    </label>
    <label>Verify Password
        <input type="password" name="verify" value=%(user_verify)s>
    </label>
    <label>Email(Optional)
        <input type="text" name="email" value=%(user_email)s>
    </label>
    <div class="actions">
        <button type="submit" class="btn primary">Signup!</button>
    </div>
</form>
"""

def valid_month(month):
      months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                'August', 'September', 'October', 'November', 'December']
      if month.capitalize() in months:
          return month.capitalize()
      else:
          return None

def valid_day(day):
    if day and day.isdigit():
        if int(day) < 1 or int(day) > 31:
            return None
        else:
            return int(day)

def valid_year(year):
    if year and year.isdigit():
        if int(year) < 1900 or int(year) > 2020:
            return None
        else:
            return int(year)

class MainPage(webapp2.RequestHandler):

  def write_form(self, error="", month="", day="", year=""):
    self.response.out.write(form % {"error" : error, 
                                    "month" : month, 
                                    "day" : day, 
                                    "year" : year })

  def get(self):
    self.write_form()

  def post(self):
    user_month = self.request.get('month')
    user_day = self.request.get('day')
    user_year = self.request.get('year')

    month = valid_month(user_month)
    day = valid_day(user_day)
    year = valid_year(user_year)

    if not(day and month and year):
      self.write_form(error="Invalid data! Please re-enter",
                      day = cgi.escape(user_day, quote=True), 
                      month = cgi.escape(user_month, quote=True),
                      year = cgi.escape(user_year, quote=True))
    else:
      self.redirect("/thanks")

class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Thanks! Thats valid")

class RotHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<h1>Rot13</h1>")
        self.response.out.write(rot_form % {"placeholder" : ""})

    def post(self):
        user_string = self.request.get("text")
        converted_string = self.rot13(user_string) 
        self.response.out.write(rot_form % {"placeholder" : converted_string})

    def rot13(self, s):
        alphabets = string.ascii_lowercase
        i = 0
        output = []
        caps = False
        while i < len(s):
            if s[i].isupper():
                caps = True
                s_index = alphabets.find(s[i].lower())
            else:
                s_index = alphabets.find(s[i])
            if s_index >= 0:
                if s_index + 13 >= 26:
                    if caps:
                        output.append((alphabets[(s_index+13)%26]).upper())
                    else:
                        output.append(alphabets[(s_index+13)%26])
                else:
                    if caps:
                        output.append((alphabets[s_index+13]).upper())
                    else:
                        output.append(alphabets[s_index+13])
            else:
                output.append(s[i])
            caps = False
            i = i + 1
        return "".join(output)

class SignupHandler(webapp2.RequestHandler):

    def valid_username(self, username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        if USER_RE.match(username):
            return True
        else:
            return False

    def valid_password(self, password, verify):
        if password != verify:
            return False
        PASS_RE = re.compile(r"^.{3,20}$")
        if PASS_RE.match(password):
            return True
        else:
            return False

    def valid_email(self, email):
        if email == "":
            return True
        EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
        if EMAIL_RE.match(email):
            return True
        else:
            return False

    def write_form(self, username="", password="", verify="", email=""):
        self.response.out.write(signup_form % {"user_username" : "", 
                                               "user_password" : "",
                                               "user_verify" : "",
                                               "user_email" : ""})
    def get(self):
        self.response.out.write(header)
        self.write_form()
        self.response.out.write(footer)

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')
        
        check_username = self.valid_username(user_username)
        check_password = self.valid_password(user_verify, user_password)
        check_email = self.valid_email(user_email)

        if not(check_username and check_password and check_email):
            # self.write_form(error="Invalid data! Please re-enter",
            #               day = cgi.escape(user_day, quote=True), 
            #               month = cgi.escape(user_month, quote=True),
            #               year = cgi.escape(user_year, quote=True))
            self.response.out.write(header)
            self.write_form()
            self.response.out.write(footer)
            # self.response.out.write("invalid!")
        else:
            self.redirect("/unit2/welcome?username=" + user_username)


class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        username = self.request.get("username")
        self.response.out.write("<h1>Welcome, " + username + "</h1>")

app = webapp2.WSGIApplication([('/', MainPage), 
                               ('/thanks', ThanksHandler),
                               ('/unit2/rot13', RotHandler),
                               ('/unit2/signup', SignupHandler),
                               ('/unit2/welcome', WelcomeHandler)], debug=True)


