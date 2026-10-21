<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    exclude-result-prefixes="xs math"
    version="3.0">
    <xsl:output method="xml" indent="1" encoding="UTF-8"/>

    <xsl:param name="collection-id" select="concat('temp', substring(string(current-dateTime()), 1, 16))"/>    
    <xsl:param name="types-to-ignore" select="('**no file**', 'photo dupes', 'images available')" as="item()+"/>
    <xsl:param name="default-extent-number" select="0" as="xs:decimal"/>
    <xsl:param name="default-extent-type" select="'linear_feet'" as="xs:string"/>
    
    <xsl:param name="series-file" select="doc('series.xml')"/>
    <xsl:param name="holdings-file" select="doc('holdings.xml')"/>
    
    <xsl:template name="xsl:initial-template" match="/">
        <xsl:call-template name="ead"/>
    </xsl:template>
    
    <xsl:template name="dsc">
        <dsc xmlns="urn:isbn:1-931666-22-9">
            <xsl:for-each select="$series-file/root">
                <xsl:apply-templates select="row[string-length(Series_prefix) eq 2]" mode="grouping-row">
                    <xsl:with-param name="level" select="'series'"/>
                </xsl:apply-templates>
            </xsl:for-each>
        </dsc>
    </xsl:template>
      
    <xsl:template match="row" mode="grouping-row">
        <xsl:param name="level" as="xs:string"/>
        <xsl:variable name="current-prefix" select="Series_prefix"/>
        <c level="{$level}" xmlns="urn:isbn:1-931666-22-9">
            <did>
                <unitid>
                    <xsl:apply-templates select="Series_prefix"/>
                </unitid>
                <unittitle>
                    <xsl:value-of select="Tech_Files_series => normalize-space()"/>
                </unittitle>
            </did>
            <!-- create notes -->
            <xsl:apply-templates select="_Series_Description_[normalize-space()]"/>
            <!-- create subseries, if any, from series.xml file -->
            <xsl:apply-templates select="following-sibling::row[starts-with(Series_prefix, $current-prefix)]" mode="#current">
                <xsl:with-param name="level" select="'subseries'"/>
            </xsl:apply-templates>
            <!-- create the file-level children / holdings -->
            <xsl:call-template name="components">
                <xsl:with-param name="current-prefix" select="$current-prefix"/>
            </xsl:call-template>
        </c>
    </xsl:template>
    
    <xsl:template name="components">
        <xsl:param name="current-prefix"/>
        <xsl:for-each select="$holdings-file/root/row[holdings_subjects_categories_SERIES_Series_prefix eq $current-prefix][not(lower-case(Material_type) = $types-to-ignore)]">         
            <xsl:for-each-group select="." group-by="holdings_subjects_CATEGORIES_Category"> 
                <xsl:apply-templates select="current-group()" mode="holding"/>
            </xsl:for-each-group>  
        </xsl:for-each>
    </xsl:template>
    
    <xsl:template match="row" mode="holding">
        <c level="file" xmlns="urn:isbn:1-931666-22-9">
            <did>
                <unitid>
                    <xsl:apply-templates select="calc_Filing_code"/>
                </unitid>
                <unittitle>
                    <xsl:value-of select="holdings_SUBJECTS_Subject || ' [' || Material_type || ']' => normalize-space()"/>
                </unittitle>
            </did>
            <xsl:apply-templates select="Notes[normalize-space()]"/>
        </c>
    </xsl:template>
    
    <xsl:template match="Notes | _Series_Description_">
        <scopecontent xmlns="urn:isbn:1-931666-22-9">
            <p>
                <xsl:apply-templates/>
            </p>
        </scopecontent>
    </xsl:template>
    
    <!-- main, EAD stuff... not interesting, since we just use as a shell to impport -->
    <xsl:template name="ead">
        <ead xmlns="urn:isbn:1-931666-22-9"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="urn:isbn:1-931666-22-9 https://www.loc.gov/ead/ead.xsd">
            <eadheader>
                <eadid>
                    <xsl:value-of select="$collection-id"/>
                </eadid>
                <filedesc>
                    <titlestmt>
                        <titleproper/>
                    </titlestmt>
                </filedesc>
            </eadheader>
            <archdesc level="collection">
                <did>
                    <unitid>
                        <xsl:value-of select="$collection-id"/>
                    </unitid>
                    <unitdate>undated</unitdate>
                    <unittitle>collection title</unittitle>
                    <physdesc>
                        <extent>
                            <xsl:value-of select="concat($default-extent-number, ' ', $default-extent-type)"/>
                        </extent>
                    </physdesc>
                    <langmaterial>
                        <language langcode="eng"/>
                    </langmaterial>
                </did>
                <xsl:call-template name="dsc"/>
            </archdesc>
        </ead>
    </xsl:template>
    
</xsl:stylesheet>
