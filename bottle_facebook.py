#
# Basic layout for the plugin was borrowed from bottle-mongodb-plugin
#  see: https://github.com/fdouetteau/bottle-mongodb-plugin
#
# Released into the public domain.  Do with this as you please
#
# Copyright 2012
#
# Authors:
#   Adam Edelman
#   Shaun Patterson
# 
#

from bottle import PluginError, request
from keys import *
import facebook
import inspect
import urllib

#
# Sample usage:
#
# fbPlugin = FacebookAuth("appId", "appSecret") 
#
#  or with optional callback
# 
# fbPlugin = FacebookAuth(keys.appId, keys.appSecret, redirectToUrl)
#
# where redirectToUrl is a function taking in 1 parameter request
#  def redirectToUrl(request):
#    parsedUrl = request.urlparts
#    redirect('/login' + '?redirect=%s' % (parsedUrl.path))
# 
# This will redirect users to your login page if they are not logged
#  in via Facebook
#

    

class FacebookAuth(object):

    def getUser(self):
        ''' Grab 'user' object from Graph API '''
        user = facebook.get_user_from_cookie(request.cookies, self.appId, self.appSecret)
        if not user:
            raise

        graphApi = facebook.GraphAPI(user['access_token']).get_object("me")

        # I don't see the user id any where in the Graph object.  So adding it in here
        graphApi['avatar'] = facebook.GraphAPI(user['access_token']).get_object("me", fields='picture')['picture']
        graphApi['uid'] = user['uid']
        return graphApi

    def __init__(self, appId, appSecret, callback=None,  keyword='fbuser'):
        self.appId = appId
        self.appSecret = appSecret
        self.callback = callback
        self.keyword = keyword

    def setup(self, app):
        ''' Make sure we don't step on anything/ourselves '''
        for apps in app.plugins:
            if not isinstance(app, FacebookAuth):
                continue
            if other.keyword == self.keyword:
                raise PluginError("Plugin keyword already exsists")

    def apply(self, callback, context):
        print context['callback']

        args = inspect.getargspec(context['callback'])[0]
        if self.keyword not in args:
            return callback

        def wrapper(*a, **ka):
            if self.keyword in args:
                try:
                    ka[self.keyword] = self.getUser()
                except:
                    ka[self.keyword] = None
                    if self.callback != None:
                        self.callback(request)

            rv = callback(*a, **ka)

            return rv

        return wrapper
