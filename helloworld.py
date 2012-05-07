import sys
import os
import webapp2
import jinja2
import hashlib
import hmac
import random
import string

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

import valid_helpers

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):

  def get(self):
    self.render("form.html")

  def post(self):
    user_month = self.request.get('month')
    user_day = self.request.get('day')
    user_year = self.request.get('year')

    month = valid_helpers.valid_month(user_month)
    day = valid_helpers.valid_day(user_day)
    year = valid_helpers.valid_year(user_year)

    if not(day and month and year):
      self.render("form.html", error="Invalid data! Please re-enter",
                  day = user_day,
                  month = user_month,
                  year = user_year)
    else:
      self.write("Thats valid")

class RotHandler(Handler):
    def get(self):
        self.render("rot_form.html")

    def post(self):
        self.render("rot_form.html", 
                placeholder = self.rot13(self.request.get("text")) )

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
                if caps:
                    output.append((alphabets[(s_index+13)%26]).upper())
                else:
                    output.append(alphabets[(s_index+13)%26])
            else:
                output.append(s[i])
            caps = False
            i = i + 1
        return "".join(output)

class SignupHandler(Handler):
    def get(self):
        self.render("signup_form.html")

    def post(self):
        have_error = False
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')
        
        check_username = valid_helpers.valid_username(user_username)
        check_password = valid_helpers.valid_password(user_password)
        check_verify = valid_helpers.valid_verify(user_verify, user_password)
        check_email = valid_helpers.valid_email(user_email)

        params = dict(user_username = user_username, user_email = user_email)

        if not(check_username):
            params['error_username'] = "That's not a valid username."
            have_error = True
        if not(check_password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        if not(check_verify):
            params['error_verify'] = "Your passwords didn't match."
            have_error = True
        if not(check_email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render("signup_form.html", **params)
        else:
            self.redirect("/unit2/welcome?username=" + user_username)

class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<h2>Welcome, " + self.request.get("username") + "!</h2>")

app = webapp2.WSGIApplication([('/', MainPage), 
                               ('/unit2/rot13', RotHandler),
                               ('/unit2/signup', SignupHandler),
                               ('/unit2/welcome', WelcomeHandler)], debug=True)
