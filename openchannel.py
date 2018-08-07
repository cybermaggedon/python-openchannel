
"""
Python API for openchannel.io
"""

import requests
import json
import time

class ApiError(Exception):
    """
    Exception encapsulating an error in the Openchannel API.  Member
    code is the HTTP status code, value is the error message.
    """
    def __init__(self, code, value):
        """
        Constructor, code=HTTP status code, value=error message
        """
        self.code = code
        self.value = value
    def __str__(self):
        return "%s: %s" % (repr(self.code), repr(self.value))

class Obj:
    """
    Base class for a number of openchannel objects, encapsulates standard
    JSON parsing, and string conversion.
    """
    def __init__(self, client=None):
        if client != None: self.client=client
    def parse(self, data):
        for v in data:
            setattr(self, v, data[v])
        return self
    def __str__(self):
        return str({v: getattr(self, v) for v in self.__dict__})

class CustomData(Obj):
    """
    Represents a custom data for an app, user or group.
    """
    pass

class ObjCD(Obj):
    """
    Base class for anything with custom data
    """
    def __init__(self, client=None):
        Obj.__init__(self, client)
        self.customData = CustomData()
    def parse(self, data):
        """
        Initialises an app with data, data should be the output of
        requests json() method.
        """
        for v in data:
            if v == "customData":
                self.customData = CustomData().parse(data[v])
            else:
                setattr(self, v, data[v])
        return self

    def encode(self):
        res = {v: getattr(self, v) for v in self.__dict__}
        res["customData"] = self.customData.__dict__
        if "client" in res:
            del res["client"]
        return json.dumps(res)

class File(Obj):
    """
    Represents a downloadable file object in openchanel.io
    """
    pass

class Ownership(ObjCD):
    """
    Represents a downloadable file object in openchanel.io
    """
    def update(self):
        return self.client.update_ownership(self)

class Stats(Obj):
    """
    Represents statistics
    """
    pass
        
class Model(Obj):
    """
    Represents an application pricing model.
    """
    pass

class Statistics(Obj):
    """
    Represents app statistics.
    """
    pass

class Status(Obj):
    """
    Represents an application's status.
    """
    pass
        
class App(Obj):
    """
    Encapsulates an app
    """
    def __init__(self, client=None):
        """
        Constructor, client handle can be passed in.
        """
        Obj.__init__(self, client)
        self.customData = CustomData()

    def parse(self, data):
        """
        Initialises an app with data, data should be the output of
        requests json() method.
        """
        for v in data:
            if v == "customData":
                self.customData = CustomData().parse(data[v])
            elif v == "status":
                self.status = Status().parse(data[v])
            elif v == "statistics":
                self.statistics = Statistics().parse(data[v])
            elif v == "model":
                self.model = [Model().parse(m) for m in data["model"]]
            else:
                setattr(self, v, data[v])

        # Helps list comprehensions if we return the app object.
        return self

    def encode(self):
        """
        Encodes to JSON
        """
        res = {v: getattr(self, v) for v in self.__dict__}
        res["customData"] = self.customData.__dict__
        if "status" in self.__dict__:
            res["status"] = self.status.__dict__
        if "model" in self.__dict__:
            res["model"] = [v.__dict__ for v in self.model]
        if "client" in res:
            del res["client"]
        return json.dumps(res)

    def delete(self):
        """
        Deletes an app
        """
        self.client.delete_app(self)

    def create(self):
        """
        Creates an app
        """
        return self.client.create_app(self)

    def update(self, version):
        """
        Updates an app's draft form.
        """
        return self.client.update_app(self, version)

    def publish_version(self, version, autoApprove=False):
        """
        Publishes an app's version
        """
        self.client.publish_app_version(self, version, autoApprove)

    def delete_version(self, version):
        """
        Deletes an app version
        """
        self.client.delete_app_version(self, version)

    def change_live_version(self, version):
        """
        Changes the live version to a previously published form
        """
        self.client.change_live_version(self, version)

    def status_change(self, status, reason):
        """
        Changes an app's status, status=suspend/unsuspend
        """
        self.client.status_change(self, status, reason)

class Developer(ObjCD):
    """
    Encapsulates an app developer
    """
    def update(self):
        """
        Create/update a developer
        """
        return self.client.update_developer(self)

    def create(self):
        """
        Synonymous with update
        """
        return self.client.update_developer(self)

class User(ObjCD):
    """
    Encapsulates an app user
    """
    def update(self):
        """
        Create/update a user
        """
        return self.client.update_user(self)

    def create(self):
        """
        Synonymous with update
        """
        return self.client.update_user(self)

class DeveloperGroup(ObjCD):
    """
    Encapsulates a developer group
    """
    def update(self):
        return self.client.update_developer_group(self)

    def create(self):
        return self.client.update_developer_group(self)

class UserGroup(ObjCD):
    """
    Encapsulates a user group
    """
    def update(self):
        return self.client.update_user_group(self)

    def create(self):
        return self.client.update_user_group(self)

class Client:
    """
    Encapsulates an openchannel.io client and makes API calls.
    """
    def __init__(self, marketplaceid, secret, userId=1, developerId=1):
        """
        Constructor
        """
        self.auth = requests.auth.HTTPBasicAuth(marketplaceid, secret)
        self.session = requests.Session()
        self.userId = userId
        self.developerId = developerId
        self.base = "https://market.openchannel.io/v2"

    def list_apps(self, query=None):

        if query == None:
            query = { "status.value": "approved" }

        url = "%s/apps?query=%s&sort=%s&userId=%s" % (
            self.base, query, {"randomize": 1}, self.userId
        )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

        return [App(client=self).parse(v) for v in resp.json()["list"]]

    def search_apps(self, text, query=None, fields=None):

        if query == None:
            query = { "status.value": "approved" }

        if fields == None:
            fields = [
                "name", "customData.summary", "customData.description"
            ]

        url = "%s/apps?query=%s&textSearch=%s&fields=%s&userId=%s" % (
            self.base, query, text, fields, self.userId
        )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

        return [App(client=self).parse(v) for v in resp.json()["list"]]

    def list_app_versions(self, query=None):

        if query == None:
            query = { "status.value": "approved" }

        url = "%s/apps/versions?query=%s&sort=%s&developerId=%s" % (
            self.base, query, {"randomize": 1}, self.developerId
        )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

        return [App(client=self).parse(v) for v in resp.json()["list"]]

    def delete_app(self, app):

        url = "%s/apps/%s?developerId=%s" % (
            self.base, app.appId, self.developerId
        )

        resp = self.session.delete(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

    def delete_app_version(self, app, version):

        url = "%s/apps/%s/versions/%s?developerId=%s" % (
            self.base, app.appId, version, self.developerId
        )

        resp = self.session.delete(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

    def create_app(self, app):

        headers = { "Content-Type": "application/json" }
        request = app.encode()

        url = "%s/apps?developerId=%s" % (
            self.base, self.developerId
        )

        resp = self.session.post(url, data=request, auth=self.auth,
                                 headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return App(client=self).parse(resp.json())

    def update_app(self, app, version):

        headers = { "Content-Type": "application/json" }
        request = app.encode()

        url = "%s/apps/%s/versions/%s?developerId=%s" % (
            self.base, app.appId, version, self.developerId
        )

        resp = self.session.post(url, data=request, auth=self.auth,
                                 headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return App(client=self).parse(resp.json())

    def publish_app_version(self, app, version, autoApprove=False):

        headers = { "Content-Type": "application/json" }
        request = {
            "version": version,
            "developerId": self.developerId,
            "autoApprove": autoApprove
        }
        
        url = "%s/apps/%s/publish" % (self.base, app.appId)

        resp = requests.post(url, data=json.dumps(request),
                             headers=headers, auth=self.auth)

        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

    def get_app_version(self, id, version):

        headers = { "Content-Type": "application/json" }

        url = "%s/apps/%s/versions/%s?developerId=%s" % (
            self.base, id, version, self.developerId
        )

        resp = self.session.get(url, auth=self.auth,
                                headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return App(client=self).parse(resp.json())

    def get_app(self, id):

        headers = { "Content-Type": "application/json" }

        url = "%s/apps/%s?userId=%s" % (
            self.base, id, self.userId
        )

        resp = self.session.get(url, auth=self.auth,
                                headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return App(client=self).parse(resp.json())

    def change_live_version(self, app, version, autoApprove=False):

        headers = { "Content-Type": "application/json" }
        request = {
            "version": version,
            "developerId": self.developerId
        }
        
        url = "%s/apps/%s/live" % (self.base, app.appId)

        resp = requests.post(url, data=json.dumps(request),
                             headers=headers, auth=self.auth)

        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

    def status_change(self, app, status, reason):

        headers = { "Content-Type": "application/json" }
        request = {
            "status": status,
            "reason": reason,
            "developerId": self.developerId
        }
        
        url = "%s/apps/%s/status" % (self.base, app.appId)

        resp = requests.post(url, data=json.dumps(request),
                             headers=headers, auth=self.auth)

        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

    def upload_file(self, filename, data):

        url = "%s/files" % self.base

        files = { filename: data }
        resp = requests.post(url, files=files, auth=self.auth)

        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

        return File().parse(resp.json())

    def upload_url(self, u):

        headers = { "Content-Type": "application/json" }
        request = {
            "url": u
        }
        
        url = "%s/files/url" % self.base

        resp = requests.post(url, data=json.dumps(request), auth=self.auth,
                             headers=headers)

        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

        return File().parse(resp.json())

    def get_app_by_safename(self, safename):

        headers = { "Content-Type": "application/json" }

        url = "%s/apps/bySafeName/%s?userId=%s" % (
            self.base, safename, self.userId
        )

        resp = self.session.get(url, auth=self.auth,
                                headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return App(client=self).parse(resp.json())

    def get_developer(self, id):

        url = "%s/developers/%s" % ( self.base, id )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return Developer(client=self).parse(resp.json())

    def list_developers(self, query=None):

        if query == None:
            query = {}

        url = "%s/developers?query=%s&sort=%s" % (
            self.base, query, {"name": 1}
        )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

        return [Developer(client=self).parse(v) for v in resp.json()["list"]]

    def update_developer(self, dev):

        headers = { "Content-Type": "application/json" }
        request = dev.encode()

        url = "%s/developers/%s" % (
            self.base, dev.developerId
        )

        resp = self.session.post(url, data=request, auth=self.auth,
                                 headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return Developer(client=self).parse(resp.json())

    def get_developer_group(self, id):

        url = "%s/developers/groups/%s" % ( self.base, id )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return DeveloperGroup(client=self).parse(resp.json())

    def update_developer_group(self, group):

        headers = { "Content-Type": "application/json" }
        request = group.encode()

        url = "%s/developers/groups/%s" % (
            self.base, group.groupId
        )

        resp = self.session.post(url, data=request, auth=self.auth,
                                 headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return DeveloperGroup(client=self).parse(resp.json())

    def get_user(self, id):

        url = "%s/users/%s" % ( self.base, id )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return User(client=self).parse(resp.json())

    def list_users(self, query=None):

        if query == None:
            query = {}

        url = "%s/users?query=%s&sort=%s" % (
            self.base, query, {"name": 1}
        )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

        return [User(client=self).parse(v) for v in resp.json()["list"]]

    def update_user(self, user):

        headers = { "Content-Type": "application/json" }
        request = user.encode()

        url = "%s/users/%s" % (
            self.base, user.userId
        )

        resp = self.session.post(url, data=request, auth=self.auth,
                                 headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return User(client=self).parse(resp.json())

    def get_user_group(self, id):

        url = "%s/users/groups/%s" % ( self.base, id )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return UserGroup(client=self).parse(resp.json())

    def update_user_group(self, group):

        headers = { "Content-Type": "application/json" }
        request = group.encode()

        url = "%s/users/groups/%s" % (
            self.base, group.groupId
        )

        resp = self.session.post(url, data=request, auth=self.auth,
                                 headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return UserGroup(client=self).parse(resp.json())
    
    def get_stats_total(self, start=None, end=None, query=None, fields=None):

        if query == None:
            query = {}

        if start == None: start = int(time.time() - 86400) * 1000
        if end == None: end = int(time.time()) * 1000

        if fields == None:
            fields = [
                "views", "downloads"
            ]
        fields = ",".join(fields)

        url = "%s/stats/total?query=%s&start=%d&end=%d&fields=%s" % (
            self.base, query, start, end, fields
        )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

        return Stats().parse(resp.json())

    def get_stats_series(self, start=None, end=None, query=None, field=None):

        if query == None:
            query = {}
        query = json.dumps(query)

        if start == None: start = int(time.time() - 86400) * 1000
        if end == None: end = int(time.time()) * 1000

        if field == None:
            field = "downloads"

        url = "%s/stats/series/%s/%s?query=%s&start=%d&end=%d" % (
            self.base, "day", field, query, start, end
        )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

        return resp.json()

    def install_app(self, user, app, model):

        headers = { "Content-Type": "application/json" }
        request = {
            "appId": app.appId,
            "userId": user.userId,
            "modelId": model.modelId
        }

        url = "%s/ownership/install" % (
            self.base
        )

        resp = self.session.post(url, data=json.dumps(request), auth=self.auth,
                                 headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return Ownership(client=self).parse(resp.json())

    def get_ownership(self, id):

        url = "%s/ownership/%s" % ( self.base, id )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)
        
        return Ownership(client=self).parse(resp.json())

    def list_ownership(self, query=None):

        if query == None:
            query = {}

        url = "%s/ownership?query=%s&sort=%s" % (
            self.base, query, {"date": 1}
        )

        resp = self.session.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

        return [Ownership(client=self).parse(v) for v in resp.json()["list"]]

    def uninstall_app(self, own):

        headers = { "Content-Type": "application/json" }
        request = {
            "userId": own.userId
        }

        url = "%s/ownership/uninstall/%s" % (
            self.base, own.ownershipId
        )

        resp = self.session.post(url, data=json.dumps(request), auth=self.auth,
                                 headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

    def update_ownership(self, own):

        headers = { "Content-Type": "application/json" }
        request = own.encode()

        url = "%s/ownership/%s" % (
            self.base, own.ownershipId
        )

        resp = self.session.post(url, data=request, auth=self.auth,
                                 headers=headers)
        if resp.status_code != 200:
            raise ApiError(resp.status_code, resp.text)

        print resp.json()
        
        return Ownership(client=self).parse(resp.json())
    
