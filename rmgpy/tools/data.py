import numpy

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
