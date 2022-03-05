# coding=utf-8

import pywikibot
from contextlib import suppress
from pywikibot import pagegenerators as pg
from pywikibot.exceptions import LockedPageError
from mwparserfromhell import parse

site = pywikibot.Site('ru', 'wikipedia')

FROM_TEMPLATES = (
    'If-wikidata',
    'Wikidata',
    'Wikidata-coord',
    'Wikidata-coords',
    'Категория по дате',
)

INFOBOX_TEMPLATES = (
    'Карточка',
    'Карточка/блок',
    'Административная единица',
    'АЕ2',
    'Болезнь',
    'Государственная должность',
    'Двигатель',
    'Достопримечательность',
    'Епархия',
    'Карточка оружия',
    'Кинематографист',
    'Кинопремия',
    'Комарка Испании',
    'Линия метрополитена',
    'Музыкальный альбом',
    'Площадь',
    'НП',
    'НП+',
    'НП3',
    'Персонаж',
    'Персонаж сериала',
    'Поселение России',
    'Серия',
    'Спортивный клуб',
    'Страна на Европейских играх',
    'Страна на Олимпийских играх',
    'Танк',
    'Теннисный турнир',
    'Улица',
)

BAD_TEMPLATES = (
    '!',
    '!!',
    '!-',
    ')',
    '!)',
    '(',
    '(!',
    '-',
    '=',
    '0',
    'Align',
    'Ambox',
    'Br separated entries',
    'Bkw',
    'Both',
    'Center',
    'Comment',
    'Coord',
    'CURRENTYEAR',
    'Delink',
    'Doc',
    'Doc-end',
    'Doc-inline',
    'Docpage',
    'Documentation',
    'ESC',
    'Flagicon',
    'Float right',
    'FULLPAGENAME',
    'Hbar',
    'Hide in print',
    'If',
    'Is_numeric',
    'Iw',
    'IPA',
    'Lang',
    'Legend',
    'Location map',
    'NAMESPACE',
    'Navbar',
    'Nbsp',
    'Nobr',
    'Nowrap',
    'PAGENAME',
    'Pct',
    'Ref-info',
    'Replace',
    'Rtl-lang',
    'S',
    'Storm colour',
    'Str find',
    'Str sub',
    'Taxobox conversion',
    'Taxobox image2',
    'Tc nom',
    'Tc nom list',
    'Tc warning center',
    'Tl',
    'U',
    'Ubl',
    'URL',
    'Wikidata',
    'Административная единица/Общие проверки',
    'Антропогеокарточки/Общие проверки',
    'Баскетбол',
    'Баскетбольная форма домашняя и гостевая',
    'Без начала',
    'Бр',
    'Будущий эпизод',
    'В 2 кв. скобках',
    'В Донбассе',
    'Год появления',
    'Дробь',
    'Зл',
    'Иероглифы-в-тексте',
    'К объединению',
    'К переименованию',
    'К разделению',
    'К удалению',
    'Конец скрытого блока',
    'Красная ссылка',
    'Крикетная форма',
    'Музыка:Общие проверки',
    'Начало скрытого блока',
    'Нет изображения',
    'Переписать шаблон',
    'Плохой перевод',
    'ПозКарта',
    'Примечания',
    'Русифицировать параметры шаблона',
    'Станция метро/Эмблема',
    'Страна в родительном падеже',
    'Ср',
    'Таксон/Цвет',
    'Текст в ссылку',
    'Телефонный код',
    'Традиционное верование',
    'Цвет',
    'Цветная ссылка',
    'Удалить теги',
    'Устаревший шаблон',
    'Флаг',
    'Флаг НОК',
    'Флаг НПК',
    'Флагификация',
    'Форматирование изображения',
    'Хоккейная форма',
)


def get_paddings(name):
    right_padding = len(name) - 1
    left_padding = len(name) - len(name.lstrip()) + len('from')
    return left_padding, right_padding


def add_from(infobox_page):
    wikicode = parse(infobox_page.text)
    has_from = False
    has_infobox = False
    test_infobox = False
    test_geocard = False
    first_template = None
    for template in wikicode.filter_templates():
        template_name = template.name.strip()
        template_name = template_name[0].upper() + template_name[1:]

        if template_name in INFOBOX_TEMPLATES:
            test_infobox = True
        if template_name == 'Геокар':
            test_geocard = True
        if first_template is None and \
                template_name not in BAD_TEMPLATES and \
                template_name not in FROM_TEMPLATES and \
                ("Шаблон:%s" % template_name) != infobox_page.title() and \
                not template_name.startswith("Карточка/") and \
                not template_name.startswith("Wikidata/") and \
                not template_name.startswith("Hiero/") and \
                not template_name.startswith("{{{") and \
                not template_name.startswith("Lang-") and \
                not template_name.startswith("Ref-") and \
                not template_name.startswith("Formatnum:") and \
                not template_name.startswith("Fullurl:") and \
                not template_name.startswith("Plural:") and \
                not template_name.startswith("Uc:") and \
                not template_name.startswith("Ucfirst:") and \
                not template_name.startswith("Urlencode:") and \
                not template_name.startswith("#expr:") and \
                not template_name.startswith("#if:") and \
                not template_name.startswith("#If:") and \
                not template_name.startswith("#ifeq:") and \
                not template_name.startswith("#iferror:") and \
                not template_name.startswith("#ifexists:") and \
                not template_name.startswith("#ifexpr:") and \
                not template_name.startswith("#property:") and \
                not template_name.startswith("#tag:") and \
                not template_name.startswith("#switch:"):
            first_template = template_name

        if any(param.name.strip() == 'from' for param in template.params):
            if template_name in INFOBOX_TEMPLATES:
                has_from = True
                continue

        if template_name in INFOBOX_TEMPLATES:
            has_infobox = True
            left_padding = 0
            right_padding = 0
            index = 0
            for i, param in enumerate(template.params):
                name = param.name.strip()
                if name == 'автозаголовки':
                    left_padding, right_padding = get_paddings(param.name)
                    index = i
                    break
                if name == 'имя шаблона' or name == 'имя карточки':
                    left_padding, right_padding = get_paddings(param.name)
                    index = i
                    break
                elif name == 'имя':
                    left_padding, right_padding = get_paddings(param.name)
                    index = i
                elif right_padding == 0:
                    left_padding, right_padding = get_paddings(param.name)
            padded_from = 'from'.rjust(left_padding).ljust(right_padding)
            from_code = "%s = {{{from|}}}\n" % padded_from
            if index and template.params[index].value.endswith("\n\n"):
                new_value = template.params[index].value.rstrip("\n") + "\n"
                template.params[index].value = new_value
                from_code += "\n"
            template.params.insert(index + 1, from_code)

        elif template_name in FROM_TEMPLATES \
                or template_name.startswith("Wikidata/") \
                or template_name.startswith("Карточка/"):
            template.params.append("from={{{from|}}}")

    # if not test_infobox:
    #     if test_geocard:
    #         # print('GEOCARD: %s' % infobox_page.title())
    #         pass
    #     elif first_template is None:
    #         print('* {{t|%s}}' % infobox_page.title().replace('Шаблон:', ''))
    #     else:
    #         print('* {{t|%s}} (<code><nowiki>{{%s}}</nowiki></code>)' % (
    #             infobox_page.title().replace('Шаблон:', ''),
    #             first_template,
    #         ))

    if has_from:
        print(infobox_page.title())

    if not has_infobox:
        return

    print('OK: %s' % infobox_page.title())
    return

    infobox_page.text = wikicode
    summary = u"автоматическое добавление параметра from в вызовы шаблонов" + \
              u" {{Карточка}}, {{wikidata}} и их подшаблонов"
    with suppress(LockedPageError):
        infobox_page.save(summary, force=True)


def iterate_items():
    infobox_category = pywikibot.Category(site, 'Шаблоны-карточки по алфавиту')
    generator = pg.CategorizedPageGenerator(infobox_category, namespaces=10)
    for infobox_page in generator:
        #print(infobox_page.title())
        add_from(infobox_page)


iterate_items()
