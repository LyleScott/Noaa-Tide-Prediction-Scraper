# Lyle Scott, III  // lyle@digitalfoo.net // Copyright 2013

import re
from lxml import html, etree


RE_STATION_ID = re.compile(r'<tr><td><a href="data_menu.shtml\?stn=([0-9]+) ([^&]+)')

URLS = {'root': 'http://tidesandcurrents.noaa.gov'}
URLS.update({
    'tide_predictions': '%s/tide_predictions.shtml' % URLS['root'],
})

DEBUG = True


def get_data_headings():
    doc = html.parse(URLS['tide_predictions'])
    tables = doc.xpath("//div[@align='center']/table/tr/td/table[@class='table']")
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
        break

    return data


def replace_nbsp(text):
    return text.replace('&nbsp', '').strip()


def get_data(regions):
    root = etree.Element('regions')

    for region in regions:

        region_node = etree.SubElement(root, 'region', title=region)

        for state, gidurl in regions[region]:

            if gidurl != '?gid=62':
                continue

            gid = gidurl.split('=')[1]
            subregion_node = etree.SubElement(region_node, 'subregion', title=state, gid=gid)
            subregion_url = '%s%s' % (URLS['tide_predictions'], gidurl)

            if DEBUG:
                print('subregion_url:', subregion_url)

            doc = html.parse(subregion_url)
            nbsp_count_prev = 0

            for row in doc.xpath("//div[@align='center']/table[@class='table']/tr"):

                for tdi, td in enumerate(row.xpath('td')):
                    css_class = td.attrib.get('class', None)

                    if css_class == 'stn_name_hdr':
                        continue
                    elif css_class == 'grphdr1':
                        text = replace_nbsp(td.xpath('b')[0].text)
                        header = etree.SubElement(subregion_node, 'subheading', title=text)
                        break
                    elif css_class == 'grphdr2':
                        text = replace_nbsp(td.xpath('b')[0].text)
                        prev_header = header
                        header = etree.SubElement(header, 'subheading', title=text)
                        break

                    text = td.text or ''

                    if tdi == 0:
                        link = td.xpath('a')

                        nbsp_count_new = text.count('&nbsp')
                        if nbsp_count_new < nbsp_count_prev:
                            header = prev_header
                        nbsp_count_prev = nbsp_count_new

                        link = link[0]

                        node = etree.SubElement(header, 'link', location=link.text)
                    else:
                        if tdi == 1:
                            key = 'stationid'
                        if tdi == 2:
                            key = 'latitude'
                        if tdi == 3:
                            key = 'longitude'
                        if tdi == 4:
                            key = 'predictions'
                        node.attrib.update({key: text.strip()})
            break
    return root


def save_data(root):
    with open('/Users/lyle/Downloads/foo.xml', 'w') as fp:
        xml = etree.tostring(root, pretty_print=True).decode('utf8')
        fp.write(xml)



if __name__ == '__main__':
    save_data(get_data(get_data_headings()))