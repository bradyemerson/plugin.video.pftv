# plugin.video.PFTV
This Kodi plugin is geared toward those who want to export shows / seasons / episodes from Project Free TV into the Kodi library. There is little (basically no) emphasis on displaying any meta data about the shows or episodes within the plugin.

### Steps for Using
1. Browse for the shows you'd like to track
2. Mark them as favorites in the context menu
3. Export the favorites into Kodi library

By default only the most recent season is exported from each series. You can manually export additional seasons from the series page (via the context menu for the season you want to export). Same can be done for individual episodes.

### To Do
Only TV shows are supported at this point. Although I left a bunch of code from the Starz plugin (which this is based on), to add movie support at some point in the future.

### Updating Library on Kodi Startup
I also wrote a service plugin which exports TV favorites on Kodi startup so your library stays up to date:
https://github.com/bradyemerson/service.pftv.updater

### Credits
Eldorados - playback is still done through Eldorados's great urlresolver plugin. I also borrowed a couple lines of html parsing from his Project Free TV plugin for finding the video links for each episode.

BlueCop - Kodi Library exporting is based on BlueCop's code from Amazon and Hulu plugins
