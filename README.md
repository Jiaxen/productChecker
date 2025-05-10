# Product Checker

I wanted to buy something, and it kept getting sold out really quickly! Grrr...

So I wrote a little script that polled the site to see if it was available, and if so, it would send me a Telegram message and an event to a Google Cloud Pub/Sub topic (which triggers more alerts).

The sample config.ini here isn't the product I originally wanted, just an example to show it can be reconfigured for other websites and products. With some modifications, it's useful for booking padel/tennis courts too!

It has a few nice configurable utilities to scan for keywords, but not "false friends" which I don't want, and skip lines with keywords. 
