# в этом файле будет великая функция, которая вызывается из основного
# файла "openwindow" и открывает все файлы, после чего обрабатывает их
# и возвращает отчётность
#import VarMapping, hwhandler,
import codecs, re # импортируем модуль для работы с объектами-домашками,
# в том числе содержащий библиотеку PyHwLib
import PyHwLib as pcp, ComparisonLib as comparison # когда-то он назывался PrimaryCodeParser
from RegexpLib import comparere, re_list

def ws(line):
    return u' ' + line + u' '

def comma(line):
    return line + u', '

class Results:
    def __init__(self):
##        self.default_headlines = [u'Прочитано файлов: ',
##                             u'Не прочитаны файлы: ',
##                             u'Комментарии:\n',
##                             u'Регулярные выражения: ',
##                             u'Совпадения в коде: ']
        self.all = 0
        self.unread = []        # сюда сохраним названия несчитанных файлов (чтобы вывести в отчет,
                                # а не в уведомления об ошибке)
 #       self.commentAna = u''   # сюда впоследствии будет сохраняться результат анализа комментариев
 ##       self.regexpAna = u''    # сюда сливается уже в текстовом виде информация о том, что происходит с регекспами
 ##       self.codeAna = u''      # это текст для всего остального
        self.addresspairs_p = []
        self.addresspairs_f = []
        self.regexp_pairs = []
        # self.commentpairs = []
        self.pp = []
# Эта переменная содержит тройки:
# пару названий файлов (да, названий) и массив кодов сходства

        self.comment_pairs = []
    def addfullpair(self, pair):
        self.addresspairs_f.append(pair)
    def addpartialpair(self, pair):
        self.addresspairs_p.append(pair)
    def add_error(self, file_path): # это метод для добавления не считанного файла в список несчитанных файлов
        self.unread.append(file_path)
    def counter_increment(self):
        self.all += 1
    def add_re(self, re_code):
        self.regexp_pairs.append(re_code)
    def addcommentpair(self, address1, address2):
        tup = (address1, address2)
        self.comment_pairs.append(tup)
    def nullcomment(self):
        self.commentpairs = None
    def nullre(self):
        self.regexp_pairs = None
    def addpart(self, partpair):
        self.pp.append(partpair)
    def plaintext(self, headlines, grade_param = 0.7, difference = 0.15):
        # сохранили первый из разделов
        text = headlines.read.capitalize() + u': ' + unicode(self.all)
        text += u'\n\n'
        # про непрочитанные файлы
        if len(self.unread) == 0:
            text += (headlines.allread_msg.capitalize() + u'.\n\n')
        else:
            text += (headlines.notread.capitalize() + u':\n')
        for c in range(len(self.unread)):
            text += unicode(c+1) + u') ' + self.unread(c) + u'\n'
        text += u'\n'
        # про регулярные выражения
        text += headlines.regexps.capitalize()
#        text += u' '
        if self.regexp_pairs == None:
            text += u' '
            text += headlines.nore
            text += u'\n'
        else:
            text += u':\n'
            if len(self.regexp_pairs) != 0:
                for i in range(len(self.regexp_pairs)):
                    text += (unicode(i + 1) + u') ' + self.regexp_pairs[i][0] + ws(headlines.link) + self.regexp_pairs[i][1])
                    temp = headlines.contain + u' '
                    if 1 in self.regexp_pairs[i][2]:
                        temp += comma(headlines.r1)
                    if 2 in self.regexp_pairs[i][2]:
                        temp += comma(headlines.r2)
                    if 3 in self.regexp_pairs[i][2]:
                        temp += comma(headlines.r3)
                    if 4 in self.regexp_pairs[i][2]:
                        temp += comma(headlines.r4)
                    text += (ws(temp[:-2]) + headlines.regexps + u'.\n')
                text += u'\n'
            else:
                text += headlines.notfound
                text += u'\n\n'
# Комменты
        text += headlines.comments.capitalize()
        if self.comment_pairs == None:
            text += u' '
            text += headlines.nore
            text += u'\n'
        else:
            text += u':\n'
            if len(self.comment_pairs) == 0:
                text += headlines.nocomment
                text += u'\n\n'
            else:
                for i in range(len(self.comment_pairs)):
                    text += (unicode(i + 1) + u') '+ self.comment_pairs[i][0] + ws(headlines.link) + self.comment_pairs[i][1])
                    text += ws(headlines.contain + ws(headlines.r1) + headlines.comments)
                    text += u'\n'
            text += u'\n'
        # код
 #       print difference
        text += headlines.check.capitalize()
        text += u':'
        text += u'\n'
        counter = 1
        for i in self.addresspairs_f:
            text += (unicode(counter) + u') ' + i[0] + ws(headlines.link) + i[1]+ u' ' + headlines.full + u';\n')
            counter += 1
        text += u'\n'
       # print len(self.addresspairs_p)
        for i in self.addresspairs_p:
            if i[2] >= grade_param or i[3] >= grade_param:
                d = i[2] - i[3]
                if d < 0:
                    d = -d
                if difference == None or d <= difference:
##                    if difference == None:
##                        print 1111
                    text += (unicode(counter) + u') ' + i[0] + ws(headlines.link) + i[1]+ u' ' + headlines.partial)
                    text += u' ('
                    percent1 = unicode(i[2]*100)[:4]
                    percent2 = unicode(i[3]*100)[:4]
                    if i[2] != i[3]:
                        text += (percent1 + u'%' + ws(headlines.link) + percent2 + u'%)\n')
                    else:
                        text += (percent2 + u'%)\n')
                    counter += 1
        text = text.strip(u'\n')
        if text[-1] == u';':
            text = text[:-1]
        if counter == 1:
            text += headlines.nopl
        return text


def code_devision(PrimaryInstance): # функция занимается преобразованием информации,
    #содержащейся в классе primary, в форму, пригодную для передачи в класс futher
    ar = PrimaryInstance.getcode()
    imports = pcp.import_recognizer(ar) # список импортированных модулей с указанием строк
    in_pieces = []
    mode = 'maincode' # Исходный режим — режим основного кода.
   # print ar[0]
    #print u'++++'
##    if re.search(u'^def[^\\w]', ar[0], flags = re.I|re.U) != None:
##        mode = 'def'
    piece_of_code = []      # Заготовка для кусков кода, которые функции
    main_piece = []         # А это — для основного куска кода, который точно один
    nums_of_change = [0]    # В качестве первой точки смены признаем начало файла
    for i in range(len(ar)):# Начинаем перебор строк
##        print ar[i]
        if re.search(u'^\\s*$', ar[i], flags = re.U) == None:
            if mode == 'maincode': # если текущая часть - основной код, не код функций
                if re.search(u'^\\s*def[^\\w]', ar[i], flags = re.I|re.U) == None: # убеждаемся, что мы не переходим в режим функции
     #               if re.search()
                    main_piece.append(ar[i]) # cохраняем всё в основном блоке
                else:   # если же мы переходим к функции, то 
     #               in_pieces.append(piece_of_code)
                    piece_of_code = [] # на всякий случай обнуляем функцию
                    piece_of_code.append(ar[i]) # сохраняем в нее строку
                    mode = 'def'                # переключаем режим на функционный
                    nums_of_change.append(i)    # и фиксируем, что на этой строке режим переменился
            else:                       # если до этого мы были в режиме функции
                if re.search(u'^def[^\\w]', ar[i], flags = re.I|re.U) == None: # проверяем, не начали ли мы новую функцию
                    # если нет, то продолжаем составлять предыдущую функцию
                    if re.search(u'^[^\\s]', ar[i], flags = re.I|re.U) != None: # считаем пробелы:
 #                       print u'"' + ar[i] + u'"'
                        # если в начале они есть, то просто прибавляем к функции кусок
     #                  piece_of_code.append(ar[i])
     #               else: # а если нет, мы снова в главной части
                        in_pieces.append(piece_of_code) # cохраняем код функции
##                        print ''
##                        for sd in piece_of_code:
##                            print sd
##                        print ''
                        piece_of_code = []              # обнуляем массив под нее
                        mode = 'maincode'               # переключаем режим на основной
                        nums_of_change.append(i)        # фиксируем точку изменения
                        main_piece.append(ar[i])        # сохраняем основной код
                       # print ar[i]
                    else:
                        piece_of_code.append(ar[i])
                else:   # если начали
                    in_pieces.append(piece_of_code)
##                    for sd in piece_of_code:
##                        print sd
                    piece_of_code = []
                    piece_of_code.append(ar[i])
     #               mode = 'maincode'
                    nums_of_change.append(i)
    nums_of_change.append(len(ar) - 1)
    if mode == 'def':
        in_pieces.append(piece_of_code)         # сохранили последний кусочек кода
    in_pieces.append(main_piece)                # и приделали основной кусок
   # print in_pieces
   # print u'-------------'
    if len(nums_of_change) - 1 == len(in_pieces):   # проверяем, удастся ли переформировать части
        for i in range(len(nums_of_change) - 1):    # перебираем номера стартовых строк кусочков
            import_line = u''                       # для каждого кусочка делаем свою import_line
            for j in imports.keys():                # перебираем номера всех строк, в которых есть комментарии
                if j < nums_of_change[i + 1]:       # и если номер строки меньше, чем номер строки конца,
                    for q in imports[j]:            # перебираем соответствующие модули и 
                        import_line += (q + u'|')   # прибавляем к строчке импорта перечисленное
            in_pieces[i] = pcp.import_deleter(in_pieces[i]) # после чего удаляем все импорты из текущего текста
            in_pieces[i] = [import_line] + in_pieces[i]     # и потом приклеиваем эту строку к строчке импорта
##    new_pieces = []             # создаем новый массив, который будет содержать то, что есть в in_pieces
##    main_part = []              # для новой общей части создаем отдельный массив
##    main_import_line = u''      # и это для нового main_line
##    for i in in_pieces:         # перебираем имеющиеся
##        if len(i) > 1 and re.search(u'^def\\s', i[1], flags = re.I|re.U) != None:
##            new_pieces.append(i)
##        else:
##            main_import_line += (i[0] + u'|')
##            if len(i) > 1:
##                    main_part += i[1:]
##    main_import_line = re.sub(u'\\|+', u'|', main_import_line.strip(u'|'), flags = re.I|re.U)
##    main_part = [main_import_line] + main_part
##    new_pieces.append(main_part)
##    print '+++'
##    for i in in_pieces:
##        for j in i:
##            print j
##        print u'======='
##    for i in in_pieces:
##        for j in i:
##            print j
##        print u'========'
##    print u'!!!!!!!!!!!!!!!!!!!!!!!!'
    customf_arr = []
    for i in in_pieces:
        m = re.search(u'^def\\s*([^ ]+?)\\s*\\(', i[0], flags = re.U) 
        if m != None:
            customf_arr.append(m.group(1))
    for c in customf_arr:
        reg = u'([^\\w])' + c + u'([^\\w])'
        for i in range(len(in_pieces)):
            for j in range(len(in_pieces[i])):
                in_pieces[i][j] = re.sub(reg, u'\\1customfunc\\2', in_pieces[i][j], flags = re.U)
##    for i in in_pieces:
##        for j in i:
##            print j
##        print u'========'
##    print u'!!!!!!!!!!!!!!!!!!!!!!!!'
    return [PrimaryInstance.getid(), in_pieces]

#def DevisionTest

class InnerVariableStorage: # чтобы в основной функции mainchecker не было слишком много переменных.
    def __init__(self, setting, files):
        self.settings = setting     # всё это время мы будем хранить поступившие настройки тут (массив)
        self.file_list = files      # а список файлов для обработки - тут
        self.res = Results()        # также внутри создаем отдельный класс для вывода результатов
        self.objects = []
        #self.comments = None # типа не актуально
        if self.settings['CHECKRE'] == 0:
            self.res.nullre()
    def fill_objects(self):     # этот метод заполняет self.objects 
        for i in range(len(self.file_list)): # перебираем список путей к файлам по номерам в массиве!
                            # номера в массиве - это идентификаторы
            try:    # пытаемся прочитать файл
                self.objects.append(pcp.primary(self.file_list[i], i))  # наполняем массив первичными вариантами
                                                                    # объектов - списков строк
                self.res.counter_increment()     # и их считаем.
            except:
                self.res.add_error(self.file_list[i]) # а иначе сразу сливаем в Unread
    def primary_to_further(self):
        new_obj_array = []  # подготавливаем новое место под хранение объектов - программ
        for i in self.objects: # перебираем объекты primary
            details = code_devision(i)
            # получаем заготовку - массив вида:
            # id, кусочки-программы в массиве
            for j in details[1]: # теперь перебираем эти самые
                pack = [details[0], j]  # готовим нечто в формат для функции
                new_obj_array.append(pcp.further(pack))
        self.objects = new_obj_array
    def correct_all_2in1(self):
        if self.settings['PARSEINSTR'] == 1: # если это вообще требуется...
            for i in range(len(self.objects)): #...перебираем объекты в self.objects
                self.objects[i].correct_2in1()
    def delete_all_re(self):
        for i in range(len(self.objects)): #...перебираем объекты в self.objects
            self.objects[i].delete_regexps()
        if self.settings['CHECKRE'] == 1:
            analyse_re(self)
    def comparisons(self):
        if self.settings['DEFINESINGLECOMP'] == 1:
            for i in range(len(self.objects)):
                self.objects[i].cn()
    def lenfreqdic(self):
        dic = {}
        for i in self.objects:
            l = i.getcode()
            le = len(l)
            if le not in dic:
                dic[le] = 1
            else:
                dic[le] += 1
        import sys
        temp_out = sys.stdout
        tF = codecs.open('statistics.csv', 'w', 'utf-8')
        sys.stdout = tF
        print u'"Количество строк","Встретилось"\n'
        k = dic.keys()
        k.sort()
        for i in k:
            print unicode(i) + u',' + unicode(dic[i]) + u''
        sys.stdout = temp_out
        tF.close()
        print 'Stopped'
        

def compare_two_arrays_of_re(array1, array2):
    codes = []
    for i in array1:
        for j in array2:
            x = comparere(i, j) # Получаем код, указывающий на то, признаны ли выражения сходными
            if x != 0:
                codes.append(x)
    if codes != []:
        return codes
    else:
        return None
    

class RegexpStatistics:
    def __init__(self, codes, num1, num2):
        self.codes = codes
        self.pair = (num1, num2)
    def statistics(self):
        return self.codes
    def nums(self):
        return self.pair


def Draw(array_of_RegexpStatistics, InnerVariableStorage_instance):
 #   line = u''
    for i in range(len(array_of_RegexpStatistics)):
        indices = array_of_RegexpStatistics[i].nums()
        codes = array_of_RegexpStatistics[i].statistics()
        if 1 == 1: #in codes or 2 in codes:
 #           line += (unicode(i) + u') ')     # Делаем красивую нумерацию
            try:
                rty = InnerVariableStorage_instance.file_list[indices[0]]
                jgh = InnerVariableStorage_instance.file_list[indices[1]] 
 #               line += (unicode(i + 1) + u') ' + rty + u' и ' + jgh)
 #               line += u' и '
 #               line += InnerVariableStorage_instance.file_list[indices[1]] # дописываем вторую строку с адресом
         ##           print indices
                info = (rty, jgh, codes)
                InnerVariableStorage_instance.res.add_re(info)
            except:
                print u'Не исправлены повторения!'
        
    

def analyse_re(InnerVariableStorage_instance):
    pairs = [] # для отчетности.
    for i in range(len(InnerVariableStorage_instance.objects) - 1):
 #       a_regs1 = InnerVariableStorage_instance.objects[i].getre()    # получаем список регулярных выражений 
                                                                    # объекта
        a_regs1 = re_list(InnerVariableStorage_instance.objects[i])    # получаем список регулярных выражений 
        if a_regs1 != None:
            regs1 = a_regs1[0]
        else:
            regs1 = None
        if regs1 != None:
            for j in range(i + 1, len(InnerVariableStorage_instance.objects)):
                a_regs2 = re_list(InnerVariableStorage_instance.objects[j])
                if a_regs2 != None:
                    regs2 = a_regs2[0]
                else:
                    regs2 = None
                if regs2 != None:
                    codes = compare_two_arrays_of_re(regs1, regs2)
##                   # print codes
##                    if codes != None:
##                        print codes
##                        for z in regs1:
##                            print z
##                        print '=========='
##                        for z in regs2:
##                            print z
                    if codes != None:
                        n1 = InnerVariableStorage_instance.objects[i].getid()
                        n2 = InnerVariableStorage_instance.objects[j].getid()
                        pairs.append(RegexpStatistics(codes, n1, n2))
    Draw(pairs, InnerVariableStorage_instance)
##    if analysis != u'':
##        InnerVariableStorage_instance.res.add_text('r', analysis)
    
            

def decide_on_comments(InnerVariableStorage_instance):
    # Эта функция полностью выпиливает все комментарии отовсюду. 
    # ВАЖНО: впоследствии убрать comments_must_be_checked из аргументов, так как эта информация должна передаваться
    # в настройках
    # аргумент comments_must_be_checked - ноль или единица. Если ноль, то комменты не проверяются,
    # если единица - проверяются
    comments_must_be_checked = InnerVariableStorage_instance.settings['COMMENTANA']
    array_of_comment_sets = []  # создаём массив для хранения множеств комментов
    for i in range(len(InnerVariableStorage_instance.objects)):
        if comments_must_be_checked == 1:   # проверка комментариев включена. 
            cSet = set() # тогда каждый раз создаем множество
           # print 'ccccccc'
            clear_text = pcp.comment_away(InnerVariableStorage_instance.objects[i], cSet)   # тут он по идее должен заполняться
            array_of_comment_sets.append(cSet)       # заносим комменты в массив. Чей коммент, можно установить по ключам
        else:
            clear_text = pcp.comment_away(InnerVariableStorage_instance.objects[i], set()) # тут просто выделываем файл
        InnerVariableStorage_instance.objects[i].change_plaintext(clear_text)   # после всего этого переприсваиваем сюда текст

# а ещё эта функция сразу вносит анализ комментов в результаты, если это требовалось
    if comments_must_be_checked == 1: # элементарная анализировалка комментов
        try:
            r_c = pcp.bad_comment_analyser(array_of_comment_sets)
 #           print 'c d '
        except:
            r_c = None
           # print u'Comment analysis problem occured'
        if r_c != None:
 #           l = u'Совпавшие комментарии найдены в файлах с адресами:\n'
            for i in r_c:
 #               print i
                try:
                    InnerVariableStorage_instance.res.addcommentpair(InnerVariableStorage_instance.file_list[InnerVariableStorage_instance.objects[i[0]].getid()],
                          InnerVariableStorage_instance.file_list[InnerVariableStorage_instance.objects[i[1]].getid()]) 
                except:
                    pass
#                    print 'eeee'
 #           InnerVariableStorage_instance.res.add_text('c', l)
        else:
            pass # на нет и суда нет. Не было интересных комментов
    else:
        InnerVariableStorage_instance.res.nullcomment()

            
def mainchecker(sett, files, from_where = None):   # два аргумента: первый - настроечное что-то, второе — список файлов для проверки
    #print sett
    all_info = InnerVariableStorage(sett, files)    # у нас создалась переменная со всей-всей инфой
    all_info.fill_objects()     # активировали заполнение объектов объектами
 
    decide_on_comments(all_info) # удаляем все комменты из текстов программ.
        # если в качестве настройки для комментов было избрано заполнение
 #   all_info.lenfreqdic() # Это была считалка строк, печатающая все в файл
    #после этого необходимо разделить все тексты программ на кусочки - подпрограммы
    all_info.primary_to_further()
    # где-то тут ещё надо что-то сделать с импортом

    all_info.correct_all_2in1()
    all_info.delete_all_re()
    all_info.comparisons()

    
    comparison.Main(all_info) # пока только тестовая строчка.
    
    # конечное отображение проверки. Эта строчка на своем месте. Точно. Окончательно.
    return all_info.res     # Возвращаем объект-результат!
