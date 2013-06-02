# this ui lib bind to the css file report.css/WebElements.css

__author__ = 'lwz'

from WebElements.Display import Label
from WebElements.Document import Document
from WebElements.DOM import Div, Link, Script, Span


class CompleteDom(Document):

    def _create(self, id=None, name=None, parent=None, **kwargs):
        Document._create(self, id, name, parent, **kwargs)
        self.addHeadLink('/static/css/WebElements-min.css')
        self.addHeadLink('/static/css/report.css')

    def setTitle(self, title):
        self.title.setText(title)

    def addHeadLink(self, css_file):
        link = Link()
        link.setProperty('rel', 'stylesheet')
        link.setProperty('type', 'text/css')
        link.setProperty('media', 'screen')
        link.setHref(css_file)
        self.head.addChildElement(link)

    def addHeadScript(self, script_file):
        script = Script()
        script.setProperty('type', 'text/javascript')
        script.setProperty('src', script_file)
        self.head.addChildElement(script)


class RoundCornerPanel(Div):

    def __init__(self, title, w=220, h=150):
        self.title = title  # must before the super init...
        self.width = w
        self.height = h

        super(Div, self).__init__()

    def _create(self, id=None, name=None, parent=None, **kwargs):
        Div._create(self, id, name, parent, **kwargs)

        self.addClass('rounded-corners')
        self.setStyleFromString('background-color: #EEEEEE;')
        self.setStyleFromString('width: {0}px; height: {1}px'.format(self.width, self.height))
        self.setStyleFromString('text-align: center;')

        self.round_div_header = Div()
        self.round_div_header.addClass('top-rounded-corners')
        self.round_div_header.setStyleFromString('background-color: #CCCCFF;')
        self.round_div_header.setStyleFromString('width: 220px; height: 30px')
        self.addChildElement(self.round_div_header)

        title_label = Label()
        title_label.setProperty('text', self.title)
        title_label.addClass('black-big-label')
        self.round_div_header.addChildElement(title_label)
