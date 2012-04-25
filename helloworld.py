import webapp2
import cgi
import string

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

class GreetingHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("fuck you chiga!")


app = webapp2.WSGIApplication([('/', MainPage), ('/thanks', ThanksHandler),
                               ('/unit2/rot13', RotHandler),
                               ('/fuck', GreetingHandler)], debug=True)


