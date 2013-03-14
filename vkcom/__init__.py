# -*- coding:utf-8 -*-
__author__ = 'eri'
import httplib
import urllib
import simplejson


class APIError(Exception):
    """
    1	Unknown error occurred.
    2	Application is disabled. Enable your application or use test mode.
    4	Incorrect signature.
    5	User authorization failed.
    6	Too many requests per second.
    7	Permission to perform this action is denied by user.
    """
    def __init__(self, response):
        self.response = response
        self.response['error_code'] = int(self.response['error_code'])

    def __str__(self):
        return self.response['error_msg']

    def __getitem__(self, item):
        return self.response[item]


class AuthError(Exception):
    def __init__(self, response):
        self.response = response
    def __str__(self):
        desc=self.response.split("error_description=")[-1].split("&")[0]
        return urllib.unquote(desc)


class OAuth(object):
    def __init__(self, master, client_id, scope):
        self.master = master
        self.client_id = client_id
        self.scope = scope

        self.parameters = {
            'client_id': self.client_id,
            'scope': self.scope,
            'redirect_uri': "http://oauth.vk.com/blank.html",
            'display': 'page',
            'response_type': "token"
        }


    def extract(self, uri):
        self.master.access_token = uri.split("access_token=")[-1].split("&")[0]
        self.master.user_id = uri.split("user_id=")[-1].split("&")[0]
        self.master.expires_in = uri.split("expires_in=")[-1].split("&")[0]

        return (self.master.access_token, self.master.user_id, self.master.expires_in)


    def webkitgtk(self, display='page'):
        self.parameters['display'] = display
        parameters = urllib.urlencode(self.parameters)
        login_uri = 'https://api.vk.com/oauth/authorize?' + parameters

        import gtk
        import webkit
        import gobject

        gobject.threads_init()
        win = gtk.Dialog()
        bro = webkit.WebView()

        bro.open(login_uri)
        win.set_title("Авторизация VK")
        win.set_default_size(300, 300)
        win.vbox.pack_start(bro)
        win.show_all()

        def resource_cb(view, frame, resource, request, response):
        #        global scope,access_token, client_id ,user_id ,expires_in

            uri = request.get_uri()
            print uri
            if uri.find('access_denied') > 1:
                if not win.emit("delete-event", gtk.gdk.Event(gtk.gdk.DELETE)):
                    win.destroy()
                raise AuthError(uri)

            if uri.find('access_token') > 1:
                self.extract(uri)
                if not win.emit("delete-event", gtk.gdk.Event(gtk.gdk.DELETE)):
                    win.destroy()


        bro.connect('resource-request-starting', resource_cb)
        win.run()
        win.destroy()
        # win.connect('destroy', gtk.main_quit)

        # gtk.main()


class API(object):
    def __init__(self, app_id, scope=None):
        self.access_token = None
        self.expires_in = None
        self.client_id = app_id
        self.user_id = 0
        self.scope = None
        self.Auth = OAuth(master=self, client_id=app_id, scope=scope or 0)


    def __call__(self, method_name, **kwargs):
        """
        https://api.vkontakte.ru/method/METHOD_NAME?PARAMETERS&access_token=ACCESS_TOKEN
        """
        parameters = dict(kwargs)
        parameters['access_token'] = self.access_token

        for k in kwargs:
            if kwargs[k] is None:
                parameters.pop(k)

        parameters = urllib.urlencode(parameters)
        conn = httplib.HTTPSConnection("api.vkontakte.ru")
        conn.request("GET", "/method/" + method_name + "?" + parameters)
        response = conn.getresponse()
        data = response.read()
        data = simplejson.loads(data)
        conn.close()

        if 'error' in data.keys():
            raise APIError(data['error'])

        return data.get('response')



