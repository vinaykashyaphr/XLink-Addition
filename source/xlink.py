import glob
import logging
import os
import pathlib
import sys

from lxml import etree

from common_functions import (Exclusion, LogBuilder, NameAndCode, Refresh_DMC,
                              Write_DMC)
from validateEntities import valent


class ElementXlinkAddition():

    def add_element_xlink(self, filename: str, folderpath: pathlib.Path,
                          xmlparser: etree.XMLParser, dmroot: etree._Element, logger: logging.Logger):

        content = dmroot.find('.//content')
        references = content.findall('.//dmRef/[@referredFragment]')

        for reference in references:
            fragment = reference.attrib['referredFragment']
            target_dm_name = NameAndCode().name_from_dmcode(
                reference.find('.//dmCode').attrib)
            ref_dmc = glob.glob("{0}*".format(target_dm_name))[0]

            if ref_dmc != []:
                target_dm = valent(ref_dmc, folderpath)
                target_root = etree.parse(target_dm, xmlparser).getroot()
                target_list = target_root.findall('.//content//*/[@id]')

                for target in target_list:
                    if target.attrib['id'] == fragment:
                        if target.tag == 'figure':
                            try:
                                fig_title = "".join(
                                    target.find('title').itertext())
                                fig_num = int(
                                    str(target.attrib['id']).replace('fig-', ''))
                                fig_xlink = 'Figure {0} - '.format(
                                    fig_num) + fig_title
                                reference.attrib['{http://www.w3.org/1999/xlink}title'] = fig_xlink
                                logger.info(
                                    "Adding Xlink: {0}".format(fig_xlink))
                            except AttributeError:
                                pass

                        elif target.tag == 'table':
                            try:
                                tab_title = "".join(
                                    target.find('title').itertext())
                                tab_num = int(
                                    str(target.attrib['id']).replace('tab-', ''))
                                tab_xlink = 'Table {0} - '.format(
                                    tab_num) + tab_title
                                reference.attrib['{http://www.w3.org/1999/xlink}title'] = tab_xlink
                                logger.info(
                                    "Adding Xlink: {0}".format(tab_xlink))
                            except AttributeError:
                                pass

                        elif (target.tag == 'para') or (target.tag == 'proceduralStep') or (target.tag == 'levelledPara'):
                            para_name = '({0})'.format(target_dm_name)
                            reference.attrib['{http://www.w3.org/1999/xlink}title'] = para_name
                            logger.info("Adding Xlink: {0}".format(para_name))
        Write_DMC(dmroot, filename, folderpath)

    def add_urn(self, filename: str, folderpath: pathlib.Path,
                dmroot: etree._Element, logger: logging.Logger):
        all_dmrefs = dmroot.findall('.//dmRef')

        URN = ['DMC-HONAERO-A-00-00-00-01A-0A4A-D',
               'DMC-HONAERO-A-00-00-00-02A-0A5A-D',
               'DMC-HONAERO-A-00-00-00-00A-00LA-D',
               'DMC-HONAERO-A-00-00-00-00A-00NA-D']

        for dmref in all_dmrefs:
            dmcode = dmref.find('.//dmCode')
            ref_dm_name = NameAndCode().name_from_dmcode(dmcode.attrib)
            if ref_dm_name in URN:
                urn = 'URN:S1000D:{0}'.format(ref_dm_name)
                dmref.attrib['{http://www.w3.org/1999/xlink}actuate'] = 'onRequest'
                dmref.attrib['{http://www.w3.org/1999/xlink}href'] = urn
                dmref.attrib['{http://www.w3.org/1999/xlink}show'] = 'replace'
                dmref.attrib['{http://www.w3.org/1999/xlink}type'] = 'simple'
                logger.info("URN added: {0}".format(urn))
        Write_DMC(dmroot, filename, folderpath)


class Commencement():
    def start(self, folderpath: pathlib.Path, all_files: list,
                 logger: logging.Logger, choice: str):
        Refresh_DMC().refresh(folderpath, logger)
        for file in all_files:
            if file.startswith('DMC-HON') and (file.endswith('.xml') or file.endswith('.XML')):
                dmc = valent(file, folderpath)
                par = etree.XMLParser(no_network=True, recover=True)
                dmroot = etree.parse(dmc, par).getroot()
                logger.info('Parsing '+dmc)
                if choice == 'xlink':
                    ElementXlinkAddition().add_element_xlink(dmc, folderpath, par, dmroot, log)
                elif choice == 'urn':
                    ElementXlinkAddition().add_urn(dmc, folderpath, dmroot, log)
                else:
                    ElementXlinkAddition().add_element_xlink(dmc, folderpath, par, dmroot, log)
                    ElementXlinkAddition().add_urn(dmc, folderpath, dmroot, log)


inputpath = pathlib.Path(sys.argv[1])  # input('Path:  '))
os.chdir(inputpath)
selection = str(sys.argv[2])  # 'xlink'
files_list = Exclusion().parsable_list(inputpath)
log = LogBuilder().build_log(inputpath, 'xlink_addition.log', 'w')
Commencement().start(inputpath, files_list, log, selection)
# os.system('pause')
