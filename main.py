#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import webapp2
import cgi
import jinja2
import os
import logging
import time
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))


class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """
    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")
        
class Post(db.Model):
    title = db.StringProperty(required = True)
    body = db.StringProperty(required = True)
    bid = db.IntegerProperty(required = True)
    

class BlogPosts(Handler):
    def get(self):
        ##Used to load pages of blogs
        page = self.request.get("page")     
        pagenum = 0 ##Set this to 0 so that we get the default if the user didnt provide another page
        if(page.isdigit and page!=''):
            pn = int(page)
            if(pn>1):
                count = Post.all(keys_only=True).count()
                if(count>(pn-1)*5):
                    pagenum = ((pn-1)*5)
                else:
                    self.redirect("/?page=0")
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY bid DESC LIMIT 5 OFFSET %s" % pagenum)
        t = jinja_env.get_template("blogmain.html")
        content = t.render(posts = posts)
        self.response.write(content)

class NewEntry(Handler):
    def get(self):
        t = jinja_env.get_template("newpost.html")
        content = t.render()
        self.response.write(content)
        
    def post(self):
        title =cgi.escape(self.request.get("title"))
        body = cgi.escape(self.request.get("body"))

        if title and body:
            count = Post.all(keys_only=True).count()
            p = Post(title=title, body=body, bid = count+1)
            p.put()
            time.sleep(0.1)
            self.redirect("/blog/"+str(count+1))
        else:
            t = jinja_env.get_template("newpost.html")
            content = t.render(error = "You need a title and body",body = body, title = title)
            self.response.write(content)
            
class ViewPostHandler(Handler):
    def get(self, id):
        myID = int(id)
        viewPost = Post.all()
        viewPost.filter('bid =', myID)
        thePost = viewPost.get()
        if thePost is None:
            t = jinja_env.get_template("post.html")
            content = t.render(error = "No post found")
            self.response.write(content)
        else:
            t = jinja_env.get_template("post.html")
            content = t.render(posts = viewPost, error = "")
            self.response.write(content)


app = webapp2.WSGIApplication([
    ('/', BlogPosts),
    ('/blog', BlogPosts),
    ('/newpost', NewEntry),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
