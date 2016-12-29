from pylatex import Document, TikZ,PageStyle,Foot,simple_page_number
from pylatex.basic import NewPage
from pylatex.base_classes import LatexObject,Command,ContainerCommand
from pylatex.package import Package

from PyQt5.QtXml import QDomDocument,QDomElement
from PyQt5.QtCore import QFile

class Draw(LatexObject):
    packages = [Package('pgfplots'), Command('pgfplotsset', 'compat=newest')]

    def __init__(self,pos1=(0,0),pos2=(1,1),shape="rectangle",options=None):
        """
        Args
        ----
        position: tuple
            Position of the node.
        label: str
            Label of the node.
        options: str, list or `~.Options`
        """

        self.pos1 = pos1
        self.pos2 = pos2
        self.shape = shape
        self.options = options

        super().__init__()

    def dumps(self):
        """Represent the node as a string in LaTeX syntax.
        Returns
        -------
        str
        """

        string = Command('draw', options=self.options).dumps()
        
        if isinstance(self.pos1,str):
            string += " {} ".format(self.pos1)
        else:
            string += " ({},{})".format(self.pos1[0],self.pos1[1])

        string += " {} ".format(self.shape)

        if isinstance(self.pos2,str):
            string += " {} ".format(self.pos2)
        else:
            string += " ({},{})".format(self.pos2[0],self.pos2[1])
        
        string+=";"
        super().dumps()

        return string


class Node(LatexObject):
    packages = [Package('pgfplots'), Command('pgfplotsset', 'compat=newest')]

    def __init__(self,position=(0,0), label="",options=None):
        """
        Args
        ----
        position: tuple
            Position of the node.
        label: str
            Label of the node.
        options: str, list or `~.Options`
        """

        self.position = position
        self.label = label
        self.options = options

        super().__init__()

    def dumps(self):
        """Represent the node as a string in LaTeX syntax.
        Returns
        -------
        str
        """

        string = Command('node', options=self.options).dumps()
        
        string += " at ({},{})".format(self.position[0],self.position[1])
        
        string += " {{{}}}".format(self.label)

        string +=";"
        super().dumps()

        return string



class Xml2Pdf():
    def __init__(self):
        self.doc = self.setupDoc()

    def setupDoc(self):
        geometry_options = {"margin": "2cm"}
        doc = Document('basic',geometry_options=geometry_options)

        header = PageStyle("header")
        with header.create(Foot("R")):
            header.append(simple_page_number())
        doc.preamble.append(header)
        doc.change_document_style("header")

        return doc

    
    def createPdf(self,xmlFile,outputFile,tex=True):
        self.dom = QDomDocument()
        openFile = QFile(xmlFile)
        self.dom.setContent(openFile)
        domProject = self.dom.elementsByTagName("Project").item(0).toElement()
        self.dancerWidth = domProject.attribute("dancerWidth")
        self.roomHeight = domProject.attribute("roomHeight")
        self.roomWidth = domProject.attribute("roomWidth")

        domFrame = domProject.elementsByTagName("Frame").item(0).toElement()
        self.createDoc(domFrame,self.doc)

        self.doc.generate_pdf(outputFile,clean_tex=False)
        if tex:
            self.doc.generate_tex()

    def createDoc(self,domFrame,doc):

        domScenes = domFrame.elementsByTagName("Scene")
        for i in range(domScenes.length()):
            domScene = domScenes.item(i)
            domScene = domScene.toElement()
            dancers = self.getDancer(domScene)
            texts = self.getTexts(domScene)
            lines = self.getLines(domScene)
            self.createFrame(dancers,texts,lines,doc)
            doc.append(NewPage())
                

    def createFrame(self,dancers,texts,lines,doc):
        with doc.create(TikZ()) as pic:
            pic.append(Draw(pos1="(0,0)",pos2="(17,17)")) 
            for dancer in dancers:
                self.createDancer(dancer,doc)
            for line in lines:
                self.createLine(line,doc)
            for text in texts:
                self.createText(text,doc)

    def createDancer(self,dancer,doc):
        doc.append(Command("definecolor{{fillColor}}{{HTML}}{{{}{}{}}};".format(dancer["color"][1:3].upper(),dancer["color"][3:5].upper(),dancer["color"][5:7].upper())))
        doc.append(Command("definecolor{{borderColor}}{{HTML}}{{{}{}{}}};".format(dancer["boundaryColor"][1:3].upper(),dancer["boundaryColor"][3:5].upper(),dancer["boundaryColor"][5:7].upper())))
        opt = 'shape=circle,line width=3, draw=borderColor ,minimum width={}, fill=fillColor,label=below:{}'.format(self.dancerWidth,dancer["name"])  
        doc.append(Node(options=opt,position=self.pixel2cm(dancer["posX"],dancer["posY"])))

    def createText(self,text,doc):
        doc.append(Node(label=text["content"],position=self.pixel2cm(text["x"],text["y"])))

    def createLine(self,line,doc):
        doc.append(Draw(pos1=self.pixel2cm(line["x1"],line["y1"]),pos2=self.pixel2cm(line["x2"],line["y2"]),shape="--"))

    def getDancer(self,domScene): 
        dancers = []
        domDancers = domScene.elementsByTagName("Dancer")
        for j in range(domDancers.length()):
            domDancer = domDancers.item(j)
            domDancer = domDancer.toElement()
            dancer = {}
            dancer["name"] = domDancer.attribute("name")
            dancer["alias"] = domDancer.attribute("alias")
            dancer["color"] = domDancer.attribute("color")
            dancer["boundaryColor"] = domDancer.attribute("boundaryColor")
            dancer["posX"] = domDancer.attribute("posX")
            dancer["posY"] = domDancer.attribute("posY")
            dancers.append(dancer)   
        return dancers

    def getTexts(self,domScene):
        texts = []
        domTexts = domScene.elementsByTagName("Text")
        for j in range(domTexts.length()):
            domText = domTexts.item(j)
            domText = domText.toElement()
            text = {}
            text["y"] = domText.attribute("y")
            text["x"] = domText.attribute("x")
            text["content"] = domText.attribute("content")
            text["rotation"] = domText.attribute("rotation")
            texts.append(text)
        return texts

    def getLines(self,domScene):
        lines = []
        domLines = domScene.elementsByTagName("Line")
        for j in range(domLines.length()):
            domLine = domLines.item(j)
            domLine = domLine.toElement()
            line = {}
            line["x1"] = domLine.attribute("x1")
            line["y1"] = domLine.attribute("y1")
            line["x2"] = domLine.attribute("x2")
            line["y2"] = domLine.attribute("y2")
            lines.append(line)
        return lines
                    
    def pixel2cm(self,px,py,cmW=17,cmH=17):
        pixelW=float(self.roomWidth)
        pixelH=float(self.roomHeight)
        px = float(px)
        py = float(py)
        cmx = 1.*cmW/pixelW * px
        cmy = -1.*cmH/pixelH *py+cmH

        return cmx,cmy
