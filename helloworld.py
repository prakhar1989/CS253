import sys
import os
import webapp2
import jinja2
import hashlib
import hmac
import random
import string

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

#imports for custom defined helpers
import valid_helpers
import auth_helpers

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class User(db.Model):
    username = db.StringProperty(required = True)
    email = db.StringProperty()
    encrypted_pass = db.StringProperty(required = True)

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
            self.write("Thanks")

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

        # Try to retrieve user from database if it already exits
        query = User.all(keys_only = True).filter('username', user_username)
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
        if not have_error:
            # query database only if no other errors exist
            existing_user = query.get()
            if existing_user:
                # if the user exists, the give error
                params['error_username'] = "This user already exists"
                have_error = True
        if have_error:
            self.render("signup_form.html", **params)
        else:
            #set cookies here and save user to database
            #encrypt the pass before saving
            encrypted_pass = auth_helpers.make_pw_hash(user_username, user_password)
            user = User(username = user_username, email = user_email, encrypted_pass = encrypted_pass)
            user.put() # save the user
            existing_user = query.get() # get the user from the database
            user_id = existing_user.id()
            user_hash = auth_helpers.make_secure_val(str(user_id))
            self.response.headers.add_header("Set-Cookie", "user = %s" % str(user_hash))
            self.redirect("/unit3/welcome")

class WelcomeHandler(Handler):
    def get(self):
        user_cookie_hash = self.request.cookies.get("user")
        if user_cookie_hash:
            user_identified = auth_helpers.check_secure_val(user_cookie_hash)
            if user_identified:
                user = User.get_by_id(int(user_identified))
                self.write("<h2>Welcome, %s" % user.username) 
            else:
                self.redirect("/signup")
        else:
            self.redirect("/signup")


class LoginHandler(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        params = dict(username = user_username)
        query = User.all().filter('username', user_username)
        user = query.get()
        if user:
            check_user = auth_helpers.valid_pw(user_username, user_password, user.encrypted_pass)
            if check_user:
                #set cookie and redirect to welcome page
                user_id = user.key().id()
                user_hash = auth_helpers.make_secure_val(str(user_id))
                self.response.headers.add_header("Set-Cookie", "user = %s" % str(user_hash))
                self.redirect("/unit3/welcome")
            else:
                params["error_username"] = "Invalid login"
                params["error_password"] = " "
                self.render("login.html", **params)
        else:
            params["error_username"] = "Invalid login"
            params["error_password"] = " "
            self.render("login.html", **params)

class LogoutHandler(Handler):
    def get(self):
        user_cookie_hash = self.request.cookies.get("user")
        if user_cookie_hash:
            # deleting the cookie by setting it to nothing
            self.response.headers.add_header('Set-Cookie', 'user=; Path=/')
            self.redirect("/signup")
        else:
            self.redirect("/signup")

app = webapp2.WSGIApplication([('/', MainPage), 
                               ('/unit2/rot13', RotHandler),
                               ('/signup', SignupHandler),
                               ('/login', LoginHandler),
                               ('/logout', LogoutHandler),
                               ('/unit3/welcome', WelcomeHandler)], debug=True)
