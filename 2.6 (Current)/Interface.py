from Tkinter import *
from ttk import *
from tkFileDialog import askopenfilenames, askdirectory, asksaveasfilename, askopenfilename
from tkMessageBox import showerror
import re, os, codecs, sys
from xml.dom.minidom import parseString, parse
import xml.dom.minidom 
from CheckLib import *
from HL import *


def clearfilelist(MainProgWin_instance): # очищает все списки файлов
        MainProgWin_instance.fileinfo.clear_allfiles()
        MainProgWin_instance.filewindow.delete('1.0', END)
        MainProgWin_instance.dirwindow.delete('1.0', END)
        MainProgWin_instance.choosefiles_button.configure(text = MainProgWin_instance.names.choosefilebutton)
        MainProgWin_instance.choosedir_button.configure(text = MainProgWin_instance.names.choosedirbutton)
 #       MainProgWin_instance.filewindow.insert('1.0', u'Ни одного файла для проверки \nпока не выбрано.\n')
        MainProgWin_instance.dirwindow.insert(END, u'Вы ещё не выбрали ни одной папки.')
        MainProgWin_instance.filewindow.insert(END, u'Вы ещё не выбрали ни одного файла.')
        MainProgWin_instance.start_or_exit.configure(text = MainProgWin_instance.names.exitbutton, command = (lambda: ex(MainProgWin_instance)))


def clearresultfield(MainProgWin_instance):
        MainProgWin_instance.outwindow.delete('1.0', END)


def clear_all(MainProgWin_instance):
        clearresultfield(MainProgWin_instance)
        clearfilelist(MainProgWin_instance)


def change_font_settings(MainProgWin_instance):
        x = fontwindow(MainProgWin_instance)


# Функция не подогнана под формат независимых нахваний кнопок
def save_result(MainProgWin_instance):
        text_of_result = MainProgWin_instance.outwindow.get('1.0', END)
        if len(text_of_result) == 0 or re.search(u'^\\s*$', text_of_result, flags = re.U) != None:
                showerror('Error', u'Результаты проверки ещё не были получены.') # ERROR4
        else:
                sa = asksaveasfilename(filetypes = [(u'Простой текст', '*.txt')])
                f = codecs.open(sa, 'w', 'utf-8')
                f.write(text_of_result)
                f.close()


def mdic(letter_code, lang):
        d = codecs.open('interface_headlines.xml', u'r', 'utf-8-sig').read()#.decode('cp1251')
        doc = parseString(d.encode('utf-8')) # сделали дерево
        for node in doc.getElementsByTagName('class'):
                tn = node.attributes['name'].value
                if tn == letter_code:
                        dic = {}
                        for n in node.getElementsByTagName('text'):
                                tl = n.attributes['lang'].value
                                if tl == lang:
                                        tdn = n.attributes['title'].value
                                        dic[tdn] = n.childNodes[0].nodeValue
        try:
                return dic
        except:
                print 'inappr code'


class ShowParametersWindow:
    def __init__(self, MW, lang):
            self.MW = MW
            u = Toplevel(MW.root)
            d = mdic('S', lang)
            pcl = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            self.pc = Combobox(u, value = pcl, width = 4)
            self.dw = Combobox(u, value = [1, 2, 3, 4, 5, 10, 15], width = 4)
            l1 = Label(u, text = d['percent'])
            t1 = Label(u, text = u'%')
            t2 = Label(u, text = u'%')
            l2 = Label(u, text = d['difference'])
 #           l3 = Label(u, text = d['len'])
            b = Button(u, text = 'OK', command = lambda:self.save())
 #           t = Text(u, height = 1, width = 4)
            l1.grid(row = 0, column = 0)
            self.pc.grid(row = 0, column = 1)
            t1.grid(row = 0, column = 2)
            l2.grid(row = 1, column = 0)
            self.dw.grid(row = 1, column = 1)
            t2.grid(row = 1, column = 2)
 #           l3.grid(row = 2, column = 0)
 #           t.grid(row = 2, column = 1)
            b.grid(row = 3, column = 0)
            self.u = u
    def save(self):
            new_grade = None
            new_diff = None
            try:
                    new_grade = float(self.pc.get())/100
                    if new_grade != None:
                            self.MW.grade = new_grade
            except:
                    pass
            try:
                    new_diff = float(self.dw.get())/100
                    
                    if new_diff != None:
                            self.MW.diff = new_diff
            except:
                    self.MW.diff == None
            #print new_diff
            self.u.destroy()
            
            

def choosedir(MainProgWin_instance):
    d = askdirectory()
    trash = 0           # мусорные адреса
    addressesc = 0      # счётчик не мусорных
    for root, dirs, files in os.walk(d):
        for i in files:
            name = root + '/' + i # ЗАМЕНИТЬ НА ДЖОЙH
            name = os.path.realpath(name)
            if re.search('\\.pyw?$', name, flags = re.I) != None:
                try:
                        MainProgWin_instance.AddPath(name) # пополняем общий список для открытия
                        addressesc += 1
                except:
                        trash += 1
    if addressesc != 0:
        MainProgWin_instance.AddDir(d) # добавили название папки куда надо
    MainProgWin_instance.norepeating()
    if MainProgWin_instance.Chosen != 0:
        MainProgWin_instance.choosefiles_button.configure(text = MainProgWin_instance.names.nonullf)
        MainProgWin_instance.choosedir_button.configure(text = MainProgWin_instance.names.nonulld)
        MainProgWin_instance.start_or_exit.configure(text = MainProgWin_instance.names.gobutton, command = (lambda: run_main_part(MainProgWin_instance)))
        t = MainProgWin_instance.DirText()
        MainProgWin_instance.dirwindow.delete('1.0', END)
        MainProgWin_instance.dirwindow.insert('1.0', t)


# функция спрашивает файлы для обработки и добавляет их в данные
def asker(MainProgWin_instance): # аргумент - MainProgWin_instance
    op = askopenfilenames() # тут получаем список файлов, который обрабатываем дальше
    try:
        if type(op) == unicode: # вариант для виндовса
                if op != '':
                        m = re.search('\\{.*?\\}', op, flags = re.I|re.U)
                        if m != None:
                            addresses = re.findall('\\{(.*?)\\}', op, flags = re.I|re.U)
                            addresses = [j for j in addresses if re.search('\\.pyw?$', j, flags = re.I) != None]
                            # проверка файлов на открывабельность
                            for counter in addresses:                                       
                                    MainProgWin_instance.AddFile(counter) # если всё читается,
                                    # то добавляем в массив эту фигню
                        else:
                            MainProgWin_instance.AddFile(op)
                else:       #такого быть не должно, потому что что-то мы выбрали.
                            #а если не выбрали, то список не нуждается в изменении
                    pass 
        else: # для макоси, она выдает результат-кортеж
                for j in op: # перебираем элементы кортежа
                        if re.search('\\.pyw?$', j, flags = re.I) != None:
                                 MainProgWin_instance.AddFile(j)
    except:
       # print u'В функции asker, good_interface.py, произошла непредвиденная ошибка.'
       pass
    MainProgWin_instance.norepeating()
    if MainProgWin_instance.Chosen != 0:
        MainProgWin_instance.choosefiles_button.configure(text = MainProgWin_instance.names.nonullf)
        MainProgWin_instance.choosedir_button.configure(text = MainProgWin_instance.names.nonulld)
        MainProgWin_instance.start_or_exit.configure(text = MainProgWin_instance.names.gobutton, command = (lambda: run_main_part(MainProgWin_instance)))
        t = MainProgWin_instance.FileText()
        MainProgWin_instance.filewindow.delete('1.0', END)
        MainProgWin_instance.filewindow.insert('1.0', t)


class Settings:
        def __init__(self, 
                     dictionary = {'PARSEINSTR': 1, 
                                'DEFINESINGLECOMP': 1,
                                'DEFS': 1,
                                'COMMENTANA': 1,
                                'CHECKRE': 0,
                                'GENERATECONTEXTS': 1},
                     good_names = {u'Переносить одиночные инструкции на новую строку': 'PARSEINSTR',
                              u'Распознавать идентичные операции сравнения': 'DEFINESINGLECOMP',
                              u'Сравнивать подпрограммы и основной код': 'DEFS',
                              u'Провести минимальный анализ комментариев': 'COMMENTANA',
                              u'Проверять регулярные выражения': 'CHECKRE',
                              u'Автоматически генерировать контексты': 'GENERATECONTEXTS'}):
                self.dic = dictionary
                self.inner_dic = good_names
                lens = [len(i) for i in good_names]
                self.l = max(lens) + 2
        def change(self, MainWin):
                window = Toplevel(MainWin.root)
                window.title('Settings')
                nom = Label(window, text=u"Выделите выбранные вами пункты проверки:", width = self.l)
                parameters = Listbox(window, selectmode=MULTIPLE, width = self.l)
                for i in self.inner_dic.keys():
                        parameters.insert(END, i)
                b = Button(window, text = u"Сохранить",
                                command = (lambda: change_settings_temp(MainWin, window, parameters)))

                nom.grid(row = 0, column = 0)
                parameters.grid(row = 1, column = 0)
                b.grid(row = 2, column = 0)
                window.mainloop()
        def all_is_nothing(self):
                self.dic = {i: 0 for i in self.dic.keys()} # обнулили всё.
        def return_settingdic(self):
                return self.dic
                


def change_settings_temp(MainProgWin_instance, win, l):
        chosen = []
        for i in l.curselection(): # собрали все строки с параметром 1
                chosen.append(l.get(0,END)[int(i)])
        MainProgWin_instance.settings.all_is_nothing()
        for i in chosen:
                code = MainProgWin_instance.settings.inner_dic[i]
                MainProgWin_instance.settings.dic[code] = 1
        win.destroy()


def run_main_part(MainProgWin_instance):
            if MainProgWin_instance.Chosen() > 1:
                    res = mainchecker(MainProgWin_instance.Setting(), # настройки
                                MainProgWin_instance.Files(), u'GUI')       # список файлов + обозначение того, что вошли из GUI
                    MainProgWin_instance.outwindow.delete('1.0', END)
                    hl = HL()
                    hl.setlang(MainProgWin_instance.lang)
                    i = res.plaintext(hl, MainProgWin_instance.grade, MainProgWin_instance.diff)
                    MainProgWin_instance.lastcheck = res
                    MainProgWin_instance.outwindow.insert(END, i)
                    MainProgWin_instance.choosefiles_button.configure(text = MainProgWin_instance.names.choosefilebutton)
                    MainProgWin_instance.choosedir_button.configure(text = MainProgWin_instance.names.choosedirbutton)
                    MainProgWin_instance.start_or_exit.configure(text = MainProgWin_instance.names.repeat)
            else:
                    showerror(MainProgWin_instance.names.errorline, u'Вы выбрали только один файл для анализа.')
                    # ERROR3


def watch(MW):
        watchwindow(MW)


encodings = ['utf-8-sig', 'MacCyrillic', 'cp1251', 'utf-16-le', 'utf-16-be']

class watchwindow:
    def __init__(self, MW):
        if MW.lastcheck != None:
                self.grade = MW.grade
                self.d = MW.diff
                self.window = Toplevel(MW.root)
                self.window.title(MW.menunames.watchwindow)
                self.title1 = Text(self.window, height = 2)
                self.title2 = Text(self.window, height = 2)
                self.code1 = Text(self.window)
                self.code2 = Text(self.window)
                self.L = MW.lastcheck.addresspairs_f + MW.lastcheck.addresspairs_p # Это будем перебирать
                n = []

                for i in self.L:
                        if i[2] >= self.grade or i[3] >= self.grade:
                                d = i[2] - i[3]
                                if d < 0:
                                    d = -d
                                if d <= self.d:
                                        n.append(i)
                self.L = n

                self.current = 0
                self.b1 = Button(self.window, text = u'<<', command = lambda: self.showerr())
                if len(self.L) == 1:
                        self.b2 = Button(self.window, text = u'>>', command = lambda: self.showerr())
                else:
                        self.b2 = Button(self.window, text = u'>>', command = lambda: self.shownextpair())
                self.p1 = Text(self.window, height = 2)
                self.p2 = Text(self.window, height = 2)
                self.title1.grid(row = 0, column = 0)
                self.title2.grid(row = 0, column = 1)
                self.code1.grid(row = 1, column = 0)
                self.code2.grid(row = 1, column = 1)
                self.p1.grid(row = 2, column = 0)
 #               self.p2.grid(row = 2, column = 1)
                self.b1.grid(row = 3, column = 0)
                self.b2.grid(row = 3, column = 1)
                self.newpair()

        else:
                showerror(u'Error', u'Пока не осуществлено ни одной проверки.') #ERROR2
    def newpair(self):
            encodings = ['utf-8-sig', 'MacCyrillic', 'cp1251', 'utf-16-le', 'utf-16-be']
            # Возможный набор кодировок. 
            self.title1.delete('1.0', END)
            self.title1.insert(END, self.L[self.current][0])
            self.title2.delete('1.0', END)
            self.title2.insert(END, self.L[self.current][1])
            self.code1.delete('1.0', END)
            self.code2.delete('1.0', END)
            for i in encodings: # Проверка всех по очереди
                try:
                    t1 = codecs.open(self.L[self.current][0], 'r', i).read()
                    self.code1.insert(END, t1)                   
                    break
                except:
                    pass
            for i in encodings: # Проверка всех по очереди
                try:
                    t2 = codecs.open(self.L[self.current][1], 'r', i).read()
                    self.code2.insert(END, t2) 
                    break
                except:
                    pass
            self.p1.delete('1.0', END)
            self.p1.insert(END, u'_____________\n')
            self.p1.insert(END, unicode((self.L[self.current][2])*100)[:4] + u'% /' + unicode((self.L[self.current][3])*100)[:4] + u'%')
    def showerr(self):
            showerror(u'Error', u'Вы дошли до конца списка.') #ERROR1
    def shownextpair(self):
            self.current += 1
            if self.current == len(self.L) - 1: # Если элемент не последний
                self.b2.configure(command = lambda: self.showerr())
            self.b1.configure(command = lambda: self.showprevpair())

            self.newpair()
            
    def showprevpair(self):
            self.current -= 1
            if self.current == 0: # Если элемент первый
                self.b1.configure(command = lambda: self.showerr())
            self.b2.configure(command = lambda: self.shownextpair())
            self.newpair()
                    

# отвечает за закрывание окна
def ex(MainProgWin_instance):
        MainProgWin_instance.root.destroy()


def change_settings(MainProgWin_instance):
        MainProgWin_instance.settings.change(MainProgWin_instance) # Говнокод


class fontwindow:
        def __init__(self, MainProgWin_instance):
                sizes = [10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24, 30, 40, 72]
                fontnames = []
                if sys.platform == 'darwin':
                        fontnames = ['Courier New',
                                     'Helvetica',
                                     'Times New Roman',
                                     'Noteworthy',
                                     'Arial']
                else:
                        fontnames = ['Courier New',
                                     'Microsoft Sans Serif',
                                     'Times New Roman',
                                     'Arial']
                self.x = Toplevel(MainProgWin_instance.root, width = 320, height = 200)# выбрасываем диалоговое окошко
                self.x.title('Font Settings')
  #              self.l1 = Label(self.x, text = u'Размер шрифта: ', width = 25)
                self.l2 = Label(self.x, text = 'Шрифт списка файлов: ', width = 25)
 #               self.l4 = Label(self.x, text = u'Размер шрифта: ', width = 25)
                self.l3 = Label(self.x, text = 'Шрифт выдачи: ', width = 25)
                self.t1 = Combobox(self.x, value = sizes)
                self.t1.set(12)
                self.t2 = Combobox(self.x, value = fontnames)
                self.t3 = Combobox(self.x, value = fontnames)    # название шрифта результатов
                self.t2.set("Times New Roman")
                self.t3.set("Times New Roman")
                self.t4 = Combobox(self.x, value = sizes)
                self.t4.set(12)
                self.but = Button(self.x, text = u'Сохранить', command = (lambda: self.ch(MainProgWin_instance)))
 #               self.l1.grid(row = 2, column = 0)
#                self.t1.grid(row = 2, column = 1)
                self.l2.grid(row = 1, column = 0)
                self.t2.grid(row = 1, column = 1)
                self.l3.grid(row = 3, column = 0)
                self.t3.grid(row = 3, column = 1)
#                self.l4.grid(row = 4, column = 0)
#                self.t4.grid(row = 4, column = 1)
                self.but.grid(row = 5, column = 0)
##        def ch(self, MainProgWin_instance):
##                MainProgWin_instance.outwindow.config(font=(self.t3.get(), self.t4.get()))
##                MainProgWin_instance.filewindow.config(font=(self.t2.get(), self.t1.get()))
##                MainProgWin_instance.dirwindow.config(font=(self.t2.get(), self.t1.get()))
##                self.x.destroy()
        def ch(self, MainProgWin_instance):
                MainProgWin_instance.outwindow.config(font=(self.t3.get(), MainProgWin_instance.winset.basesize))
                MainProgWin_instance.filewindow.config(font=(self.t2.get(), MainProgWin_instance.winset.basesize))
                MainProgWin_instance.dirwindow.config(font=(self.t2.get(), MainProgWin_instance.winset.basesize))
                self.x.destroy()


class OtherErrors:
    def __init__(self, lang):
        self.lang = lang
        d = mdic('E', lang)
##        d = codecs.open('interface_headlines.xml', u'r', 'utf-8-sig').read()#.decode('cp1251')
##        doc = parseString(d.encode('utf-8')) # сделали дерево
##        for node in doc.getElementsByTagName('class'):
##                tn = node.attributes['name'].value
##                if tn == u'E':
##                        dic = {}
##                        for n in node.getElementsByTagName('text'):
##                                tl = n.attributes['lang'].value
##                                if tl == lang:
##                                        tdn = n.attributes['title'].value
##                                        dic[tdn] = n.childNodes[0].nodeValue
        self.err = dic['err']
        self.e1 = dic['e1']
        self.e2 = dic['e2']
        self.e3 = dic['e3']
        self.e4 = dic['e4']
                

                
class ViewSettings:
    def __init__(self, basefont = 'verdana', basesize = 14):
        self.basefont = basefont # в качестве аргументов можно передать
        # шрифт, размер и т.п.
        self.basesize = basesize
        self.platform = sys.platform # платформа определяется автоматически
        if self.platform != 'darwin':
                self.basesize = 10
        self.buttonwidth = 20
        self.dirsize = 12
        self.outputsize = 26
        self.fw = 40
    def system(self):
        return self.platform
    def font(self):
        return self.basefont
    def fontsize(self):
        return self.basesize


def change_view_settings(MW):
        ShowParametersWindow(MW, u'RUS')


class AddedFilesInfo:
    def __init__(self):
        self.allfiles = []      # этот список нужен для отображения файлов
        self.dirs = []          # этот - для отображения папок
        self.listoffiles = []   # это - список файлов, который передастся в прогу
    def savedirname(self, d):
        self.dirs.append(d)
    def savereadfile(self, d):
        self.allfiles.append(d)
    def makedirtext(self):
            t = u''
            for i in range(len(self.dirs)):
                t += unicode(i+1)
                t += u') '
                t += unicode(self.dirs[i])
                t += u'\n'
            return t
    def norepeat(self):
        self.allfiles = list(set(self.allfiles))     # этот список нужен для отображения файлов
        self.dirs = list(set(self.dirs))         # этот - для отображения папок
        self.listoffiles = list(set(self.listoffiles))  # это - список файлов, который передастся в прогу
    def savepathinboth(self, d):
            self.allfiles.append(d)
            self.listoffiles.append(d)
    def makefiletext(self):
            t = u''
            for i in range(len(self.listoffiles)):
                t += unicode(i+1)
                t += u') '
                t += unicode(self.listoffiles[i])
                t += u'\n'
            return t
    def clear_allfiles(self):
            self.allfiles = []
            self.dirs = []
            self.listoffiles = []


class Texts:
    def __init__(self, lang):
        d = codecs.open('interface_headlines.xml', u'r', 'utf-8-sig').read()#.decode('cp1251')
        doc = parseString(d.encode('utf-8')) # сделали дерево
        for node in doc.getElementsByTagName('class'):
                tn = node.attributes['name'].value
                if tn == u'T':
                        dic = {}
                        for n in node.getElementsByTagName('text'):
                                tl = n.attributes['lang'].value
                                if tl == lang:
                                        tdn = n.attributes['title'].value
                                        dic[tdn] = n.childNodes[0].nodeValue
                        self.mainwin_name = dic[u'mainwin_name'] # Название окна
                        self.filewindow = dic[u'filewindow'] # Название окна с файлами
                        self.dirwindow = dic[u'dirwindow']
                        self.output = dic[u'output'] # название окна выдачи
                        self.exitbutton = dic[u'exitbutton'] # Кнопка "выход"
                        self.gobutton = dic[u'gobutton'] # кнопка "выход" переименовывается в...
                        self.choosefilebutton = dic[u'choosefilebutton'] # Название кнопки "выбрать файлы"
                        self.choosedirbutton = dic[u'choosedirbutton'] # Название кнопки "выбрать папку"
                        self.nonullf = dic[u'nonullf']
                        self.nonulld = dic[u'nonulld']
                        self.errorline = dic[u'errorline']
                        self.repeat = dic[u'repeat']
                        self.nofiletext = dic[u'nofiletext']
                        self.nodirtext = dic[u'nodirtext']
                        break
        self.language = lang # Название языка, на котором класс


class MenuNames: # это просто шаг к возможности безболезненно переводить интерфейс на разные языки.
##        # впоследствии неплохо бы избавиться от ужасного числа аргументов, оставив только язык -
##        # остальное будет выписываться из файла
    def __init__(self, lang):
        d = codecs.open('interface_headlines.xml', u'r', 'utf-8-sig').read()#.decode('cp1251')
        doc = parseString(d.encode('utf-8')) # сделали дерево
        for node in doc.getElementsByTagName('class'):
                tn = node.attributes['name'].value
                if tn == u'M':
                        dic = {}
                        for n in node.getElementsByTagName('text'):
                                tl = n.attributes['lang'].value
                                if tl == lang:
                                        tdn = n.attributes['title'].value
                                        dic[tdn] = n.childNodes[0].nodeValue
                        self.fileroot = dic[u'fileroot']
                        self.windowroot = dic[u'windowroot']
                        self.settingroot = dic[u'settingroot']
                        self.file_save = dic[u'file_save']
                        self.setting_fonts = dic[u'setting_fonts']
                        self.setting_parameters = dic[u'setting_parameters']
                        self.window_clearfiles = dic[u'window_clearfiles']
                        self.window_clearoutput = dic[u'window_clearoutput']
                        self.window_clearall = dic[u'window_clearall']
                        self.watchmode = dic[u'watchmode']
                        self.watchwindow = dic[u'watchmode']
                        break
        self.language = lang # Название языка, на котором класс
        
class MainWindow: # класс, содержащий основное окно и всё для него нужное
    def __init__(self, language = 'RUS'):
        self.lang = language
        self.settings = Settings()
        winset = ViewSettings() # Создаем класс с настройками внутри
        self.fileinfo = AddedFilesInfo()
        self.lastcheck = None
        names = Texts(language)
        menu_points = MenuNames(language)
        self.names = names
        self.winset = winset
        self.grade = 0.55
        self.diff = 0.05

        self.menunames = menu_points
        
        root = Tk()     # Внутри создаем корневое окно
        maxw = root.winfo_screenwidth() # ширина
        maxh = root.winfo_screenheight() #высота
        root.title(names.mainwin_name) # название
        addit = Frame(root)
        addit2 = Frame(root)
        filewindow = Frame(addit)
        outputwindow = Frame(addit2)
        fr = Frame(filewindow)
        dr = Frame(filewindow)
        canv = Canvas(filewindow,height=3,width = 360, bg="white")
        filelist_heading = Label(fr, text = names.filewindow) # заголовок окошка с файлами
        dir_heading = Label(dr, text = names.dirwindow)
        output_heading = Label(outputwindow, text = names.output) # заголовок окошка с выдачей
        self.filewindow = Text(fr, height = winset.dirsize + 4, font=(winset.basefont, winset.basesize, 'normal'),
                               width = winset.fw)

        self.dirwindow = Text(dr, height = winset.dirsize, font=(winset.basefont, winset.basesize, 'normal'),
                              width = winset.fw)
        self.dirwindow.insert(END, names.nodirtext)
        self.filewindow.insert(END, names.nofiletext)
        self.outwindow = Text(outputwindow, height = winset.outputsize + 7, font=(winset.basefont, winset.basesize, 'normal'))
        rightscr = Scrollbar(outputwindow, command = self.outwindow.yview)
        self.outwindow.config(yscrollcommand = rightscr.set)
        leftscr = Scrollbar(dr, command = self.dirwindow.yview)
        self.dirwindow.config(yscrollcommand = leftscr.set)
        leftscr2 = Scrollbar(fr, command = self.filewindow.yview)
        self.filewindow.config(yscrollcommand = leftscr2.set)
        self.choosefiles_button = Button(filewindow, text = names.choosefilebutton, width = winset.buttonwidth, command = (lambda: asker(self)))
        self.start_or_exit = Button(filewindow, text = names.exitbutton, width = winset.buttonwidth, command = (lambda:ex(self)))
        self.choosedir_button = Button(filewindow, text = names.choosedirbutton, width = winset.buttonwidth, command = (lambda: choosedir(self)))
        self.root = root
 #       canv.pack(side = TOP)
        leftscr.pack(side = LEFT)
        leftscr2.pack(side = LEFT)
        dir_heading.pack(side = TOP)      # Это всё внутри фрейма
        self.dirwindow.pack(side = BOTTOM)
        filelist_heading.pack(side = TOP)
        self.filewindow.pack(side = BOTTOM)
        dr.pack(side = TOP)
        self.start_or_exit.pack(side = BOTTOM)
        self.choosefiles_button.pack(side = BOTTOM) # Это тоже внутри фрейма
        self.choosedir_button.pack(side = BOTTOM)
        fr.pack(side = BOTTOM)
        filewindow.pack(side = TOP)
        addit.pack(side = LEFT)
        outputwindow.pack(side = TOP)
        addit2.pack(side = LEFT)
        output_heading.pack(side = TOP)
        self.outwindow.pack(side = LEFT)
        rightscr.pack(side = RIGHT)
        ################################
        self.m = Menu(self.root) # Создаем меню
        self.root.config(menu = self.m) # приделываем его к программе
        self.fm = Menu(self.m) # выпадающая хрень
        self.om = Menu(self.m) 
        self.hm = Menu(self.m) # файл
        self.helplist = Menu(self.m)
        self.m.add_cascade(label = menu_points.fileroot, menu = self.hm)
        self.m.add_cascade(label = menu_points.windowroot, menu = self.om)
        self.m.add_cascade(label = menu_points.settingroot, menu = self.fm)
##        self.m.add_cascade(label = u'Информация', menu = self.am)
        self.fm.add_command(label = menu_points.setting_fonts, command = (lambda: change_font_settings(self)))
        self.fm.add_command(label = u'Демонстрация результатов', command = (lambda: change_view_settings(self)))
        self.fm.add_command(label = menu_points.setting_parameters, command = (lambda: change_settings(self)))
 #       self.fm.add_command(label = u'Вернуться к стандартным настройкам проверки', command = (lambda: standart_set(self)))
        self.hm.add_command(label = menu_points.file_save, command = (lambda: save_result(self)))
        self.hm.add_command(label = menu_points.watchmode, command = (lambda: watch(self)))
        self.om.add_command(label = menu_points.window_clearfiles, command = (lambda: clearfilelist(self)))
        self.om.add_command(label = menu_points.window_clearoutput, command = (lambda: clearresultfield(self)))
        self.om.add_command(label = menu_points.window_clearall, command = (lambda: clear_all(self)))

        # Приделывание нового раздела (неоконченное)
##        self.m.add_cascade(label = 'Help&About', menu = self.helplist)
##        self.helplist = Menu(self.m)
##        self.m.add_cascade(label = 'Help&About', menu = self.helplist)
##        self.helplist.add_command(label = u'FAQ')

        #############################
    def Start(self):
            self.root.mainloop()
    def AddDir(self, dirname):
            self.fileinfo.savedirname(dirname)
    def AddPath(self, path):
            self.fileinfo.savereadfile(path)
    def Chosen(self):
            return len(self.fileinfo.allfiles)
    def DirText(self):
            return self.fileinfo.makedirtext()
    def FileText(self):
            return self.fileinfo.makefiletext()
    def norepeating(self):
            self.fileinfo.norepeat()
    def AddFile(self, path):
            self.fileinfo.savepathinboth(path)
    def Setting(self):
            return self.settings.return_settingdic()
    def Files(self):
            return self.fileinfo.allfiles


class StartLanguageWindow:
        def __init__(self):
                language = 'RUS'
                root = Tk()
                root.title(u'Language Bar')
                l = Label(root, text = u'Choose a language: ')
                self.lb = Listbox(root)
                for i in ['RUS', 'ENG']:
                        self.lb.insert(END, i)
                self.b = Button(root, text = u'OK', command = lambda: self.run_next_win())
                l.pack(side = TOP)
                self.lb.pack(side = TOP)
                self.b.pack(side = TOP)
                self.root = root
        def start(self):
                self.root.mainloop()
        def run_next_win(self):
                chosen = []
                for i in self.lb.curselection(): # собрали все строки с параметром 1
                        chosen.append(self.lb.get(0,END)[int(i)])
                if len(chosen) != 1:
                    showerror(u'Error', u'Choose a language!')
                else:
                        lang = chosen[0]
                        x = MainWindow(lang)
                        self.root.destroy()
                        x.Start()

                        

def start(chooselang = True):
        if chooselang == True:
                x = StartLanguageWindow()
                x.start()
        else:
                x = MainWindow()
                x.Start()               
        

start(False)        
