import webapp2
import cgi

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

app = webapp2.WSGIApplication([('/', MainPage), ('/thanks', ThanksHandler)], debug=True)


