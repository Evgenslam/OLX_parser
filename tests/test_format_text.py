from olx_parser import format_text

def format_text_good():
    assert format_text({'title': 'Ijaraga hovli joy!!! Student bolalar!!!', 'price': '80 у.е.Договорная', 'district':
        'Яшнабадский район', 'time': '2022-12-28 в 10:04', 'lnk':
        'https://www.olx.uz//d/obyavlenie/ijaraga-hovli-joy-student-bolalar-ID30cA2.html'} == '80 у.е.Договорная
    Яшнабадский район
    https://www.olx.uz//d/obyavlenie/ijaraga-hovli-joy-student-bolalar-ID30cA2.html
    Ijaraga hovli joy!!! Student bolalar!!!
    2022-12-28 в 10:04'

