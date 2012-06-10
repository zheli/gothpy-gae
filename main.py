import webapp2
import os
import jinja2
import logging

from google.appengine.api import users, channel
from google.appengine.ext import db

from django.utils import simplejson as json

ROOT_PATH = os.path.dirname(__file__)
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.join(ROOT_PATH, 'templates')))
logging.getLogger().setLevel(logging.DEBUG)

class Channels(db.Model):
    channel_id  = db.StringProperty(default = "") 

class IndexPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            logging.debug("user (id: " + user.user_id() + ") has logged in.")
            channel_id = user.user_id()
            chat_token = channel.create_channel(channel_id)
            template_values = {
                    'nickname'  : user.nickname(),
                    'user_id'   : user.user_id(),
                    'channel_id': channel_id,
                    'chat_token': chat_token
                    }
            template = jinja_environment.get_template('index.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class PostMsg(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template_values = {}
            template = jinja_environment.get_template('post_message.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        user            = users.get_current_user()
        message         = '%s said %s </br>' % (user.nickname(), self.request.get('message'))
        all_channels    = Channels.all().fetch(1000)
        for c in all_channels:
            channel_msg = json.dumps({'success': True, 'html': message})
            logging.debug('sending message to:' + c.channel_id)
            channel.send_message(c.channel_id, channel_msg)

        template_values = {}
        template = jinja_environment.get_template('post_message.html')
        self.response.out.write(template.render(template_values))
            
class Disconnected(webapp2.RequestHandler):
    def post(self):
        client_id   = self.request.get('from')
        logging.debug('client_id:' + client_id + 'disconnected')
        channel_key = db.Key.from_path('Channels', client_id)
        current_channel = db.get(channel_key)
        if current_channel:
            db.delete(channel_key)

class Connected(webapp2.RequestHandler):
    def post(self):
        client_id   = self.request.get('from')
        logging.info('client_id:' + client_id + ' has connected')
        channel_key = db.Key.from_path('Channels', client_id)
        current_channel = db.get(channel_key)
        if not current_channel:
            current_channel = Channels(key_name = client_id, channel_id = client_id)
            current_channel.put()

class Logout(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))

app = webapp2.WSGIApplication(
        [
            ('/', IndexPage),
            ('/post/', PostMsg),
            ('/logout/', Logout),
            ('/_ah/channel/disconnected/', Disconnected),
            ('/_ah/channel/connected/', Connected)
        ],
        debug = True)
