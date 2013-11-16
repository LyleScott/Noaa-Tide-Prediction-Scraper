"""
Copyright 2013 Lyle Scott, III
lyle@digitalfoo.net
"""
import os
from lxml import html
from lxml import etree
from urllib import urlencode


URLS = {'root': 'http://tidesandcurrents.noaa.gov'}
URLS.update({
    'tide_predictions': '%s/tide_predictions.shtml' % URLS['root'],
})


def get_regions():
    """Scrape the regions from the main prediction page.

    :returns: Yields (label, url) tuples.
     The labels are the region (ie, East Coast).
     The urls are to the region's page that lists all the subregions and places.
    """
    doc = html.parse('%s' % URLS['tide_predictions'])
    regions = doc.xpath(
        '//li[preceding-sibling::li[@class="nav-header" and text()="Regions"]]/'
        '/a')
    for region in regions:
        label = region.text
        gid = region.get('href').split('#')[0]
        url = '%s%s' % (URLS['tide_predictions'], gid)
        yield (label, url)


def create_root_nodes(node):
    """Create the subareas and places nodes.

    :param node: The parent node to add children to.
    """
    etree.SubElement(node, 'subareas')
    etree.SubElement(node, 'places')


def parse_areas(regions):
    """Parse the areas and regions into an XML tree.

    :param regions: The region names and urls to scrape to build the children
      nodes which will represent sub areas and places.

    :returns: lxml.Element representing the root node that all children belong
      to.
    """

    root_node = etree.Element('root')

    for name, url in regions:
        print name, url

        region_node = etree.SubElement(root_node, 'subrea', title=name)
        create_root_nodes(region_node)
        nbsp_map = {0: region_node}

        doc = html.parse(url)
        rows = doc.xpath("//div[@align='center']/table[@class='table']/tr")

        for row in rows:
            for tdi, tdnode in enumerate(row.xpath('td')):
                css_class = tdnode.attrib.get('class', None)
                if css_class == 'stn_name_hdr':
                    break
                elif css_class in ('grphdr1', 'grphdr2', 'grphdr3'):
                    create_header_node(tdnode, nbsp_map)
                    break
                else:
                    if tdi == 0:
                        place_node = get_place_node(tdnode, nbsp_map)
                    else:
                        edit_place_node(tdnode, tdi, place_node)
    return root_node


def create_header_node(tdnode, nbsp_map):
    """Create a heading node.

    :param td:
    :param nbsp_map:
    """
    text = tdnode.xpath('b')[0].text
    nbsp_count = text.count('&nbsp')
    text = text.replace('&nbsp', '').strip()
    i = nbsp_count - 2
    parent = nbsp_map[i]
    node = parent.xpath('subareas')[0]

    header = etree.SubElement(
        node, 'subarea', title=text)
    create_root_nodes(header)

    nbsp_map[nbsp_count] = header


def get_place_node(tdnode, nbsp_map):
    """Add attributes to a place node.

    :param td: The <td/> node that contains the place text.
    :param nbsp_map: A map that defines what header belongs to what level.
    """
    text = tdnode.text or ''
    link = tdnode.xpath('a')[0]
    i = text.count('&nbsp') - 2
    parent = nbsp_map[i].xpath('places')[0]
    href = '%s%s' % (URLS['root'], link.attrib['href'])
    node = etree.SubElement(
        parent, 'place', location=link.text, url=href)

    predictions_node = etree.SubElement(node, 'predictions')
    get_predictions(href)

    return node


def edit_place_node(tdnode, tdi, node):
    """Create a place node.

    :param td: The <td/> node that contains the place text.
    :param nbsp_map: A map that defines what header belongs to what level.
    :param tdi: An integer counter that represents the index of the current td.
    :param node: The place node to add info to.
    """
    text = tdnode.text or ''

    if tdi == 1:
        key = 'stationid'
    elif tdi == 2:
        key = 'latitude'
    elif tdi == 3:
        key = 'longitude'
    elif tdi == 4:
        key = 'predictions'

    node.attrib.update({key: text.strip()})


def get_predictions(url):
    """Get the predictions XML file for the URL.

    :param url: The URL that provides the station's info.
    """
    # To download the XML file, you need to submit a GET form.
    doc = html.parse(url)
    vals = {}
    for field in doc.xpath('//input[@type="hidden"]'):
        name = field.attrib.get('name')
        if name == 'utf8':
            continue
        value = field.attrib.get('value')
        vals[name] = value
    vals['datatype'] = 'Annual XML'

    file_url = '%s&%s' % (url, urlencode(vals))
    doc = etree.parse(file_url)
    if not os.path.exists('xml'):
        os.mkdir('xml')
    write_to_xml(doc, filename='xml/%s.xml' % vals['Stationid'])


def write_to_xml(node, filename):
    """Write the XML tree to a file."""
    with open(filename, 'w') as xmlfile:
        xml = etree.tostring(node, pretty_print=True)
        xmlfile.write(xml)


def process():
    """Do work!"""
    regions = get_regions()
    root_node = parse_areas(regions)
    write_to_xml(root_node, filename='stations.xml')


if __name__ == '__main__':
    process()
