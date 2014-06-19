import codecs
from xml.dom.minidom import parseString


class HL:
    def __init__(self, lang = 'RU',
                 read = u'обработано файлов',
                 notread = u'не прочитаны',
                 allread_msg = u'все файлы успешно считаны',
                 regexps = u'регулярные выражения',
                 r1 = u'полностью совпадающие',
                 r2 = u'частично совпадающие',
                 r3 = u'схожие по структуре',
                 r4 = u'состоящие из схожих по структуре фрагментов',
                 contain = u'содержат',
                 nore = u'не проверялись',
                 comments = u'комментарии',
                 nocomment = u'cхожих комментариев не найдено',
                 notfound = u'схожих не найдено',
                 check = u'совпадения в коде',
                 full = u'полностью идентичны',
                 partial =  u'схожи',
                 link = u'и',
                 pf = u'содержат полностью идентичные части',
                 nopl = u'весь код оригинален'):
        self.lang = lang
        self.read = read
        self.notread = notread
        self.allread_msg = allread_msg
        self.regexps = regexps
        self.contain = contain
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4
        self.nore = nore
        self.comments = comments
        self.nocomment = nocomment
        self.check = check
        self.full = full
        self.partial =  partial
        self.link = link
        self.id_parts = pf
        self.notfound = notfound
        self.nopl = nopl
    def setlang(self, lang):
        d = codecs.open('interface_headlines.xml', u'r', 'utf-8-sig').read()#.decode('cp1251')
        doc = parseString(d.encode('utf-8')) # сделали дерево
        for node in doc.getElementsByTagName('class'):
                tn = node.attributes['name'].value
                if tn == u'H':
                        dic = {}
                        for n in node.getElementsByTagName('text'):
                                tl = n.attributes['lang'].value
                                if tl == lang:
                                        tdn = n.attributes['title'].value
                                        dic[tdn] = n.childNodes[0].nodeValue
            
        self.lang = lang
        self.read = dic['read']
        self.notread = dic['notread']
        self.allread_msg = dic['allread_msg']
        self.regexps = dic['regexps']
        self.contain = dic['contain']
        self.r1 = dic['r1']
        self.r2 = dic['r2']
        self.r3 = dic['r3']
        self.r4 = dic['r4']
        self.nore = dic['nore']
        self.comments = dic['comments']
        self.nocomment = dic['nocomment']
        self.check = dic['check']
        self.full = dic['full']
        self.partial = dic['partial']
        self.link = dic['link']
        self.id_parts = dic['id_parts']
        self.notfound = dic['notfound']
        self.nopl = dic['nopl']
        
        
