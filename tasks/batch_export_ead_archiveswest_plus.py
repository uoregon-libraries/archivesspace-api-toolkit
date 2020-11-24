from tasks.generic import GenericTask
from collections import OrderedDict
import copy
import json
import mechanize
import tempfile
from lxml import etree
import zipfile

# Batch export resources in EAD format. XML or PDF
class BatchExportEADArchiveswestPlus(GenericTask):

  def run(self):
    # Get repository ID
    while True:
      repo_id = self.repo_menu()
      if id:
        break

    while True:
      options = self.options_menu()
      if options:
        break

    while True:
      data = self.json_menu()
      if data:
        break

    for resource_id in data:
      url = "/repositories/%s/resource_descriptions/%s.xml?include_unpublished=%s&include_daos=%s&numbered_cs=%s&ead3=%s"\
            % (repo_id, resource_id, options[0], options[1], options[2], options[3])
      # Export resource
      resp = super()._call(url, "get", None)
      try:
        as_xml = etree.fromstring(resp.text.encode('utf-8'))
      except Exception as e:
        self.logger.exception('Could not parse received XML')
        continue

      # Build ArchivesWest XML
      namespaces = {
        None: 'urn:isbn:1-931666-22-9',
        'xlink': 'http://www.w3.org/1999/xlink'
      }
      aw_xml = etree.Element('ead', nsmap=namespaces)

      # Copy all ead attributes
      for key, value in dict(as_xml.attrib).items():
        aw_xml.attrib[key] = value
      aw_xml.tag = as_xml.tag

      # Keep ead/eadheader
      subtree = copy.deepcopy(as_xml.find('eadheader', namespaces))
      if subtree is not None:
        aw_xml.append(subtree)

      # Keep ead/control
      subtree = copy.deepcopy(as_xml.find('control', namespaces))
      if subtree is not None:
        aw_xml.append(subtree)

      # Copy all ead/archdesc and all its attributes attributes without copying its children
      subtree = as_xml.find('archdesc', namespaces)
      if subtree is not None:
        aw_archdesc = etree.SubElement(aw_xml, '{%s}archdesc' % (namespaces[None]))
        for key, value in dict(subtree.attrib).items():
          aw_archdesc.attrib[key] = value

      # Keep ead/archdesc/did
      subtree = copy.deepcopy(as_xml.find('archdesc/did', namespaces))
      if subtree is not None:
        aw_archdesc.append(subtree)

      # Keep ead/archdesc/accessrestrict
      subtree = copy.deepcopy(as_xml.find('archdesc/accessrestrict', namespaces))
      if subtree is not None:
        aw_archdesc.append(subtree)

      # Keep ead/archdesc/controlaccess
      subtree = copy.deepcopy(as_xml.find('archdesc/controlaccess', namespaces))
      if subtree is not None:
        aw_archdesc.append(subtree)

      # Keep ead/archdesc/otherfindaid
      subtree = copy.deepcopy(as_xml.find('archdesc/otherfindaid', namespaces))
      if subtree is not None:
        aw_archdesc.append(subtree)

      # Keep ead/archdesc/bioghist
      subtree = copy.deepcopy(as_xml.find('archdesc/bioghist', namespaces))
      if subtree is not None:
        aw_archdesc.append(subtree)

      # Keep ead/archdesc/scopecontent
      subtree = copy.deepcopy(as_xml.find('archdesc/scopecontent', namespaces))
      if subtree is not None:
        aw_archdesc.append(subtree)

      # Update ArchivesWest resource title & append finding aid location
      filedesc_title = aw_xml.findall('eadheader/filedesc/titlestmt/titleproper', namespaces)[-1].text
      archdesc_title = aw_xml.findall('archdesc/did/unittitle', namespaces)[-1].text
      resource_uri = 'https://scua.uoregon.edu/repositories/%s/resources/%s' % (repo_id, resource_id)
      if isinstance(archdesc_title, str):
        # Grab and reset archdesc/did/unittitle
        subtree = aw_xml.find('archdesc/did/unittitle', namespaces)
        subtree.clear()
        # Add <extref> to <unittitle>
        subtree = etree.SubElement(subtree, 'extref')
        subtree.text = archdesc_title
        subtree.attrib['{%s}title' % (namespaces['xlink'])] = archdesc_title.replace(' ', '-')
        subtree.attrib['{%s}show' % (namespaces['xlink'])] = 'new'
        subtree.attrib['{%s}href' % (namespaces['xlink'])] = resource_uri
        subtree.attrib['{%s}actuate' % (namespaces['xlink'])] = 'onrequest'

      if isinstance(filedesc_title, str):
        # Re-create archdesc/dsc/c01/did/unittitle
        subtree = aw_xml.find('archdesc', namespaces)
        subtree = etree.SubElement(subtree, 'dsc')
        subtree = etree.SubElement(subtree, 'c01')
        subtree.attrib['level'] = 'otherlevel'
        subtree.attrib['otherlevel'] = 'Heading'
        subtree = etree.SubElement(subtree, 'did')
        subtree = etree.SubElement(subtree, 'unittitle')
        # Add <extref> to <unittitle>
        subtree = etree.SubElement(subtree, 'extref')
        subtree.text = filedesc_title
        subtree.attrib['{%s}title' % (namespaces['xlink'])] = filedesc_title.replace(' ', '-')
        subtree.attrib['{%s}show' % (namespaces['xlink'])] = 'new'
        subtree.attrib['{%s}href' % (namespaces['xlink'])] = resource_uri
        subtree.attrib['{%s}actuate' % (namespaces['xlink'])] = 'onrequest'

      # Grab and append archdesc/otherfindaid
      subtree = aw_xml.find('archdesc', namespaces)
      subtree = etree.SubElement(subtree, 'otherfindaid')
      # Re-create archdesc/otherfindaid
      subtree = etree.SubElement(subtree, 'p')
      subtree = etree.SubElement(subtree, 'extref')
      subtree.text = 'See the Current Collection Guide for detailed description and requesting options.'
      subtree.attrib['{%s}title' % (namespaces['xlink'])] = 'see-current-collection-guide-and-requesting-options'
      subtree.attrib['{%s}show' % (namespaces['xlink'])] = 'new'
      subtree.attrib['{%s}href' % (namespaces['xlink'])] = resource_uri
      subtree.attrib['{%s}actuate' % (namespaces['xlink'])] = 'onrequest'

      # Retrieve converted file and write out again
      filename = 'out/%s.xml' %(resource_id)

      with open(filename, mode="wb") as file:
        file.write(etree.tostring(aw_xml, xml_declaration=True, encoding='UTF-8', pretty_print=True))
        file.close()
      with open(filename+'.orig', mode="wb") as file:
        file.write(etree.tostring(as_xml, xml_declaration=True, encoding='UTF-8', pretty_print=True))
        file.close()

  # Menu prompt
  def prompt(self):
    return "Batch export resources as EAD for ArchivesWest: With a Vengeance"

  # Query user for repository ID
  def repo_menu(self):
    print("Enter the repository ID to export from:")
    print("ie: 5")
    print("")
    try:
      id = input(">> ")
    except EOFError:
      return None
    return id if super()._confirm("Confirm ID: %s" % id) else None

  # Query user for export format
  def options_menu(self):
    unpublished = super()._confirm("Include unpublished records?")
    daos = super()._confirm("Include digital objects in dao tags?")
    tags = super()._confirm("Use numbered tags in ead?")
    ead = super()._confirm("Export using EAD3 schema?")
    ead = False
    return [unpublished, daos, tags, ead]
