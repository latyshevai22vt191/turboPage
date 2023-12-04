s = """
<country name="Liechtenstein">
    <year>2008</year>
    <gdppc>141100</gdppc>
</country>
"""
import xml.etree.ElementTree as ET
doc = ET.ElementTree(ET.fromstring(s))

outFile = open('output.xml', 'w')
doc.write(outFile.buffer)             # <--- buffer here
outFile.close()