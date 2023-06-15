import os
import re
import pathlib
import glob
import logging
from lxml import etree
from validateEntities import valent


class Write_DMC():

   def __init__(self, dmroot, filename, mainfolder):
        GRENT = []
        all_graphics = dmroot.xpath('.//*[self::symbol or self::graphic]')
        entity_isochr = '''<!ENTITY % ISOEntities PUBLIC "ISO 8879-1986//ENTITIES ISO Character Entities 20030531//EN//XML" "http://www.s1000d.org/S1000D_4-1/ent/ISOEntities">
%ISOEntities;'''
        tif_notation = '<!NOTATION tiff SYSTEM "tiff">'
        cgm_notation = '<!NOTATION cgm SYSTEM "cgm">'
        if all_graphics != []:
            for graphic in all_graphics:
                entity_tif = '<!ENTITY {0} SYSTEM "Graphics/{0}.tif" NDATA tiff>'.format(graphic.attrib['infoEntityIdent'])
                entity_cgm = '<!ENTITY {0} SYSTEM "Graphics/{0}.cgm" NDATA cgm>'.format(graphic.attrib['infoEntityIdent'])
                GRENT.append(entity_tif)
                GRENT.append(entity_cgm)
            graphic_entities = '\n'.join(GRENT)
            doctype_declaration = '''<!DOCTYPE dmodule [\n{0}\n{1}\n{2}\n{3}\n]>'''.format(entity_isochr, 
                                                                                           tif_notation,
                                                                                           cgm_notation,
                                                                                           graphic_entities)
        else:
            doctype_declaration = '''<!DOCTYPE dmodule [\n{0}\n]>'''.format(entity_isochr)
            
        os.chdir(mainfolder)
        write_source = open(filename, 'w', encoding = 'utf-8')
        write_source.write("<?xml version='1.0' encoding='UTF-8'?>")
        write_source.write(doctype_declaration)
        write_source.write(etree.tostring(dmroot).decode())
        write_source.close()


class Write_PMC():

   def __init__(self, dmroot, filename, mainfolder):
        entity_isochr = '''<!ENTITY % ISOEntities PUBLIC "ISO 8879-1986//ENTITIES ISO Character Entities 20030531//EN//XML" "http://www.s1000d.org/S1000D_4-1/ent/ISOEntities">
%ISOEntities;'''
        doctype_declaration = '''<!DOCTYPE pm [\n{0}\n]>'''.format(entity_isochr)
        os.chdir(mainfolder)
        write_source = open(filename, 'w', encoding = 'utf-8')
        write_source.write("<?xml version='1.0' encoding='UTF-8'?>")
        write_source.write(doctype_declaration)
        write_source.write(etree.tostring(dmroot).decode())
        write_source.close()


class NameAndCode():

    def name_from_dmcode(self, dmcode_attribute_dictonary):
            adder = ('DMC', dmcode_attribute_dictonary['modelIdentCode'], 
                            dmcode_attribute_dictonary['systemDiffCode'], 
                            dmcode_attribute_dictonary['systemCode'], 
                            dmcode_attribute_dictonary['subSystemCode']+dmcode_attribute_dictonary['subSubSystemCode'], 
                            dmcode_attribute_dictonary['assyCode'], 
                            dmcode_attribute_dictonary['disassyCode']+dmcode_attribute_dictonary['disassyCodeVariant'], 
                            dmcode_attribute_dictonary['infoCode']+dmcode_attribute_dictonary['infoCodeVariant'], 
                            dmcode_attribute_dictonary['itemLocationCode'])
            filename = '-'.join(adder)
            return str(filename)
    
    def dmcode_from_name(self, dmc_name):
                                    #P      MIC                 SDC             SC               SSC      SSSC       AC         DC        DCV         IC          ICV         ILC
        namecompiler = re.compile(r'(DMC)-(HON[A-Z0-9]{2,14})-([A-Z0-9]{1,3})-([A-Z0-9]{2,3})-([0-9]{1})([0-9]{1})-([0-9]{2})-([A-Z0-9]{2})([A-Y]{1})-([A-Z0-9]{3})([A-Z]{1})-([A-D]{1})')
        filename = re.match(namecompiler, str(dmc_name)).group()
        attributes = re.findall(namecompiler, str(dmc_name))
        dmcodeelem = etree.Element('dmCode', modelIdentCode = attributes[0][1],
                                            systemDiffCode = attributes[0][2],
                                            systemCode = attributes[0][3],
                                            subSystemCode = attributes[0][4],
                                            subSubSystemCode = attributes[0][5],
                                            assyCode = attributes[0][6],
                                            disassyCode = attributes[0][7],
                                            disassyCodeVariant = attributes[0][8],
                                            infoCode = attributes[0][9],
                                            infoCodeVariant = attributes[0][10],
                                            itemLocationCode = attributes[0][11])                                    
        return dmcodeelem, filename

    def only_name(self, dmname):
        namecompiler = re.compile(r'(DMC)-(HON[A-Z0-9]{2,14})-([A-Z0-9]{1,3})-([A-Z0-9]{2,3})-([0-9]{1})([0-9]{1})-([0-9]{2})-([A-Z0-9]{2})([A-Y]{1})-([A-Z0-9]{3})([A-Z]{1})-([A-D]{1})')
        filename = re.match(namecompiler, str(dmname))
        if filename != None:
            return filename.group()


class Refresh_DMC():

    def refresh(self, pmpath, logger):
        dirpath = pathlib.PureWindowsPath(pmpath).as_posix()
        os.chdir(dirpath)
        allfiles = Exclusion().parsable_list(dirpath)
        dmcname_outside = None
        for each in allfiles:
            if each.startswith('DMC-HON'):
                file = valent(each, dirpath)
                logger.info('Refreshing DMC:: {0}'.format(file))
                fileparser = etree.XMLParser(no_network = True, recover = True)
                parsedxml = etree.parse(file, fileparser)
                dmroot = parsedxml.getroot()
                identcode = dmroot.find('.//dmAddress//dmIdent/dmCode')
                dmcname_attribs = NameAndCode().dmcode_from_name(str(file))
                dmcname_code = dmcname_attribs[0]
                dmcname_outside = dmcname_attribs[1]
                if identcode.attrib != dmcname_code.attrib:
                    identcode.addnext(dmcname_code)
                    identcode.getparent().remove(identcode)
                    logger.info('Renamed from:: {0} to {1}'.format(NameAndCode().name_from_dmcode(identcode.attrib), dmcname_outside))
                Write_DMC(dmroot, file, dirpath)
                os.rename(file, '{0}.xml'.format(dmcname_outside))
        logger.info('Task Completed:: Refresh DMC')
        return Exclusion().parsable_list(dirpath), dmcname_outside


class Exclusion():

    def parsable_list(self, path):
        os.chdir(path)
        all_files = os.listdir(path)
        G = ['DMC-HONAERO-*',
            'DMC-HON*-00LA-*',
            'DMC-HON*-00NA-*',
            'DMC-HON*-00KA-*',
            'DMC-HON*-012A-*',
            'DMC-HON*-012B-*',
            'DMC-HON*-0A4A-*',
            'DMC-HON*-0A5A-*'
            ]

        R = []
        for each in G:
            for i in glob.glob('{0}*.xml'.format(each)):
                par = etree.XMLParser(no_network=True, recover=True)
                root = etree.parse(i, par).getroot()
                if root.find('.//commonRepository') != None:
                    R.append(i)
                elif i.startswith('DMC-HONAERO-'):
                    R.append(i)
                else:
                    pass

        partial = list(set(dict.fromkeys(R))^set(all_files))

        RESULT = []
        for p in partial:
            if ((str(p).startswith('DMC-HON') or str(p).startswith('PMC-HON'))
                and (str(p).endswith('.xml') or str(p).endswith('.XML'))):
                RESULT.append(p)
        return RESULT
        
class LogBuilder():

    def build_log(self, rootdir: pathlib.Path, name:str, mode:str):
        os.chdir(rootdir)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('[%(levelname)s]: [%(message)s]')
        filehandler = logging.FileHandler(name, mode)
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(formatter)

        streamhandler = logging.StreamHandler()
        streamhandler.setFormatter(formatter)

        logger.addHandler(filehandler)
        logger.addHandler(streamhandler)
        return logger