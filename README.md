
# PyOpenchannel

## Introduction

Python client library for OpenChannel.io, online market-place toolkit.

## Connect

```
import openchannel as oc

marketplaceid = "MARKET PLACE ID HERE"
secret = "SECRET GOES HERE"

cli = oc.Client(marketplaceid, secret)
```

## List apps

```
apps = cli.list_apps()
for v in apps:
    print("  %s" % (v.name, v.customData.summary))
```

## List apps and versions

```
apps = cli.list_app_versions()
for v in apps:
    print("  %s version %s" % (v.name, v.version))
```

## Get an app

```
app = cli.get_app("98127471249728951025")
print(app.name)
```

## Safe name

```
app = cli.get_app_by_safename("fish-1")
print("App %s is %s" % (app.safeName[0], app.name))
```

## Create app

```
app = oc.App(client=cli)
app.name = "Fish"
app.author = "Example Ltd."
app.customData.description = "Here is an app"
app.customData.summary = "Here is an app"
app.customData.icon = icon
app.customData.category = [ "cybersecurity" ]
app.customData.video = [ "https://www.youtube.com/watch?v=K7CnMQ4L9Pc" ]
app.customData.images = [
    "https://upload.wikimedia.org/wikipedia/commons/7/73/Lion_waiting_in_Namibia.jpg"
]
app.developerId = "1"
model = oc.Model(client=cli)
model.type = "single"
model.price = 200
model.license = "single"
model.customData = oc.CustomData()
model.customData.billing = "online"
app.model = [model]
app = app.create()
app.publish_version(1, autoApprove=True)
```

## Update an app
```
app = cli.get_app("my-app-1")
app.customData.summary = "Application"
app.update()
app = app.publish_version(app.version, autoApprove=True)
```
## Delete an app

```
app = cli.get_app("my-app-1")
app.delete()
```

## Stats

```
print("Stats:")
stats = cli.get_stats_total()

for v in stats.apps:
    stat = stats.apps[v]
    app = cli.get_app(v)
    print("  " + app.name, stat["downloads"], stat["views"])

stats = cli.get_stats_series(start=1000 * int(time.time() - (86400 * 7)), end=1000 * int(time.time()))

print("Series:")
print(stats)
```

## Add a review
```
review = oc.Review(client=cli)
review.appId = appid
review.userId = "1"
review.headline = "What a great app"
# 4 out of 5 stars
review.rating = 400
review.description = "What a bunch of stuff"
review.mustOwnApp = False
review.customData.thing = "12389123"
review = review.create()
```
## Get review
```
review = cli.get_review(reviewId)
```
or
```
review = cli.get_review_by_app_user(app, cli.get_user("1"))
```

## Update review
```
review.rating = 300
review.headline = "It's OK"
review = review.update()
```
## User permissions to install an app

```
perm = oc.Permission(client=cli)
perm.userId = "1"
perm = perm.add(app)

perm = cli.get_permission(app, cli.get_user("1"))
print(perm.encode())
perm.delete(app)
```
## App admin

```
app = cli.get_app_version(appid, 1)
app = cli.get_app(appid)
app.change_live_version(1)

print("Status is " + app.status.value)
app.status_change("suspend", "API testing")
```

## Developers

```
grp = oc.DeveloperGroup(client=cli)
grp.groupId = "abcde"
grp.customData.companyName = "Example Ltd."
grp = grp.update()

grp = cli.get_developer_group("abcde")

dev = cli.get_developer("1")

devs = cli.list_developers()
for dev in devs:
    print("  " + dev.name)

dev = cli.get_developer("1")
dev.name = "Mark"
dev.email = "mark@example.org"
dev.customData.companyName = "Example Ltd."
dev.customData.interests = ["cybersecurity", "cycling"]
dev = dev.update()

dev = oc.Developer(client=cli)
dev.developerId = "233"
dev.groupId = "abcde"
dev.name = "Brian"
dev.update()

print("Developer 233:")
dev = cli.get_developer("233")
print("  " + dev.name)
```

## Users

```
grp = oc.UserGroup(client=cli)
grp.groupId = "zzzabcde"
grp.customData.companyName = "Example Ltd."
grp = grp.update()

grp = cli.get_user_group("zzzabcde")

usr = cli.get_user("1")
print("  " + usr.name)

print("Users:")
usrs = cli.list_users()
for usr in usrs:
    print("  " + usr.name)

usr = cli.get_user("1")
usr.name = "Mark"
usr.email = "mark@example.org"
usr.customData.companyName = "Example Ltd."
usr.customData.interests = ["cybersecurity", "cycling"]

usr = usr.update()

usr = oc.User(client=cli)
usr.userId = "3233"
usr.groupId = "zzzabcde"
usr.name = "Brian"
usr.update()

usr = cli.get_user("3233")
print("  " + usr.name)
```

## Uploading

```
file = cli.upload_file("file", "hello world")
print("Uploaded as " + file.fileUrl)
print("  ID " + file.fileId)

file = cli.upload_url("http://example.org/download")
print("Uploaded download " + file.fileUrl)
print("  ID " + file.fileId)
```

## Install an app

```
usr = cli.get_user("3233")
app = cli.get_app_by_safename("fish-1")
own = cli.install_app(usr, app, app.model[0])
print("Installed app.")
```

## Ownership
```
print("Product keys:")
owns = cli.list_ownership()
for o in owns:
    print("  %s" % o.productKey)
```

## Transactions (custom gateway)

```
trans = oc.Transaction()
trans.amount = 200
trans.customData.billing = "sales team"

trans = cli.custom_gateway_add_payment(own, trans)
print("Transaction: " + trans.encode())

print("Transactions:")
transes = cli.list_transactions()
for t in transes:
    print("  %s" % t.encode())

trans = cli.custom_gateway_add_refund(own, trans)
print("Transaction: " + trans.encode())

trans.delete()
print("Refund deleted.")

print("Transactions:")
transes = cli.list_transactions()
for t in transes:
    print("  %s" % t.encode())
```

## Uninstall
```
cli.uninstall_app(own)
```

## Most of the API is implemented

Read openchannel.py for calls which aren't described here.

Most objects are mapped straight in from the OpenChannel API, see the docs
for their structure e.g. `app.name` and `app.customData.summary` work.

