# Current Project Status

## Dec 4, 2020:
I'm currently trying to get all sites working from the linux ec2 box. I've gotten all sites working
using the requests library in python from windows, but everything except Best Buy works when running
from the ec2 box. Mainly, all I had to change was the request header for user agent. I'm not sure why
Best Buy doesn't work though, it might be because it detects the request is coming from an Amazon IP
address??? 

The chrome web driver currently works for all sites on the ec2 box but it's much slower than the
requests library. Best Buy takes the longest of all sites, which I'm guessing is because their website
has to much crap on a single product page. I would like to figure out how to use the requests library
if at all possible. Timing is important when trying to locate if something is in stock.
I could throw in the towel on the Best Buy part for now and just try to get the cron job set up with
the requests library or I could try running it on my Rasp Pi or a linux virtual machine on my PC,
mainly so it comes from a different ip address than the EC2 box.

## Nov 30, 2020
I was having issues connecting to some sites (such as Micro Center) because I think
the website can tell it isn't an actual user connecting through a web browser. This might involve changing the
headers in the request, similar to what is being done in commented line 85. The best way to figure out what
headers to add might be to try and echo what the chrome browser is sending vs what is being sent by
the request using the urllib library (line 85) or what is being done by the headless selenium chrome
webdriver on line 103. I'm also not sure if selenium allows you to add headers.

I think trying to run in headless mode using the chrome web driver either adds or removes header(s) that other
sites see as a non-legitimate browser. I *think* running the chrome web driver without the "--headless"
argument might be causing the box to run out of memory. Running without "--headless" using the windows
chromedriver works fine with Micro Center's website (not sure about Best Buy). One way to see if this is an
issue might be to either run a virtual linux machine on my PC or try running the linux chromedriver on my
raspberry pi(which might have more memory than the EC2 box but not sure).