# Product Checker

I wanted to buy something, and it kept getting sold out really quickly! Grrr...

So I wrote a quick script that polled the site to see if it was available and if so, it would send a message to a Google Cloud Pub/Sub topic, which I had hooked up to some alerts and other scripts. 

The sample config.ini here isn't the product I originally wanted, just an example, which can be reconfigured for other websites and products. With some modifications, useful for booking padel/tennis courts too!
It has a few nice configurable utilities to scan for keywords, but not "false friends" which I don't want, and skip lines with keywords. 