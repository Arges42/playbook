from pylatex import Document, TikZ,PageStyle,Foot,simple_page_number
from pylatex.basic import NewPage
from pylatex.base_classes import LatexObject,Command
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

    
    def createPdf(self,xmlFile):
        self.dom = QDomDocument()
        openFile = QFile(xmlFile)
        self.dom.setContent(openFile)
        domProject = self.dom.elementsByTagName("Project").item(0).toElement()
        self.dancerWidth = domProject.attribute("dancerWidth")
        self.roomHeight = domProject.attribute("roomHeight")
        self.roomWidth = domProject.attribute("roomWidth")

        domFrame = domProject.elementsByTagName("Frame").item(0).toElement()
        self.createDoc(domFrame,self.doc)

        self.doc.generate_pdf(clean_tex=False)
        self.doc.generate_tex()

    def createDoc(self,domFrame,doc):

        domScenes = domFrame.elementsByTagName("Scene")
        for i in range(domScenes.length()):
            domScene = domScenes.item(i)
            domScene = domScene.toElement()
            dancers = self.getDancer(domScene)
            self.createFrame(dancers,doc)
            doc.append(NewPage())
                

    def createFrame(self,dancers,doc):
        with doc.create(TikZ()) as pic:
            pic.append(Draw(pos1="(0,0)",pos2="(17,17)")) 
            for dancer in dancers:
                self.createDancer(dancer,doc)

    def createDancer(self,dancer,doc):
        doc.append(Command("definecolor{{tmpcolor}}{{HTML}}{{{}{}{}}};".format(dancer["color"][1:3].upper(),dancer["color"][3:5].upper(),dancer["color"][5:7].upper())))
        opt = 'shape=circle,draw,minimum width={}, fill=tmpcolor,label=center:{}'.format(self.dancerWidth,dancer["name"])  
        doc.append(Node(options=opt,position=self.pixel2cm(dancer["posX"],dancer["posY"])))

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

    def pixel2cm(self,px,py,cmW=17,cmH=17):
        pixelW=float(self.roomWidth)
        pixelH=float(self.roomHeight)
        px = float(px)
        py = float(py)
        cmx = 1.*cmW/pixelW * px
        cmy = -1.*cmH/pixelH *py+cmH

        return cmx,cmy
