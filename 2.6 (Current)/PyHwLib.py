import re, codecs

# ----- Бывший модуль Loops. Не проверялось -----
# Функция просто находит в строке переменную-итератор
def Find(line):
    #print 'W'
    m = re.search(u'^\\s*for\\s+(.+?)\\s+in', line, flags = re.I|re.U)
    if m != None:
        #print 'Yes'
        return m.group(1)
    else:
        return None


def Enumerate(lines, nums):
    Map = []    # В этот массив мы будем класть пары чисел:
                # от номера такого-то до номера такого-то идёт цикл
    Max = 0
    for i in range(len(lines)):     # Совершаем первичный обход, ища самый глубокий цикл.
        if Find(lines[i]) != None:  # Если что-то нашлось...
            if nums[i] > Max:       # ... делаем новый максимум, если надо
                Max = nums[i]
                
    counter = 0
    #print Max
    start = 0   # Номер первой найденной строки
    L = None
    while counter <= Max:   # Пока мы не напроверяли до максимума того, что надо проверять
        for i in range(len(lines)):  # Прогоняем снова все строчки
            if nums[i] == counter:      # Если мы подходим требованию,
                v = Find(lines[i])      # ищем.
                if v != None:   # Если нашли,
                    if  L == True:  # Если до этого мы уже были в цикле, то
                        tup = (start, i - 1, counter)    # сохраняем данные о нем в массив
                        #print tup
                        Map.append(tup)
                    L = True    # помечаем, что да, и
                    start = i   # фиксируем номер, где именно.
                else:
                    if L != None:
                        tup = (start, i - 1, counter)
                        Map.append(tup)
                    L = False   # Поставили метку непребывания в цикле.
        if L == True:
            tup = (start, i, counter)
            Map.append(tup)
            L = None
        counter += 1
    return Map


def Index(signatures):  # Эта функция пересчитывает найденные глубины в нормальную нумерацию.
    Max = 0
    a = []
    for i in signatures:
        if i[2] > Max:
            Max = i[2]
        if i[2] not in a:
            a.append(i[2])
    # Теперь как-то надо сделать так, чтобы установить соответствие
    # между номерами i[2] и нормальной нумерацией с нуля до х.
    dic = {a[i]: i for i in range(len(a))}
    return dic


def Rename(signatures, array):
    copy = array[:]
    compl = Index(signatures)
    for i in signatures:    # Перебираем диапазоны циклов. 
        varname = Find(copy[i[0]])
        if varname != None:
            regexp = u'([^\\w]|^)' + varname + u'([^\\w]|$)'
            for j in range(i[0], i[1] + 1): # Перебираем строки, где актуально происходящее
                copy[j] = re.sub(regexp, u'\\1<loopvar' + unicode(compl[i[2]]) + u'>\\2', copy[j], flags = re.U)
        else:
            pass
    return [copy, len(compl)]


def Do(array, n):
    x = Rename(Enumerate(array, n), array)
    for i in range(len(x[0])):
        x[0][i] = re.sub(u'<loopvar', u'<variable', x[0][i], flags = re.U)
    return x

# ----- Конец Loops -----


class primary:
    def __init__(self, name, address_id):   # создаём очень простой класс
        self.plaintext = reader(name)       # тут список строчек
        self.pathid = address_id            # и фиксируем номер работы,
                                            # которую проверяем
        if self.plaintext == None:
            print u'o_O В файле не нашлось ни одной строчки'
    def getcode(self):  # метод для извлечения списка строчек
        return self.plaintext
    def getid(self):    # метод для получения идентификатора
        return self.pathid
    def change_plaintext(self, new_plaintext_array):
        self.plaintext = new_plaintext_array



class further:
    def __init__(self, identificator_array_array):
        self.pathid = identificator_array_array[0]  # идентификатор сразу заносим в нужное место, а дальше...
        lines = identificator_array_array[1]        # а сюда выносится список настроек
        tuples = realdepth(identificator_array_array[1])    # сюда вынесен список кортежей, который надо поделить
        # на два списка
        self.nums = [i[0] for i in tuples]  # сюда выделяем глубину строчек
        self.lines = [i[1] for i in tuples] # сюда выделяем строчки
        self.imports = [i.strip() for i in self.lines[0].split(u'|') if i.strip() != u''] # Это как бы массив с импортами
        self.lines = self.lines[1:]
        self.nums = self.nums[1:]
        self.regexps = []                   # тут когда-нибудь будут лежать регекспы
        afterloop = Do(self.lines, self.nums)
        self.lines = afterloop[0]
        self.loopnum = afterloop[1]
        x = variable_renamer(self.lines, variables(self.lines) + def_vars(self.lines), afterloop[1])
        # в итоге в переменной получаем кортеж из строк и словарь соответствий переменных
        self.varnames = x[1]
        self.lines = x[0]
    def correct_2in1(self): # метод делит строки, содержащие что-то на одной строке с условным
                            # оператором и т.п.
        inappr_syntax_editor(self)
    def delete_regexps(self):   # эта штука вырезает все регекспы из self.lines
        regexps = string_normalizer(self)   # сюда вырезаем строки
        self.regexps = regexps
        a = []
        for line in self.lines:
            for i in regexps:
                line = re.sub(i, u'<regexp>', line, flags = re.I|re.U)
            a.append(line)
        self.lines = a
    def cn(self):
        comparison_normalizer(self)
    def getre(self):
        if self.regexps != []:
            return self.regexps
        else:
            return None
    def getcode(self):
        return self.lines
    def getid(self):
        return self.pathid
    def getdepth(self):
        return self.nums
    def change_text(self, code, depths):
        if len(code) == len(depths):
            self.nums = depths
            self.lines = code
        else:
            print u'Unknown mistake'


def reader(name):
    ar = []
    encodings = ['utf-8-sig', 'MacCyrillic', 'cp1251', 'utf-16-le', 'utf-16-be']
    # Возможный набор кодировок. 
    for i in encodings: # Проверка всех по очереди
        try:
            f = codecs.open(name, 'r', i) 
            for line in f:
                if re.search(u'^\\s*$', line, flags = re.I|re.U) == None: # отсекаем пустые строки
 #                   print line
                    ar.append(line.rstrip())
            f.close()
            break
        except:
            pass
    if ar != []:
        return ar # Ура, что-то считалось
    else:
        return None # :(


def PrintReaderResult(address): # Тест для reader
    for i in reader(address):
        print i


def comment_away(primary_object, set_for_comments):
    # первый аргумент - объект класса primary, второй - пустое множество,
    # куда можно сложить комменты
    array_without_comments = []
    source = primary_object.getcode()
    previous = None # это значит, что строка будет первой
    for i in range(len(source)):  # перебираем элементы массива со строками
        m = re.search(u'^(.*?)#(.*)$', source[i], flags = re.I|re.U)
        if m == None: # если не нашли, значит, не нашли.
            array_without_comments.append(source[i]) #переносим исходную версию строки
        else:
            if re.search(u'^\\s*$', m.group(1), flags = re.I|re.U) == None:             # если строка не пустая
                array_without_comments.append(m.group(1).rstrip())    # тогда сохраняем в качестве очищенной
            # то, что cлева
            set_for_comments.add(m.group(2).lstrip(u'#'))# а то, что в комментс, отправляем в множество
    return array_without_comments


def CommentAwayTest(address):
    obj = primary(address, 0)
    temp_set = set()
    x = comment_away(obj, temp_set)
    print 'Code:'
    for i in x:
        print i
    print u'\nComments:'
    for i in temp_set:
        print i


# Эти функции отвечают за подсчёт строк
def depth_definer(array):
# получает массив строк программы, 
# а возвращает массив кортежей, первое число в каждом кортеже - глубина,
# измерeнная в пробелах (!!!),
# вторая часть кортежа - строка без пробела в начале
    new_array = []
    for i in array:
        m = re.search(u'^( *)([^ ].*)$', i, flags = re.I|re.U)
        # тут мы отсчитываем пробелы
        if m != None:
            tup = (len(m.group(1)), m.group(2))
        else:
            tup = (0, u'<emptyline>')   # рудимент. Однако пусть живёт
        new_array.append(tup)
    return new_array


# Эта функция опознаёт уровень вложенности без ориентации на то, что в начале строки должно быть кратное 4
# Число пробелов
def realdepth(array):
    new = depth_definer(array)# получили массив кортежей, в котором
    # первые элементы - количество пробелов в начале, вторые - сами строки с отрезанными пробелами
    previous_line = 0 # это смещение предыдущей строки
    current_line = 0
    a = []
    for i in new:
        position = i[0] # узнаём, на сколько пробелов смещена строка
        if position > previous_line:
            current_line += 1 # это ПОРЯДОК текущей
        elif position == previous_line:
            pass
        else:
            current_line -= 1
        tup = (current_line, i[1])
        a.append(tup)
        previous_line = position
    return a


# ЭТУ И СЛЕДУЮЩУЮ ФУНКЦИИ НАДО РЕДАКТИРОВАТЬ ПАРАЛЛЕЛЬНО
def import_recognizer(ar): # помогает повырезать информацию о том, какие модули импортировались в файл и где
    dic_of_imports = {} # сюда мы соберем информацию о том, что куда импортировано
    for i in range(len(ar)):
        m = re.search(u'^\\s*import\\s+(.*)$', ar[i], flags = re.U|re.I)
        if m != None:
            parsing_parts = m.group(1).split(u',') # отделяем список импортированных модулей
            tempP = []
            for i1 in parsing_parts:
                m2 = re.search(u'[^ ]+\\s+as\\s+([^ ]+$)', i1, flags = re.I) 
                if m2 != None:
                    tempP.append(m2.group(1))
                else:
                    tempP.append(i1)
            parsing_parts = [j.strip() for j in tempP] # выделяем из строки список выделенных модулей
            dic_of_imports[i] = parsing_parts
    return dic_of_imports


def import_deleter(array):
    a = []
    for line in array:
        if re.search(u'^\\s*import\\s+.*$', line, flags = re.U|re.I) == None:
            ### напрашивается вывод, что это регулярное выражение должно быть где-то отдельно задано,
            ### раз уж оно используется в двух разных функциях.
            if re.search(u'^\\s*from\\s+.*$', line, flags = re.U|re.I) == None: # просто игнорируем!
                a.append(line)
    return a

# ------------------------------------------------------
# Функция рассчитана на полностью обработанный массив строк,
# полученный посредством работы функции depth_definer().
# Возвращает список номеров строк, 
# в которых есть одна инструкция на одной строке с циклом или условным оператором.
def inappr_syntax_checker(array):
    lines = array
    ### это Вы думаете, что теперь lines и array -- два разных массива?
    ### если да, то как бы не так: на самом деле копируется указатель,
    ### если говорить в терминах C++. :) Чтобы скопировать сам массив,
    ### нужно написать lines = array[:]. Или Вам не для этого нужно это присваивание?
    ### Replied: не думаю! :) Мало того, это нафиг не нужно. Но там когда-то была какая-то путаница с
    ### переменными, и я это сделала, кажется, чтобы перестать ее терять (можно и убрать)
    a = []
    counter = 0
    for line in lines: 
        m = re.search(u'^(for|while|(?:el)?if|else).*:(.+)$', line, flags = re.I|re.U) # line1 - строка
        if m != None:
                if re.search(u'\\w', m.group(2),  flags = re.I|re.U) != None:
                    a.append(counter)
        counter += 1
    return a

def inappr_syntax_editor(furtherInstance):
    depth = furtherInstance.nums    # сюда мы выделили информацию о глубине
    lines = furtherInstance.lines   # а сюда - сами строки
    if inappr_syntax_checker(lines) != []:  # проверяем файл на наличие проблем
        newdepth = []
        newlines = []
        correction = inappr_syntax_checker(lines)
        for i in range(len(lines)):
            if i in correction:
                m = re.search(u'^((?:for|while|(?:el)?if|else).*:)(.+)$', lines[i], flags = re.I|re.U)
                ### Я бы поставил здесь .*? от греха подальше.
                ### И опять же: не стоит одно и то же выражение использовать порознь
                ### в двух разных функциях. Может, файл какой создать вообще для них?
                newdepth.append(depth[i])
                newdepth.append(depth[i] + 1)
                newlines.append(m.group(1))
                newlines.append(m.group(2))
            else:
               newdepth.append(depth[i])
               newlines.append(lines[i])
        furtherInstance.nums = newdepth     # изменяем содержимое переданного экземпляра
        furtherInstance.lines = newlines

# Необходимо тестировать (не перепроверенная копипаста)
def comparison_normalizer(furtherInstance):
    depth = furtherInstance.nums    # сюда мы выделили информацию о глубине
    lines = furtherInstance.lines   # а сюда - сами строки
    new_array = []
    for line in lines:
        lefttoright = len(re.findall(u'<((?:commonvar|func|metaline|emptyline|variable)\\d*)>', line, flags = re.U|re.I))
        # посчитали 
        right = len(re.findall(u'<', line, flags = re.U|re.I)) # смотрим число закрывающих скобок
        if lefttoright < right: # есть знак "меньше"
            line = re.sub(u'<((?:commonvar|func|metaline|emptyline|variable)\\d*)>', u'{\\1}', line, flags = re.I|re.U)
            m = re.search(u'(^(?:while|(?:el)?if)\\s+)([^ ]+)\\s*(<=?)\\s*([^ ]+)(.*)$', line, flags = re.I|re.U) 
            if m != None:
                line = m.group(1) + m.group(4) + u' ' + m.group(3).replace(u'<', u'>') + u' ' + m.group(2) + m.group(5)
                line = line.replace(u'{', u'<')
                line = line.replace(u'}', u'>')
        new_array.append(line)
    furtherInstance.lines = new_array
    furtherInstance.depth  = depth
#    return [depth, new_array]
    
def bad_comment_analyser(array_of_sets):
    ident = []
    # аргументом функции является массив множеств
    for i in range(len(array_of_sets)):
        array_of_sets[i] = list(array_of_sets[i]) # сделали массив
        array_of_sets[i] = set([re.sub(u'\\s+', u'', c, flags = re.I|re.U) for c in array_of_sets[i]])
        for j in range(i + 1, len(array_of_sets)):
            array_of_sets[j] = list(array_of_sets[j])
            array_of_sets[j] = set([re.sub(u'\\s+', u'', c, flags = re.I|re.U) for c in array_of_sets[j]])
            as1 = set([i1 for i1 in array_of_sets[i] if u'coding' not in i1])
            as2 = set([i2 for i2 in array_of_sets[j] if u'coding' not in i2])
            if len(as1 & as2) > 0:
               # print array_of_sets[i]
                #print array_of_sets[j]
                tup = (i, j)
                ident.append(tup)
            else:
                for c1 in array_of_sets[i]:
                    for c2 in array_of_sets[j]:
                        if re.search(re.escape(c1), c2, flags = re.I|re.U) != None or re.search(re.escape(c2), c1, flags = re.I|re.U) != None:
                            # эта проверка на случай того, что где-то нашлись похожие комментарии
 #                           print c2
#                            print c1
#                            print u'-------'
                            tup = (i, j)
                            ident.append(tup)
                            break
    if ident != []:
        #for i in ident:
#            print i
        return list(set(ident))
    else:
        return None

def string_normalizer(furtherInstance):
    # возвращаем массив строк
    strings = []
    array_of_strings = furtherInstance.getcode()
    r1 = u'u?"(?:\\\\(?:\\\\\\\\)*"|[^"])*"'  # составляем регулярное выражение,
    r2 = u"u?'(?:\\\\(?:\\\\\\\\)*'|[^'])*'"  # адекватно находящее все
    re_full = r1 + u'|' + r2                # строки
    ### ААААА! Сколько здесь бэкслэшей! Я ничего не понимаю!
    ### Кажется, пришла пора рассказать Вам правду про r"..." / ur"...": http://docs.python.org/2/library/re.html
    ### Replied: про неформатированные строки я читала (вот сейчас сижу без интернета, а знаю, о чем Ваша ссылка),
    ### но так как это оказалось актуально лишь для части  строки-выражения, я не стала пытаться сделать так.
    ### P.S. Это место давайте считать пока магией, я сама уже не помню, как оно работает.
    for i in range(len(array_of_strings)):
        s = re.findall(re_full, array_of_strings[i], flags = re.U|re.I)
        if re.search(u're\\.(match|sub|search|findall)', array_of_strings[i], flags = re.U) != None:
            s = [u'SEARCH' + i for i in s]
        strings += s # что бы то ни было, прибавляем массив к массиву
    strings = list(set(strings))
    for i in range(len(strings)):
        strings[i] = re.escape(strings[i])
    return relevant_line_finder(strings)


def relevant_line_finder(array_of_regexps):
    samples = ['r', 'w', 'a',       # в отдельный массив выписаны регекспы, не интересующие нас при анализе регекспом
               'utf-8', 'cp1251',
               'cp1252']
    return [i for i in array_of_regexps if i.strip('\'u') not in samples]


# Функция принимает на вход массив строк
def loop_vars(array):
    v = []
    for i in array: # для переменных в циклах for
        m = re.search(u'^\\s*for\\s+(.+?)\\s+in', i, flags = re.I|re.U)
        if m != None:
            v.append(m.group(1))
    v = list(set(v))
    return v

def def_vars(array):
    # находит агрументы - переменные в названии функции
    v = []
    for i in array:
        m = re.search(u'def\\s+.+?\\((.*?)\\)', i, flags = re.I|re.U)
        if m != None:
            temp = m.group(1).split(u',')
            temp = [i.strip() for i in temp]
            for j in temp:
                if u'=' not in j:
                    v.append(j)
                else:
                    m1 = re.search(u'([^ ]+)\\s=', j, flags = re.I|re.U)
                    if m1 != None:
                        v.append(m1.group(1))
    return v
            

def variables(array_of_lines):
    variables = []
    for i in array_of_lines:
        # аргументы по умолчанию же не проходят 
        m = re.search(u'(?:^\\s+|^)([^= ]+)[\\s ]*=[^=]', i, flags = re.U|re.I)
        if m != None:
                variables.append(m.group(1).strip(u' '))
    return list(set(variables))

# МАГИЯ, НЕ ТРОГАТЬ
def var_name_definer(all_vars, start_point = 0): # поступает список переменных
    dic = {}
    v = all_vars
    for i in range(len(v)):
        new_title = u'<variable' + unicode(i + start_point) + u'>'
        dic[v[i]] = new_title
    return dic # возвращает словарь, в котором каждой переменной соответствует ее шифровка


def variable_renamer(cleartext_array, v = [], start_point = 0):
    # На вход в функцию подается: массив строк программы,
    # список всех переменных, за исключением тех, что использовались в циклах,
    # и количество переменных, использованных в циклах.
    a = []
    var = var_name_definer(v, start_point)  # Делаем словарь, какие названия на какие переименовывать.
    # Вторым параметром передаем количество уже переименованных в циклах переменных.
##    counter = len(var) + start_point        # смотрим, откуда начинаем добавлять переменные
##    for i in v:
##        if i not in var.keys():
##            var[i] = u'<variable' + unicode(counter) + u'>'
##            counter += 1
    for i in cleartext_array:
        if "'" not in i and '"' not in i:
            for j in var.keys():
                reg = u'(^|[^\\w])' + re.escape(j) + u'([^\\w]|$)' # тут всё очень плохо
                new = u'\\1' + var[j] + u'\\2'
                i = re.sub(reg, new, i, flags = re.I|re.U)
        else:
            for j in var.keys():
                try:
                    testReg = u'^[^\'"]*((?:"|\')[^\'"]*((?:(?:"|\')[^\'"]*){2})*)' + j
                                    # одиночная     # две группы
                                    # группа
                    tR = re.search(testReg, i, flags = re.I|re.U)
                except:
                    print 'PyHwLib, Ln485: RegexpError'
                    tR = None
                tr2 = u'^' + j
                if tR == None: # типа гарантия того, что это не кусок строки
                    reg = u'(^|[^\\w])' + re.escape(j) + u'([^\\w]|$)' # тут всё очень плохо
                    new = u'\\1' + var[j] + u'\\2'
                    i = re.sub(reg, new, i, flags = re.I|re.U)
                else:
                    if re.search(tr2, i, flags = re.I|re.U) != None: # типа гарантия того, что это не кусок строки
                        reg = u'(^|[^\\w])' + re.escape(j) + u'([^\\w]|$)' # тут всё очень плохо
                        new = u'\\1' + var[j] + u'\\2'
                        i = re.sub(reg, new, i, flags = re.I|re.U)
##                    else:
##                        print 'Not changed',
##                        print i
        a.append(i)
##    for i in a:
##        print i
##    print u'--------'
    return (a, var)

# ------------------------------------------------------

#CommentAwayTest(u'/Users/marina/Dropbox/PD Copy/CheckLib.py')
