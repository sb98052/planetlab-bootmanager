<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:import href="http://docbook.sourceforge.net/release/xsl/current/fo/docbook.xsl"/>

<xsl:param name="header.rule" select="0"></xsl:param>
<xsl:param name="footer.rule" select="0"></xsl:param>
<xsl:param name="section.autolabel" select="1"></xsl:param>

<!-- more room for the titles at the top of each page -->
<xsl:param name="header.column.widths" select="'1 2 1'"></xsl:param>

<!-- remove revision history -->
<xsl:template match="revhistory" mode="titlepage.mode">
</xsl:template>

</xsl:stylesheet>
