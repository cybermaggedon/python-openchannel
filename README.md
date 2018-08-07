
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
    print("  %s" % (v.name))
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
app = app.create()
app.publish_version(1, autoApprove=True)
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

## Install an app

usr = cli.get_user("3233")
app = cli.get_app_by_safename("fish-1")
own = cli.install_app(usr, app, app.model[0])
print("Installed app.")

## Ownership

print("Product keys:")
owns = cli.list_ownership()
for o in owns:
    print("  %s" % o.productKey)

## Most of the API is implemented

Read openchannel.py for calls which aren't described here.

Most objects are mapped straight in from the OpenChannel API, see the docs
for their structure e.g. `app.name` and `app.customData.summary` work.

