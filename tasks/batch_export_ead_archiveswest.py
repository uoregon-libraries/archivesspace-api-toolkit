from tasks.generic import GenericTask
from collections import OrderedDict
import copy
import json
import mechanize
import tempfile
from lxml import etree
import zipfile

# Batch export resources in EAD format. XML or PDF
class BatchExportEADArchiveswest(GenericTask):

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

    orbis_base_url = 'https://archiveswest.orbiscascade.org'
    br = mechanize.Browser()
    br.open(orbis_base_url + '/tools/Login.aspx?destination=%2ftools%2fAs2Aw.aspx')
    br.select_form('aspnetForm')
    br['ctl00$mainContentPlaceHolder$usernameTextBox'] = self.args.config['archiveswest_credentials']['username']
    br['ctl00$mainContentPlaceHolder$passwordTextBox'] = self.args.config['archiveswest_credentials']['password']
    br.submit()

    for resource_id in data:
      url = "/repositories/%s/resource_descriptions/%s.xml?include_unpublished=%s&include_daos=%s&numbered_cs=%s&ead3=%s"\
            % (repo_id, resource_id, options[0], options[1], options[2], options[3])
      # Export resource
      resp = super()._call(url, "get", None)
      as_xml = etree.fromstring(resp.text.encode('utf-8'))

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
        aw_archdesc = etree.SubElement(aw_xml, 'archdesc')
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

      # Update ArchivesWest resource title & append finding aid location
      title = aw_xml.find('archdesc/did/unittitle', namespaces).text
      if isinstance(title, str):
        resource_uri = 'https://scua.uoregon.edu/repositories/%s/resources/%s' % (repo_id, resource_id)

        # Grab and reset archdesc/did/unittitle
        subtree = aw_xml.find('archdesc/did/unittitle', namespaces)
        subtree.clear()

        # Add <extref> to <unittitle>
        subtree = etree.SubElement(subtree, 'extref')
        subtree.text = title
        subtree.attrib['{%s}title' % (namespaces['xlink'])] = title.replace(' ', '-')
        subtree.attrib['{%s}show' % (namespaces['xlink'])] = 'new'
        subtree.attrib['{%s}href' % (namespaces['xlink'])] = resource_uri
        subtree.attrib['{%s}actuate' % (namespaces['xlink'])] = 'onrequest'

        paragraphs = aw_xml.findall('archdesc/accessrestrict/p', namespaces)
        subtree = aw_xml.find('archdesc/accessrestrict', namespaces)
        if paragraphs:
          extref = paragraphs[-1].find('extref')
        # No paragraphs or the last paragraph does not contain a link or the last paragraph's link is not the right link
        if not paragraphs or not extref or extref.attrib['{%s}href' % (namespaces['xlink'])] != resource_uri:
          # Add <p> tag
          subtree = etree.SubElement(subtree, 'p')
          # Add <emph> to <p>
          emph = etree.SubElement(subtree, 'emph')
          emph.text = 'UO Finding Aid:'
          emph.set('render', 'bold')

          # Add <extref> to <p>
          extref = etree.SubElement(subtree, 'extref')
          extref.text = 'Guide to %s' % (title)
          extref.attrib['{%s}title' % (namespaces['xlink'])] = title.replace(' ', '-')
          extref.attrib['{%s}show' % (namespaces['xlink'])] = 'new'
          extref.attrib['{%s}href' % (namespaces['xlink'])] = resource_uri
          extref.attrib['{%s}actuate' % (namespaces['xlink'])] = 'onrequest'

      # Temporarily write file to upload to AS to AW converter
      with tempfile.NamedTemporaryFile(mode='w+b', suffix='.xml') as tmp:
        tmp.write(etree.tostring(aw_xml))
        tmp.seek(0)

        # Convert temporary file
        br.select_form('aspnetForm')
        br.add_file(tmp, 'text/xml', '%s.xml' % (resource_id))
        br.submit()

        tmp.close()

      # Retrieve converted file and write out again
      filename = 'out/%s.xml' %(resource_id)
      try:
        src = br.find_link('Click this link to download a zip file containing the converted document.')
        # Download zip and unzip in output directory
        filename = "%s.zip" % (filename)
        br.retrieve(orbis_base_url + src.url, filename)
        with zipfile.ZipFile(filename, 'r') as zip_ref:
          zip_ref.extractall('out/')
      except mechanize._mechanize.LinkNotFoundError as e:
        # No download link so lets just output the closest we can get to pre-conversion.
        with open(filename, mode="wb") as file:
          file.write(etree.tostring(aw_xml, pretty_print=True))
          file.close()
        with open(filename+'.origas_xml', mode="wb") as file:
          file.write(etree.tostring(as_xml, pretty_print=True))
          file.close()

  # Menu prompt
  def prompt(self):
    return "Batch export resources as EAD for ArchivesWest"

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