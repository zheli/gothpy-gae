import webapp2
import os
import jinja2

ROOT_PATH = os.path.dirname(__file__)
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.join(ROOT_PATH, 'templates')))

class IndexPage(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class PostMsg(webapp2.RequestHandler):
    def post(self):
        template_values = { 'message' : self.request.get('message')}
        template = jinja_environment.get_template('showmessage.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication(
        [
            ('/', IndexPage),
            ('/post', PostMsg)
        ],
        debug = True)
