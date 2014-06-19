import re
# Этот модуль вмещает все функции, требуемые для обработки строк, встретившихся
# в исходном коде программы.

def ifre(furtherInstance):
    # Эта функция принимает на вход объект класса further и возвращает
    # булево значение: True означает, что регулярные выражения
    # был доступны для этого фрагмента кода, False - что нет.
    if furtherInstance.imports == None:
        return False
    for i in furtherInstance.imports:   # перебираем массив
                                        # с названиями импортированных модулей
        if i == u're':
            return True
    return False


def re_list(furtherInstance, stop_re = []):
    # Эта штука разделяет всё, что в нее поступило, на два набора:
    # регекспы и не регекспы
    array_of_re = []
    if ifre(furtherInstance) == False:
        array_of_not_re = furtherInstance.getre()
    else:
        array_of_not_re = []
        symbols = u'+[]|^$'    # Специфические для регулярных выражений символы
        additional_symbols = u')(.'
        if furtherInstance.getre() != None:
            for i in furtherInstance.getre():
     #           print i
                if re.search(u'^SEARCH', i, flags = re.U) != None:
                    i = re.sub(u'^SEARCH', u'', i, flags = re.U)
                   # print i
                    array_of_re.append(i)
                    continue
                counter = 0
                for j in symbols:
                    for q in i:
                        if q == j:
                            counter += 1
                if counter != 0:
                    for j in additional_symbols:
                        for q in i:
                            if q == j:
                                counter += 1

                if counter != 0:
                    array_of_re.append(i)
                    counter = 0
                else:
                    array_of_not_re.append(i)
    if array_of_re == []:
        array_of_re = None
    if array_of_not_re == []:
        array_of_not_re = None
    result = [array_of_re, array_of_not_re]
    if result[0] == None and result[1] == None:
        return None
    return result


def purify(reg):     # Очищаем регексп от оформления строки
    reg = reg.strip(u'ru').strip(u'"\'\\')


def replace_classes(reg, setting = 1):
    # Эта штука помогает заменять классы символов на стандартные "или"
    if setting == 1:
        pieces = re.findall(u'\\[.+?\\]', reg, flags = re.U)
        for i in pieces:
            new_part = u''
            for j in i:     # Перебираем кусочки по одной букве
                new_part += (j + u'|')
            new_part = u'(' + new_part[:-1] + u')'
            reg = re.sub(escape(i), new_part, flags = re.U)

    
def parse_line(line):
    # Функция получает на вход выражение, которое надо распарсить
    left_b = 0
    right_b = 0
    pieces = []
    l = u''
    for i in line:
        if i != u'|':   # Если время парсить не пришло...
            l += i      # пополняем кусочек
            if i == u'(' or i == u'[':
                left_b += 1
            elif i == u')' or i == u']':
                right_b += 1
        else:
            if left_b == right_b:
                pieces.append(l)
                l = u''
            else:
                l += i
    pieces.append(l)
    # Возвращаем первоначальные куски.
    return pieces

def parse_line_recursive(lines, param = 0):
    # Функция получает на вход выражение, которое надо распарсить
    left_b = 0
    right_b = 0
    pieces = []
    l = u''
    for i in line:
        if i != u'|':   # Если время парсить не пришло...
            l += i      # пополняем кусочек
            if i == u'(' or i == u'[':
                left_b += 1
            elif i == u')' or i == u']':
                right_b += 1
        else:
            if left_b == right_b:
                pieces.append(l)
                l = u''
            else:
                l += i
    pieces.append(l)
    parse_line_recursive()
    # Возвращаем первоначальные куски.
    return pieces


def depth_counter(piece_of_regexp):
    eternal_counter = 0
    counter = 0
    for i in piece_of_regexp:
        if i == u'(':
            counter += 1 # увеличиваем счетчик на 1
        if counter > eternal_counter:
            eternal_counter = counter
        if i == u')':
            counter -= 1
    return eternal_counter


# Одиночная буква - SL
# Последовательность цифр, не окруженных буквами/пробелами - NUMSONLY
# Текст на русском языке без цифр - RUSTEXT
# Последовательность из английских букв с возможным употреблением цифр - LETTERSNUMS
# Указание на количество повторов группы в фигурных скобках - RP (не реализовано, т.к. необходимость
# не очевидна).
def structurize(reg):
 #   print reg,
    tags = [u'RUSTEXT', u'NUMSONLY', u'SL']
    new = re.sub(u'[йцукенгшщзхъёэждлорпавыфячсмитьбю ]{2,}', u'RUSTEXT', reg.lower(), flags = re.U|re.I)
    # все последовательности из русских букв и пробелов стали заменены на маркер RUSTEXT
    new = re.sub(u'(^|[^\\d\\w ])\\d+($|[^\\d\\w ])', u'\\1NUMSONLY\\2', new, flags = re.U)
    # Все цифры не в пробелах или буквах заменились на маркер NUMSONLY
    new = re.sub(u'([^\\w]|^)[\\w]([^\\w]|$)', u'\\1SL\\2', new, flags = re.U|re.I)
    # Все одиночные буквы оказались заменены на маркер SL
    patterns = re.findall(u'[\\w\\d ]+', new, flags = re.U|re.I) # нам не надо заменять метки!
    patterns = [i for i in patterns if i not in tags] # отсеяли нашедшиеся метки
    for i in patterns:
        new = re.sub(i, u'LETTERSNUMS', new, flags = re.U|re.I)
 #   print new
    return new

def comparere(r1, r2):
    re1 = r1[:]
    re2 = r2[:]
    purify(re1)
    purify(re2)
    if re1 == re2:  # Они совпали!
        return 1
    elif set(parse_line(re1)) == set(parse_line(re2)):
        return 2
    else:
        if depth_counter(re1) > 2 and depth_counter(re2) > 2 and \
        structurize(re1) == structurize(re2):
            return 3
        else:
            pieces1 = [structurize(i) for i in parse_line(re1)]
            pieces2 = [structurize(i) for i in parse_line(re2)]
            pd1 = [depth_counter(i) for i in parse_line(re1)]
            pd2 = [depth_counter(i) for i in parse_line(re2)]
            if max(pd1) > 2 and max(pd2) > 2:
                if set(pieces1) == set(pieces2):
                    return 4
                else:
                    return 0
            else:
                return 0


def TestF(re1, re2):
    x = comparere(re1, re2)
    if x == 1:
        print u'полностью идентичны'
    elif x == 2:
        print u'coстоят из одинаковых частей'
    elif x == 3:
        print u'сходны по структуре'
    elif x == 4:
        print 'части'
    else:
        print u'ничего общего'

re1 = u'asd(f(f(f)f)f)|f|ggg'
re2 = u'f|asd|asd(f(f(f)f)f)'

#print depth_counter(re2)

#TestF(re1, re2)
    
