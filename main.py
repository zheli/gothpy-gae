import webapp2

class IndexPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Hello, World!')

app = webapp2.WSGIApplication(
        [('/', IndexPage)],
        debug = True)
