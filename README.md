# OLX_parser
Это парсер, чтобы приходили оповещения в телегу при появлении новых квартир по заданным параметрам на сайте недвиги. 
Скрипт заходит на сайт каждые 2-3 минуты (время рандомизировано). 
Бьютифул суп (json не нашёл). 
Headers задал своего родного браузера. Пробовоал fake-useragent и pyuser, но с ними почему-то не работает. 
Приобрёл 3 прокси, из которых рандомно выбираю при каждом новом запросе, чтобы избежать блокировки.

Вопросы

-Последовательность написания функций - правильно ли?
-Блок try except работает не так, как я ожидал. Думал, он выведет надпись и продолжит работу,а скрипт всё равно падает с ошибкой.
-Что не так с фейк-юзерагентом?

Ссылка на сайт. https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?currency=UZS&search%5Border%5D=created_at%3Adesc&search%5Bfilter_enum_comission%5D%5B0%5D=no&view=list
