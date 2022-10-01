
import xml.sax
import numpy as np
import xml.etree.ElementTree as et

class MatrixHandler():
    def __init__(self):
        self.CurrentData = ""
        self.matrix = np.zeros(shape=(4,4))
        self.xmlTree = et.parse('transformationMatrix.xml')

    def __str__(self):
        print(f"Maxtrix representation: \n {self.matrix}")


    def Element(self):
        for matrix in self.xmlTree.iter('matrix'):
            for rows in matrix.iter('row'):
                for elements in rows.iter('element'):
                    row = int(rows.attrib['num'])
                    col = int(elements.attrib['col'])
                    self.matrix[row-1, col-1] = float(elements.text)

    def multiply(self, matrix):
        mult_matrix = np.multiply(self.matrix, matrix)
        return mult_matrix

    def Transpose(self):
        trans_matrix = np.transpose(self.matrix)
        return trans_matrix

if (__name__ == "__main__"):
    Handler = MatrixHandler()
    Handler.Element()
    Handler.__str__()
