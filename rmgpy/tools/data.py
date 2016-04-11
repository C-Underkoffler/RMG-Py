import numpy
import math
import csv

class GenericData(object):
    """
    A generic data class for the purpose of plotting.
    ======================= ==============================================================================================
    Attribute               Description
    ======================= ==============================================================================================
    `label`                 A string label describing the data, can be used in a plot legend or in an axis label
    `data`                  A numpy array of the data
    `species`               Contains species associated with the data, often used with a Species object
    `reaction`              Contains reaction associated with the data, often used with a Reaction object
    `units`                 Contains a string describing the units associated with the data
    `index`                 An integer containing the index associated with the data
    ======================= ==============================================================================================
    """
    def __init__(self, label='', data=None, species=None, reaction=None, units=None, index=None):
        
        self.label = str(label) if label else None
        
        if isinstance(data, list):
                self.data = numpy.array(data)
        elif isinstance(data, numpy.ndarray):
                self.data = data
        else:
            raise Exception('Data for GenericData object must be initialized as a list or numpy.array of values.')
            
        self.species = species
        self.reaction = reaction
        self.units = str(units) if units else None
        self.index = int(index) if index else None


class ComparisonBundle:
    """
    A class for storing multiple :class: GenericData for the purpose of comparison
    ======================= ==============================================================================================
    Attribute               Description
    ======================= ==============================================================================================
    `title`                 A string label describing the data, (recommended to use dependent variable and use source
                                differentiation for label of GenericData objects in yData)
    `xDataList`             A list of numpy arrays for the independent variable (list index corresponds to yData)
    'yDataList'             A list of numpy arrays for the independent variable (list index corresponds to xData)
    `species`               Contains species associated with the data, often used with a Species object
    `reaction`              Contains reaction associated with the data, often used with a Reaction object
    `xUnits`                Contains a string describing the units associated with the data of the independent variable
    'yUnits'                Contains a string describing the units associated with the data of the independent variable
    `index`                 An integer containing the index associated with the data
    ======================= ==============================================================================================
    """
    def __init__(self, title='', xDataList=[], yDataList=[], species=None, reaction=None, xUnits=None, yUnits=None, index=None):
        self.title=title
        self.xDataList=xDataList
        self.yDataList=yDataList
        self.species=species
        self.reaction=reaction
        self.xUnits=xUnits
        self.yUnits=yUnits
        self.index=index

        #Check that there is a xData for every yData
        assert len(self.xDataList) == len(self.yDataList), "The length of xDataList and yDataList are not the same."

        #assign indicies to the xData and yData
        for index, (x,y) in enumerate(zip(self.xDataList, yDataList)):
            x.index=index
            y.index=index

        #Check that species, reaction, and unit are consistent across all data
        self.checkAndMakeConsistent()

    def __str__(self):
        """
        Return a string representation of this test case, using its title'.
        """
        return 'Comparison Bundle: {0}'.format(self.title)

    def checkAndMakeConsistent(self):
        """
        Checks that the species, reaction, and units are consistent across all data, raising an assertion error if
         anything with the exception of an omission in the form of None.

        If species, reaction, yUnits, or xUnits are None on the ComparisonBundle (self), then this function will
        attempt to pick it out from GenericData objects in xDataList and yDataList

        Conversely, if species, reaction, or units are None in any of the GenericData objects in xDataList or
        yDataList, this function will set those attributes equal to the appropriate analog from the ComparisonBundle.
        """

        #Check that there is a xData for every yData
        assert len(self.xDataList) == len(self.yDataList), "The length of xDataList and yDataList are not the same."

        #If there is no data, there is nothing to check
        if not self.xDataList>0:
            return

        #Matching of attributes for the "head" (self) and the genericDatas
        matching={'species': (self.yDataList, 'species', "yData"),
               'reaction': (self.yDataList, 'reaction', "xData"),
               'xUnits': (self.xDataList, 'units', 'xData'),
               'yUnits': (self.yDataList, 'units', 'yData'),

        }

        #If the head attributes are not set, try to take it from one of the arrays in the list
        for headAttr, objAttr in matching.iteritems():
            dataList=objAttr[0]
            slaveAttr=objAttr[1]
            if getattr(self, headAttr) is None:
                for data in dataList:
                    if not getattr(data, slaveAttr) is None:
                        setattr(self, headAttr, getattr(data, slaveAttr))

        #Now check that all attributes are consistent
        for headAttr, objAttr in matching.iteritems():
            dataList=objAttr[0]
            slaveAttr=objAttr[1]
            for data in dataList:
                if getattr(data, slaveAttr) is None:
                    setattr(data, slaveAttr, getattr(self, headAttr))

                if getattr(self,headAttr) is None:
                    assert getattr(data, slaveAttr)==getattr(self, headAttr), \
                        "The GenericData for {0} index {1} has inconsistent {2} with the '{3}' or " \
                        "other GenericData objects in the ComparisonBundle".format(objAttr[2], data.index, slaveAttr,
                                                                                   str(self))
                elif headAttr== "species" or headAttr=="reaction":
                    assert getattr(self, headAttr).isIsomorphic(getattr(data, slaveAttr)), \
                        "The GenericData for {0} index {1} has inconsistent {2} with the '{3}' or " \
                        "other GenericData objects in the ComparisonBundle".format(objAttr[2], data.index, slaveAttr,
                                                                                   str(self))
                else:
                    assert getattr(data, slaveAttr)==getattr(self, headAttr), \
                        "The GenericData for {0} index {1} has inconsistent {2} with the '{3}' or " \
                        "other GenericData objects in the ComparisonBundle".format(objAttr[2], data.index, slaveAttr,
                                                                                   str(self))
    def addDataSet(self, xData, yData):
        """
        Adds a new set of data to the ComparisonBundle where xData and yData are :class: GenericData objects with either
        matching species, reaction, and units, or with all the former units unintialized with None
        """
        newIndex=len(self.xDataList)
        xData.index=newIndex
        self.xDataList.append(xData)

        yData.index=newIndex
        self.yDataList.append(yData)

        #Recheck that the newly added data set conforms to the correct attributes
        self.checkAndMakeConsistent()

    def removeDataSet(self, yLabel=None, index=None):
        """
        Removes a data set (a pair of :class: GenericData objects, one from xDataList and one from yDataList). The data
        set is recognized by the label of the yData OR the index of data set which is the same as the list index in
        xDataList or yDataList.
        """
        if index is None and yLabel is None:
            raise Exception("No label or index was given to identify the Data set to be removed")

        #Find index if label is provided
        if yLabel:
            for newIndex, yData in enumerate(self.yDataList):
                if yData.label==yLabel:
                    index=newIndex
                    break
            else: raise Exception("The inputted label {0} did not match the label for any of the data sets " \
                                  "(checks the y variable)".format(yLabel))

        #Remove the data set
        del self.xDataList[index]
        del self.yDataList[index]

        #reindex all remaining data sets
        for xData, yData in zip(self.xDataList[index:], self.yDataList[index:]):
            xData.index+=-1
            yData.index+=-1

    def makeLog(self, base=10.0):
        """
        Converts the yData arrays to logarithms. The variable 'base' is a float defining the base of the logarithm.

        Any data points that are not compatible (negative value or 0), will be discarded along with the corresponding
        point in xData
        """

        for xData, yData in zip(self.xDataList, self.yDataList):
            newXArray=[]
            newYArray=[]
            for xPoint, yPoint in zip(xData.data, yData.data):
                if yPoint >0:
                    newXArray.append(xPoint)
                    newYArray.append(math.log(yPoint,base))
            #Convert to numpy array and set data
            newXArray=numpy.array(newXArray)
            newYArray=numpy.array(newYArray)
            xData.data=newXArray
            yData.data=newYArray

            #Change units on yData
            yData.units="log" +str(base)+ " " + yData.units

        #Change units on ComparisonBundle
        self.yUnits="log" +str(base)+ " " + self.yUnits

    def sortByX(self):
        """
        Sort all the datapoints in each GenericData in xDataList in ascending order and perform a corresponding sort
        on the datapoints in each GenericData in yDataList
        """

        for xData, yData in zip(self.xDataList, self.yDataList):
            #decorated sort
            xTuple, yTuple=zip(*sorted(zip(xData.data, yData.data)))
            #set data
            xData.data=numpy.array(xTuple)
            yData.data=numpy.array(yTuple)

    def printToCsv(self, outputPath):
        #Sort to make human readable
        self.sortByX()
        with open(outputPath, 'wb') as output:
            spamwriter=csv.writer(output)
            #write out headings and units
            labelLine=[]
            unitLine=[]
            for xData, yData in zip(self.xDataList, self.yDataList):
                labelLine.append(xData.label)
                labelLine.append(yData.label)
                unitLine.append(xData.units)
                unitLine.append(yData.units)

            spamwriter.writerow(labelLine)
            spamwriter.writerow(unitLine)

            dataMatrix=[]
            largestLength=max([len(xData.data) for xData in self.xDataList])
            for xData, yData in zip(self.xDataList, self.yDataList):
                #Concatenate extra blank entries if length is not longest
                if len(xData.data)<largestLength:
                    tail=numpy.array(['']*(largestLength-len(xData.data)))
                    newXData=numpy.concatenate((xData.data,tail))
                    newYData=numpy.concatenate((yData.data,tail))
                    dataMatrix.append(newXData)
                    dataMatrix.append(newYData)
                else:
                    dataMatrix.append(xData.data)
                    dataMatrix.append(yData.data)

            #transpose dataMatrix
            numpy.array(dataMatrix)
            newDataMatrix=numpy.transpose(dataMatrix)

            #write out data points
            for line in newDataMatrix:
                spamwriter.writerow(line)