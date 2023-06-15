from lxml import etree

XML = '''
<A xlink:show="replace" xlink:type="simple">
    <B foo="123">
        <C>thing</C>
        <D>stuff</D>
    </B>
</A>'''

XSLT = '''
<xsl:stylesheet version="1.0"
     xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
     xmlns:ns1="www.example.com">
 <xsl:output method="xml" indent="yes" omit-xml-declaration="yes"/>

  <xsl:template match="*">
   <xsl:element name="ns1:{name()}">
    <xsl:apply-templates select="node()|@*"/>
   </xsl:element>
  </xsl:template>

  <!-- No prefix on the A element -->
  <xsl:template match="A">
   <A xmlns:ns1="www.example.com">
    <xsl:apply-templates select="node()|@*"/>
   </A>
  </xsl:template>
</xsl:stylesheet>'''

xml_doc = etree.fromstring(XML)
xslt_doc = etree.fromstring(XSLT)
transform = etree.XSLT(xslt_doc)
print(transform(xml_doc))