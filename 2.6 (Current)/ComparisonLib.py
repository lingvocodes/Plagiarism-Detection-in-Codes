import xml.dom.minidom, codecs
from xml.dom.minidom import parseString, parse
import re, sys


def readxml(whattodo = False, material = None):
# Считываем вспомогательный файл, содержащий данные для построения внутренне используемых регулярных выражений, и переводим 
# всё его части в форму кортежей из двух элементов, первый из которых — строка, второй — уточнение (лево/право).
# Cохраняем результат на протяжении всего времени работы главной функции модуля.
    if whattodo == False or material == None:
        f = codecs.open('var_act.xml', 'r', 'utf-8-sig').read()
        doc = parseString(f) # сделали дерево
        info_pairs = []
        for node in doc.getElementsByTagName('actiontype'):     # перебираем все возможные регекспы
            site = node.attributes['site'].value    # тут хранится положение - "left" или "right"
            reg = node.childNodes[0].nodeValue      # а сюда сохраняем само выражение,
            if 'compar' in reg:
                reg.replace('compar', '<')
            compared = node.attributes['compared'].value    # плюс возможность сравнения.
            tup = (reg, site, compared)
            info_pairs.append(tup)
        return info_pairs
        if whattodo == True and material == None:
            print 'Epic Fail'
    else:
        return dynamic_contexts(material)


class context:  # один класс-один контекст
    def __init__(self, context_line, side, args = None):
        self.string = context_line # Сам вырезанный кусочек-контекст
        self.side = side           # Лево/право
        self.args = args           # если это функция, то сколько в ней аргументов?
    def generate(self, name_of_variable):
##        if self.args != None:
##            print self.args
        # Аргументом является название переменной, которое необходимо встроить в регулярное выражение
        if self.args == None or self.args < 2:
            # Если проблем с аргументами нет, строим регулярное выражение по старой схеме
            if self.side == 'left':     # То есть просто соединяем кусочки в правильном порядке
                regexp = self.string + name_of_variable
            else:
                regexp = name_of_variable + self.string
 #           print regexp
            return [regexp]     # А возвращаем в любом случае массив
        else:
            array = []
            for i in range(self.args): # тогда будет столько выражений, сколько аргументов
                if self.side == 'left':  # тяжелый случай
                    temp = u'.*?,?' # что угодно и запятая
                    regexp = self.string + temp * i + name_of_variable
                else:
                    regexp = name_of_variable + self.string
                #print regexp
                array.append(regexp)
            return array
    def identify(self):     
        line = self.string + self.side + unicode(self.args)
        return line


def dynamic_contexts(objects):
    contexts = []
    check_array = []
    regexp_left = u'(?:\\{|<)variable\\d*(?:\\}|>)(\\.\\w+|[^\\w^\\,\\{<>]+|\\]|\\))'
    for i in objects:
        code = i.getcode()
        for j in code:
            j = j.replace(u' ', u'')
            m = re.search(regexp_left, j, flags = re.U)
            if m != None:
                tup = context(re.escape(m.group(1)), u'right')
                temp01 = tup.identify()
                if temp01 not in check_array:
                    contexts.append(tup)
                    check_array.append(temp01)
#    regexp_right = u'(\\w+\\(|[^\\w\\s\\}<>])(?:\\{|<)variable\\d*(?:\\}|>)'
 #   regexp_right_1 = u'(?:[^\\w]|^)(\\w+\\()(.*?\\))(?:\\{|<)variable\\d*(?:\\}|>)'
    regexp_right = u'([^\\w\\s\\}<>])(?:\\{|<)variable\\d*(?:\\}|>)' # Вариант для выражения - не функции
    regexp_right_1 = u'(?:[^\\w]|^)(\\w+\\()(.*?\\))'
    for i in objects:
        code = i.getcode()
        for j in code:
            j = j.replace(u' ', u'')
            m = re.search(regexp_right, j, flags = re.U)
            if m != None:
                tup = context(re.escape(m.group(1)), u'left')
                temp01 = tup.identify()
                if temp01 not in check_array:
                    contexts.append(tup)
                    check_array.append(temp01)
            else:
                #print regexp_right_1
                m = re.search(regexp_right_1, j, flags = re.U)
                if m != None:
                    #print m.group(1)
                    args = m.group(2).strip(u'()')   # Аргументы, очищенные от скобок
                    if args != u'':
                        parts = args.split(u',') # разбиваем по запятым
                        if len(parts) > 0:
                            tup = context(re.escape(m.group(1)), u'left', len(parts))
                        else:
                            tup = context(re.escape(m.group(1)), u'left')
                    temp01 = tup.identify()
                    if temp01 not in check_array:
                        contexts.append(tup)
                        check_array.append(temp01)                   
    return contexts
                

def create_regexps(name_of_variable, pieces):

    templates = []

    res = []
    kostyl = []
    for i in pieces:
##        if i[1] == 'left':
##            regexp = i[0] + name_of_variable
##        else:
##            regexp = name_of_variable + i[0]
        regexps = i.generate(name_of_variable)
        res += regexps
        kostyl.append(0)    # Я не знаю, что это и что оно тут делает, но убирать страшно

    res += templates
    return [res, kostyl]


def form(objects, DEF_P = 1, reading_setting = False):
    pieces = readxml(reading_setting, objects)
# Перебираем все объекты в InnerVariableStorage_instance.objects и извлекаем из каждого объекта массив variables.
# Обращаясь к переменной, полученной в п.2, строим для каждой переменной объекта набор регулярных выражений, попутно пронумерованных
# (выражения, различающиеся только названием переменной, — под одним номером).
    shortened_obj_list = []

    stop_words = u'^(print|return|yield)'  # Это для проверки строк на предмет их выведения на экран/
                                                    # вывода в качестве результата
    previous = None

    if DEF_P == 1:
        try:           
            for i in objects:
                x = re.search(u'^def\\s.+\\((.*)\\)', i.getcode()[0], flags = re.U)
                if x != None:   # Если это всё-таки функция
                     allcode = i.getcode()[1:]  # Выделяем "годную" часть
                     alldepth = i.getdepth()[1:]
                     alldepth = [c - 1 for c in alldepth]
                     var = x.group(1).split(u',')
                     for j in var:
                         if u'=' not in j:
                             addition = j + u'=-100500'
                         else:
                             addition = j
                         allcode = [addition] + allcode
                         alldepth = [i.getdepth()[0]] + alldepth
                     if len(allcode) == len(alldepth):
                         i.lines = allcode
                         i.nums = alldepth
        except:
            pass
    templates = [u'<whileloop>', u'<ifcheck>', u'<elifcheck>', u'<elsecheck>']
    for i in objects:
        obj_info = []
        varlist = i.varnames
        loops = i.loopnum
        for j in range(len(varlist) + loops):
            r = create_regexps(u'<variable' + unicode(j) + u'>', pieces)
            regexps = r[0] + templates
            kostyl = r[1]
            a = []
            # Костыльно-ориентированное программирование
            for c1 in range(len(i.getcode())):
                search_line = i.getcode()[c1].replace(u' ', u'')
                search_line = re.sub(u'{([^}])', u'<\\1', search_line, flags = re.U)
                search_line = re.sub(u'([^{])}', u'\\1>', search_line, flags = re.U)
                for c2 in range(len(regexps)):
                    if regexps[c2] not in templates:
                        if re.search(regexps[c2], search_line, flags = re.U) != None:
                            if previous == 'yes':
                                if re.search(stop_words, search_line, flags = re.U) != None:
                                    tup = (c2, i.getdepth()[c1])#, kostyl[c2], True)
                                else:
                                    tup = (c2, i.getdepth()[c1])#, kostyl[c2], False)
                            else:
                                tup = (c2, i.getdepth()[c1])#, kostyl[c2], False)
                            a.append(tup)
 #                           previous = kostyl[c2]
                                          
            obj_info.append(a)
        shortened_obj_list.append(obj_info)
    return shortened_obj_list


def max_depth(array):
    # Входные данные - массив массивов кортежей, ищем - максимальную глубину
    m = 0
    for j in array: # перебираем массивы кортежей
        for i in j:
                if i[1] > m:
                    m = i[1]
    return m


def make_set_of_strings(array_of_arrays_of_tuples, stop_num = None):
    a = set()
    for array in array_of_arrays_of_tuples:
        line = u''
        for i in array:
            if stop_num == None or i[1] < stop_num: # по умолчанию stop_num нет. Не по умолчанию - всё,
                # что глубже stop_num, срезается
                line += (unicode(i[0]) + unicode(i[1]))
        a.add(line)
    return a # возвращаем множество полностью свернутых строк


    # Тупенькая внутренняя функция, проверяющая входящие наборы и говорящая да или нет
def inner_comp(x, y, xDepth = None, yDepth = None):
    common = make_set_of_strings(x, xDepth) & make_set_of_strings(y, yDepth)
    if common == make_set_of_strings(y, yDepth) and common == make_set_of_strings(x, xDepth):
        return True
    else:
        return False


stop_num = 6 # если поставить больше, будете ждать результатов вечность даже              

       
def compare(x, y):
    xMax = max_depth(x)
    yMax = max_depth(y)
    c = inner_comp(x, y)
    signature = False
    if c == True and type(c) == bool:
 #       print True
        return True ### ПОЛНОЕ СОВРАДЕНИЕ
    else:
        while xMax >= 0 and yMax >= 0:    #  Начинаем "выбивать" глубины
            temptemp = inner_comp(x, y, xMax, yMax)
            if temptemp == True and type(temptemp) == bool:
                if xMax == 0:
                    if max_depth(x) < 2:
                        return xMax
                    else:
                        return False ### Обозначение нуля
                else:
                    return xMax ### Частичное, глубина больше 0

                break
            else:
                if xMax > yMax:
                    xMax -= 1
                else:
                    yMax -= 1
                    xMax -= 1
        else:
            return None ### просто ничего не нашлось


def delete_peaks(objects):
    array = []
    for i in objects:
        tempCode = i.getcode()      # код
        tempDepth = i.getdepth()    # глубина
        prev = 0
        newCode = []
        newDepth = []
        for j in range(len(tempDepth)):  # анализируем исключительно глубины
            if tempDepth[j] >= prev: # если не удовлетворяет этому условию, точно не пик
                for c in range(j + 1, len(tempDepth)):   # теперь проверяем, что идет дальше
                    if tempDepth[c] > tempDepth[j]:     # если получилось, что больше, то
                        newCode.append(tempCode[j])     # строка не пиковая, и мы ее оставляем
                        newDepth.append(tempDepth[j])   # и номер оставляем тоже
##                        print tempCode[j]
                        break                           # сразу выходим из перебора!
                    elif tempDepth[c] < tempDepth[j]:   # а вот если меньше, то ничего не делать, просто выйти,
                                                        # потому что это был пик
##                        print 'Deleted:',
##                        print tempCode[j]
                        break
                    # если же всё равно, то продолжаем цикл до конца
                else:
                    pass
##                        print 'Deleted after:',
##                        print tempCode[j]
                    
            else:
                newCode.append(tempCode[j])     # строка не пиковая, и мы ее оставляем
                newDepth.append(tempDepth[j])   # и номер оставляем тоже
##                print tempCode[j]
            prev = tempDepth[j]
        i.change_text(newCode, newDepth)
        array.append(i)
##        print ''
##        for xxx in i.getcode():
##            print xxx
##        print '\n'
    return array


def commonize(objects):
    new_array = []
    for i in objects:
        new_lines = []
        for j in i.getcode():   # перебираем строки
            if re.search(u'^while', j, flags = re.I|re.U) != None:
                new_lines.append(u'<whileloop>')
            elif re.search(u'^if', j, flags = re.I|re.U) != None:
                new_lines.append(u'<ifcheck>')
            elif re.search(u'^elif', j, flags = re.I|re.U) != None:
                new_lines.append(u'<elifcheck>')
            elif re.search(u'^else:', j, flags = re.I|re.U) != None:
                new_lines.append(u'<elsecheck>')
            else:
                new_lines.append(j)
        i.lines = new_lines
        new_array.append(i)
    return new_array


class StatDic:
    def __init__(self, IVS_instance, full_length_source = None):
        # Необязательным аргументом может быть IVS_instance, не усеченный (не модификация)
        code = IVS_instance.getcode()
        depth = IVS_instance.getdepth()
        dic = {}
        d = {}
        cc = 0
        for i in range(len(depth)):
            if depth[i] not in dic:
                dic[depth[i]] = 1
            else:
                dic[depth[i]] += 1
            if re.search(u'whileloop>|<(?:el)?(?:if|se)check>', code[i], flags = re.U) == None:
                # Вторая часть - с выкинутыми сравнениями
                cc += 1
                if depth[i] not in d:
                    d[depth[i]] = 1
                else:
                    d[depth[i]] += 1
        self.dic_without_commonization = dic
        self.dic_with_commonization = d
        self.num_of_lines_commonized = cc
        if full_length_source == None:
            self.all_lines = len(code)
            self.cut = False # не урезано
        else:
            temp = full_length_source.getcode()
            self.all_lines = len(temp)
            self.cut = True # урезано
    def percent(self, Depth, commonization_off = True):
        if self.all_lines == 0:
 #           print 'FAIL'
            return 0.0
#        print 'not fail'
        depth = Depth
        if Depth == False and type(Depth) == bool:
            depth = 0

        num_of_lines = 0    # Столько строк в этом самом урезанном варианте
        for c in self.dic_without_commonization.values():
            num_of_lines += c

        if depth == True and type(depth) == bool:   # Что-то где-то полностью совпало, осталось понять, что
            if commonization_off == True:
                if self.cut == False:
                    return 1.0              # вернули 100%
                else:
                    return float(num_of_lines) / self.all_lines 
            else:
                # Совпало всё то, что не в сравнениях.
                return float(self.num_of_lines_commonized) / self.all_lines
        elif depth == None:
            return 0.0              # изначально не нашлось свойств
        else:
            # глубина - это число
            if type(depth) == int:
                lines_not_deleted = 0
                if commonization_off == True: # значит, убирать строки-сравнения не надо
                    for i in self.dic_without_commonization.keys(): # перебираем ключи - номера
                        #if type(depth) == int:
                            if i <= depth:      # если строки уцелели...
                                lines_not_deleted += self.dic_without_commonization[i] # плюсуем количество таких строк
                    return float(lines_not_deleted) / self.all_lines
                else:
                    for i in self.dic_with_commonization.keys(): # перебираем ключи - номера
                        if i <= depth:      # если строки уцелели...
                            lines_not_deleted += self.dic_with_commonization[i] # плюсуем количество таких строк
                    return float(lines_not_deleted) / self.all_lines
            else:
                print u'Произошел сбой в подсчете статистики'
                return 0.0
    def part(self, Depth, commonization_off = True):
        if self.all_lines == 0:
            return 0.0
        depth = Depth
        if Depth == False and type(Depth) == bool:
            depth = 0
        num_of_lines = 0    # Столько строк в этом самом урезанном варианте
        for c in self.dic_without_commonization.values():
            num_of_lines += c

        if depth == True and type(depth) == bool:   # Что-то где-то полностью совпало, осталось понять, что
            if commonization_off == True:
               # if self.cut == False:
 #                   return 1.0              # вернули 100%
 #               else:
                    return float(num_of_lines) #/ self.all_lines 
            else:
                # Совпало всё то, что не в сравнениях.
                return float(self.num_of_lines_commonized) #/ self.all_lines
        elif depth == None:
            return 0.0              # изначально не нашлось свойств
        else:
            # глубина - это число
            if type(depth) == int:
                lines_not_deleted = 0
                if commonization_off == True: # значит, убирать строки-сравнения не надо
                    for i in self.dic_without_commonization.keys(): # перебираем ключи - номера
                        #if type(depth) == int:
                            if i <= depth:      # если строки уцелели...
                                lines_not_deleted += self.dic_without_commonization[i] # плюсуем количество таких строк
                    return float(lines_not_deleted) #/ self.all_lines
                else:
                    for i in self.dic_with_commonization.keys(): # перебираем ключи - номера
                        if i <= depth:      # если строки уцелели...
                            lines_not_deleted += self.dic_with_commonization[i] # плюсуем количество таких строк
                    return float(lines_not_deleted) #/ self.all_lines
            else:
                print u'Произошел сбой в подсчете статистики'
                return 0.0
            
            

def create_stat_objects(IVS_objects, full_variants = None):
    array = []
    for i in range(len(IVS_objects)):
        if full_variants == None: # не урезан
            x = StatDic(IVS_objects[i])
        else:
            x = StatDic(IVS_objects[i], full_variants[i])           
        array.append(x)
    return array


class Container:
    def __init__(self, num1, num2, percent1, percent2):
        if num1 < num2:
            self.pair = (num1, num2)    # Пара идентификаторов
            self.p1 = percent1          # Процент типа неоригинального кода в первом файле
            self.p2 = percent2          # Процент типа неоригинального кода во втором файле
        else:
            self.pair = (num2, num1)    # Пара идентификаторов
            self.p1 = percent2          # Процент типа неоригинального кода в первом файле
            self.p2 = percent1          # Процент типа неоригинального кода во втором файле            
    def get_1(self):
        return self.pair[0]
    def get_2(self):
        return self.pair[1]
    def get_pair(self):
        return self.pair
    def percent_1(self):
        return self.p1
    def percent_2(self):
        return self.p2


class FullStat:
    def __init__(self, objects, modifications):
        self.full = create_stat_objects(objects)   # рассчитали всю статистику для не урезанных delete_peaks() файлов
        self.not_full = create_stat_objects(modifications, objects) # и для урезанных
    def get(self, num, result_of_calc, commonization_off, peaks_deleted_or_not):
        # первый аргумент - просто результат из compare,
        # второй — true/false - были ли при этом обобщены сравнения,
        # третий - true/false - удалялись ли пики.
        if peaks_deleted_or_not == True:    # Пики были удалены
            activedic = self.not_full[num]
        else:                               # Не были удалены
            activedic = self.full[num]
        return activedic.part(result_of_calc, commonization_off)
    def get_percent(self, num, result_of_calc, commonization_off, peaks_deleted_or_not):
        # первый аргумент - просто результат из compare,
        # второй — true/false - были ли при этом обобщены сравнения,
        # третий - true/false - удалялись ли пики.
        if peaks_deleted_or_not == True:    # Пики были удалены
            activedic = self.not_full[num]
        else:                               # Не были удалены
            activedic = self.full[num]
        return activedic.percent(result_of_calc, commonization_off)
    
    
class s:
    def __init__(self, IVS_objects_arr):
        filter_dic = {}
        # Соответствия: номер кусочка — номер файла
        size_dic = {}
        for i in range(len(IVS_objects_arr)):
            ID = IVS_objects_arr[i].getid()
            if i not in filter_dic:
                filter_dic[i] = ID
            if ID not in size_dic:
                size_dic[ID] = 1
            else:
                size_dic[ID] += 1
                
        self.filter = filter_dic
        self.sizes = size_dic
        self.array = {}     # Класс включает словарик, в котором обозначено,
                            # к какому исходному файлу относится каждый из кусочков
        self.codes = []     # Вспомогательная ересь
    def append(self, cont):
        if cont.p1 != 0 and cont.p2 != 0: # всё нулевое срезаем.
            #if cont.pair not in self.codes: # Проверяем, нет ли уже такой пары кусочков
            # Ликвидировано, потому что иначе нафига нужна arrange()
                temp = (self.filter[cont.pair[0]], self.filter[cont.pair[1]])
                self.codes.append(cont.pair)
                if temp not in self.array:
                    self.array[temp] = []
                self.array[temp].append(cont)
    def arrange(self):
        # Работаем с каждым из словариков в массиве self.array.
        # каждый из словариков проверяем на наличие лишних кусочков;
        # если есть лишние, осуществляем фильтрацию.
        # Если после фильтрации чего-то нехватает, то дополняем
        # пустыми контейнерами.
        new_array = {}
        for i in self.array.keys(): # перебираем массивы контейнеров по их именам,
            temp_cont_array = {}    # это словарь сортировки:
            inner_cont_array = []
                                    # ключ - первое число пары,
                                    # значение - массив со всеми контейнерами
                                    # с таким первым значением
            for j in self.array[i]: # перебираем контейнеры в массивах.
                x = j.get_1()       # получаем ключ для временного массива
                if x not in temp_cont_array:
                    temp_cont_array[x] = []
                temp_cont_array[x].append(j)
            # здесь мы получили массив словарей,
            # каждый из словарей соответствует одной части ПЕРВОГО файла.
            # теперь из каждого словаря надо выбрать самое большое значение пары.
            for j in temp_cont_array.keys(): # Cooтветственно, перебираем пары.
                maximum = 0.0
                max_cont = None
                for c in temp_cont_array[j]:
                    contr_num = c.percent_1()
                    if contr_num > maximum:
                        maximum = contr_num
                        max_cont = c
                # в конце этого цикла max_cont - максимальный контейнер.
                if max_cont != None:
                    inner_cont_array.append(max_cont)
            # Тут необходимо пересохранить куда надо inner_cont_array
            reallen1 = self.sizes[i[0]] # Выяснили, сколько фрагментов в каждом из файлов
            reallen2 = self.sizes[i[1]]
            if len(inner_cont_array) < reallen1 or len(inner_cont_array) < reallen2:
                res1 = reallen1 - len(inner_cont_array)
                res2 = reallen2 - len(inner_cont_array)
                if res1 > res2: # планы по созданию доп. кусочков
                    in_common = res2
                    only1 = res1 - res2
                    only2 = 0
                else:
                    in_common = res1
                    only1 = 0
                    only2 = res1 - res2
                random_num1 = None
                random_num2 = None
                for ttt in self.filter.keys():
                    if self.filter[ttt] == i[0]:
                        random_num1 = ttt
                    if self.filter[ttt] == i[1]:
                        random_num2 = ttt
                if random_num1 != None and random_num2 != None:
                    donate_pair = (random_num1, random_num2)
                    for i in range(in_common):
                        tc = Container(random_num1, random_num2, 0.0, 0.0)
                        inner_cont_array.append(tc)
                    for i in range(only1):
                        tc = Container(random_num1, random_num2, 0.0, None)
                        inner_cont_array.append(tc)
                    for i in range(only2):
                        tc = Container(random_num1, random_num2, None, 0.0)
                        inner_cont_array.append(tc)
            new_array[i] = inner_cont_array
        # На этом этапе имеем доделанный self.array
        self.array = new_array
                
    def get(self):
        real_arr = []
        for i in self.array.keys():
            real_arr += self.array[i]
        return real_arr
    
def Main(InnerVariableStorage_instance):
    # Из внешнего модуля получаем объект класса InnerVariableStorage и извлекаем из него переменную objects:
    # InnerVariableStorage_instance.objects
    objects = InnerVariableStorage_instance.objects

    stat_array = create_stat_objects(commonize(objects))
        
# Считываем вспомогательный файл, содержащий данные для построения внутренне используемых регулярных выражений, и переводим 
# всё его части в форму кортежей из двух элементов, первый из которых — строка, второй — уточнение (лево/право).
# Cохраняем результат на протяжении всего времени работы главной функции модуля.
    x = form(objects, InnerVariableStorage_instance.settings['DEFS'], InnerVariableStorage_instance.settings['GENERATECONTEXTS'])
    modifications = delete_peaks(objects)
    x2 = form(modifications, InnerVariableStorage_instance.settings['DEFS'], InnerVariableStorage_instance.settings['GENERATECONTEXTS'])
    x3 = form(commonize(objects), InnerVariableStorage_instance.settings['DEFS'], InnerVariableStorage_instance.settings['GENERATECONTEXTS'])
    x4 = form(commonize(modifications), InnerVariableStorage_instance.settings['DEFS'], InnerVariableStorage_instance.settings['GENERATECONTEXTS'])

##    similarity_grade = create_stat_objects(objects)   # рассчитали всю статистику для не урезанных delete_peaks() файлов
##    semilarity_grade_1 = create_stat_objects(modifications, objects) # и для урезанных
    similarity_grade = FullStat(objects, modifications)
    similarity = s(objects)

    for i in range(len(x) - 1):     # перебираем получившиеся структуры.
        for j in range(i + 1, len(x)):
            RES = compare(x[i], x[j])
            cont = None
            if RES == True and type(RES) == bool:     # Не может быть никаких вопросов. Полное совпадение.
                s1 = similarity_grade.get(i, RES, True, False)
                s2 = similarity_grade.get(j, RES, True, False)
                cont = Container(i, j, s1, s2)
 #               print 'Yeah'
 #               similarity.append(cont)
            else: # Не повезло
                R2 = compare(x3[i], x3[j]) # Проверяем не усеченные файлы, но обобщаем сравнения
                if R2 != None:              #  Если минимально прокатило, то
                    if type(RES) == int or RES == False: # если находилось хоть что-то...
                        s1_p = similarity_grade.get(i, R2, False, False)     # Смотрим процент совпадения
                        s2_p = similarity_grade.get(j, R2, False, False)
                        sp_common = (s1_p + s2_p) / 2
                        s1_f = similarity_grade.get(i, RES, True, False)     # Смотрим процент совпадения
                        s2_f = similarity_grade.get(j, RES, True, False)
                        sf_common = (s1_f + s2_f) / 2
                        if sp_common > sf_common:
                            cont = Container(i, j, s1_p, s2_p)
                        else:
                            cont = Container(i, j, s1_f, s2_f)
                    else:
                        s1_p = similarity_grade.get(i, R2, False, False)     # Тогда без вариантов
                        s2_p = similarity_grade.get(j, R2, False, False)
                        cont = Container(i, j, s1_p, s2_p)
                else: # Если только выкидывание сравнений не помогло...
                    R3 = compare(x2[i], x2[j])
                    if R3 != None:
                        cont = Container(i, j,
                                         similarity_grade.get(i, R3, True, True),
                                         similarity_grade.get(j, R3, True, True))
                    else:
                        R4 = compare(x4[i], x4[j])
                        cont = Container(i, j,
                                         similarity_grade.get(i, R4, False, True),
                                         similarity_grade.get(j, R4, False, True))

            similarity.append(cont)
##    for i in similarity.array:
##        print i.pair
##        print i.p1,
##        print i.p2
    similarity.arrange()
    X = similarity.get()
    find_names(InnerVariableStorage_instance, X)


class inner:
    def __init__(self, percent, l):
        self.percent = percent
        self.length = l

class outer:
    def __init__(self):
        self.array = []
        self.common = 0
    def new(self, percent, obj):
##        print percent
        o = obj.getcode()
##        print o
        l = len(o)
##        if l == 0:
##            print 'NULL'
        x = inner(percent, l)
        self.array.append(x)
        self.common += l
    def stat(self):
        res = 0
 #       checksum = 0
        for i in self.array:    # Перебираем кусочки программы
##            print i.percent,
##            print self.common
            if self.common != 0:
                if i.percent != None:
                    part = i.percent / self.common
                    res += part
        return res

class progpair:
    def __init__(self, numbertup):
        self.pair = numbertup
        self.first = outer()
        self.second = outer()
    def add(self, container, objects):
        o = objects[container.pair[0]]       # выскребли объект
        self.first.new(container.p1, o)
        o = objects[container.pair[1]]       # выскребли объект
        self.second.new(container.p2, o)
    def maketup(self, file_list):
        f1 = file_list[self.pair[0]]
        f2 = file_list[self.pair[1]]
        s1 = self.first.stat()
        s2 = self.second.stat()
        tup = (f1, f2, s1, s2)
        return tup

        
def find_names(InnerVariableStorage_instance, similarity):
    # similarity - массив контейнеров
    # В similarity входят ВСЕ объекты
    
    files = InnerVariableStorage_instance.file_list     # Из этого списка мы сможем добывать истинные названия файлов
    o = InnerVariableStorage_instance.objects           # А это список всех объектов в обработке

    coefficients = {}               # cоздаем словарь для расчета коэффициентов


    for i in similarity:            # Пребираем совпадения.
        id1 = i.get_1()             # Получаем меньший...
        id2 = i.get_2()             # ... и больший id

        real_name_1 = o[id1].getid() # извлекли идентификатор из списка для первого файла
        real_name_2 = o[id2].getid() # извлекли идентификатор из списка для второго файла

        if real_name_1 < real_name_2:       # в кортеже делаем сортировку: первый элемент - всегда меньший
            # Это позволяет не думать о том, что может быть наоборот
            tup = (real_name_1, real_name_2)
        else:
            tup = (real_name_2, real_name_1)
        if i.percent_1() == 1.0 and i.percent_2() == 1.0:
            FULL = (files[real_name_1], files[real_name_2])
            InnerVariableStorage_instance.res.addpart(FULL)
        if tup not in coefficients:
            coefficients[tup] = progpair(tup)
        coefficients[tup].add(i, o)
##        if tup not in coefficients2:
##            coefficients2[tup] = i.percent_2()
##        else:
##            coefficients2[tup] += i.percent_2()
    
    fullC = 1
    partialC = 1
    for c in coefficients.values():
        Pair = c.maketup(files)
##        Pair = (files[c[0]], files[c[1]], coefficients1[c], coefficients2[c])
        if Pair[2] == 1.0 and Pair[3] == 1.0:
            InnerVariableStorage_instance.res.addfullpair(Pair)
            fullC += 1
        else:

                InnerVariableStorage_instance.res.addpartialpair(Pair)
                partialC += 1

    
                

