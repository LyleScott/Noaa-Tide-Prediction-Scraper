# Lyle Scott, III  // lyle@digitalfoo.net // Copyright 2013

import re
from lxml import etree
from lxml import html


RE_STATION_ID = re.compile(
    r'<tr><td><a href="data_menu.shtml\?stn=([0-9]+) ([^&]+)')

URLS = {'root': 'http://tidesandcurrents.noaa.gov'}
URLS.update({
    'tide_predictions': '%s/tide_predictions.shtml' % URLS['root'],
})

DEBUG = True


def get_regions():
    """Create a dict stucture initialized with regions and the links to states.
    """
    doc = html.parse(URLS['tide_predictions'])
    tables = doc.xpath(
        "//div[@align='center']/table/tr/td/table[@class='table']")
    data = {}
    heading_map = {}

    for table in tables:
        rows = table.xpath('tr')

        for i, heading in enumerate(rows[0].xpath('th')):
            data[heading.text] = []
            heading_map[i] = heading.text

        for row in rows[1:]:
            for i, cell in enumerate(row.xpath('td')):
                a = cell.xpath('a')
                if not a:
                    continue
                a = a[0]
                data[heading_map[i]].append((a.text, a.attrib['href']))
        #break

    return data


def create_root_nodes(parent):
    """Create the subareas and places nodes.

    :param parent: The parent node to add children to.
    """
    etree.SubElement(parent, 'subareas')
    etree.SubElement(parent, 'places')


def create_header_node(td, nbsp_map):
    """

    :param td:
    :param nbsp_map:
    """
    text = td.xpath('b')[0].text
    nbsp_count = text.count('&nbsp')
    text = text.replace('&nbsp', '').strip()
    i = nbsp_count - 2
    parent = nbsp_map[i]
    node = parent.xpath('subareas')[0]

    header = etree.SubElement(
        node, 'subarea', title=text)
    create_root_nodes(header)

    nbsp_map[nbsp_count] = header


def get_place_node(td, nbsp_map):
    """Add attributes to a place node.

    :param td: The <td/> node that contains the place text.
    :param nbsp_map: A map that defines what header belongs to what level.
    """
    text = td.text or ''
    link = td.xpath('a')[0]
    i = text.count('&nbsp') - 2
    parent = nbsp_map[i].xpath('places')[0]
    href = '%s%s' % (URLS['root'], link.attrib['href'])
    node = etree.SubElement(
        parent, 'place', location=link.text, url=href)
    return node


def edit_place_node(td, nbsp_map, tdi, node):
    """Create a place node.

    :param td: The <td/> node that contains the place text.
    :param nbsp_map: A map that defines what header belongs to what level.
    :param tdi: An integer counter that represents the index of the current td.
    :param node: The place node to add info to.
    """
    text = td.text or ''

    if tdi == 1:
        key = 'stationid'
    elif tdi == 2:
        key = 'latitude'
    elif tdi == 3:
        key = 'longitude'
    elif tdi == 4:
        key = 'predictions'

    node.attrib.update({key: text.strip()})


def get_state_data(region_node, state, gidurl):
    """Create the state node and generate the url.

    :param region_node: The parent node to add the subregion child node to.
    :param state: The US state label on the new node.
    :param gidurl: The gid GET parameter in the form of "gid=XXX"..

    :returns: A tuple of (state_node, state_url)
    """
    gid = gidurl.split('=')[1]
    state_url = '%s%s' % (URLS['tide_predictions'], gidurl)
    if DEBUG:
        print('state_url:', state_url)

    state_node = etree.SubElement(
        region_node, 'state', title=state, gid=gid, url=state_url)

    return (state_node, state_url)


def get_data(regions):
    """

    :param regions:
    """
    root = etree.Element('regions')

    for region in regions:
        region_node = etree.SubElement(root, 'region', title=region)

        for state, gidurl in regions[region]:

            state_node, state_url = get_state_data(region_node, state, gidurl)
            create_root_nodes(state_node)
            nbsp_map = {0: state_node}
            place_node = None

            doc = html.parse(state_url)
            rows = doc.xpath("//div[@align='center']/table[@class='table']/tr")

            for row in rows:
                for tdi, td in enumerate(row.xpath('td')):
                    css_class = td.attrib.get('class', None)
                    if css_class == 'stn_name_hdr':
                        break
                    elif css_class in ('grphdr1', 'grphdr2'):
                        create_header_node(td, nbsp_map)
                        break
                    else:
                        if tdi == 0:
                            place_node = get_place_node(td, nbsp_map)
                        else:
                            edit_place_node(td, nbsp_map, tdi, place_node)
            #break
    return root


def save_to_xml(root, filename=None, pretty_print=True):
    """Save the XML tree to a file.

    :param root: The root node of the XML tree to traverse.
    :param filename: The filename to write the XML to.
    :param pretty_print: Opt. Pretty print the XML tree. Defaults to True.
    """
    if filename is None:
        filename = '/tmp/regions.xml'

    xml = etree.tostring(root, pretty_print=pretty_print).decode('utf8')

    with open(filename, 'w') as fp:
        fp.write(xml)


if __name__ == '__main__':
    save_to_xml(get_data(get_regions()))
