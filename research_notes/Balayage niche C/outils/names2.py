import json, re
from yt import *
for h in ["@costoffree","@thecostoffree","@behindthebill","@thebillbehind","@hiddentab","@thehiddentab","@nothingisfree","@nothingsfree",
          "@whopicksupthetab","@pickupthetab","@thetabeconomics","@tabpaid","@thetollbooth","@tollbootheconomics","@thehiddentoll","@hiddentoll",
          "@thefreelunch","@nofreelunch","@nofreelunchtv","@thereisnofreelunch","@freelunchfiles","@thefreelunchfiles"]:
    r = api("channels", part="snippet,statistics", forHandle=h)
    it = r.get("items") or []
    print(h, ("PRIS: "+it[0]["snippet"]["title"]+" | abonnés "+it[0]["statistics"].get("subscriberCount","?")+" | vidéos "+it[0]["statistics"].get("videoCount","?")) if it else "libre")
