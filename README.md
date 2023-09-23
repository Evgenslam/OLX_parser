# OLX_parser
## Описание
This is a parser designed to send notifications to Telegram when new apartments matching specified criteria appear on the real estate website olx.uz. The subscriber takes a survey first to get notifications about all apartments that match his or her criteria.

The app was born out of my own pain trying to find a reasonable accomodation in Tashkent(Uzbekistan).

The script visits the website every 2-3 minutes (with randomized timing). It uses BeautifulSoup for parsing.

The script sets headers to mimic a standard web browser. Previous version used "fake-useragent" and "pyuser," which turned out to be excessive. The script uses three proxies, randomly selecting one for each new request to avoid being blocked. Can also be set to access the website with your own IP address.



