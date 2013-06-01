__author__ = 'lwz'

from WebElements.Document import Document
from WebElements.DOM import Div, Link, Script


class CompleteDom(Document):
    def _create(self, id=None, name=None, parent=None, **kwargs):
        Document._create(self, id, name, parent, **kwargs)

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

    def _create(self, id=None, name=None, parent=None, **kwargs):
        Div._create(self, id, name, parent, **kwargs)

        self.addClass('rounded-corners')
        self.setStyleFromString('background-color: #EEEEEE;')
        self.setStyleFromString('width: 220px; height: 150px')

        self.round_div_header = Div()
        self.round_div_header.addClass('top-rounded-corners')
        self.round_div_header.setStyleFromString('background-color: #CCCCFF;')
        self.round_div_header.setStyleFromString('width: 220px; height: 30px')
        self.addChildElement(self.round_div_header)