<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/user_data">
    <validated_data>
      <xsl:for-each select="item">
        <item>
          <xsl:copy-of select="name"/>
          <xsl:copy-of select="email"/>
          <xsl:copy-of select="address"/>
          <xsl:copy-of select="date_of_birth"/>
          <xsl:copy-of select="phone_number"/>
          <xsl:copy-of select="job"/>
          <xsl:copy-of select="company"/>
          <validation>
            <xsl:if test="not(contains(email, '@')) or not(contains(email, '.'))">
              <error>Email некорректен</error>
            </xsl:if>
            <xsl:if test="string-length(address) &lt; 5">
              <error>Адрес некорректен</error>
            </xsl:if>
            <xsl:if test="not(contains(date_of_birth, '-')) or string-length(date_of_birth) != 10">
              <error>Дата рождения некорректна (формат YYYY-MM-DD)</error>
            </xsl:if>
            <xsl:variable name="birth_year"
              select="number(substring(date_of_birth,1,4))"/>
            <xsl:if test="number($birth_year) &lt; 1925 or number($birth_year) &gt; 2007">
              <error>Возраст вне диапазона 18–100 лет</error>
            </xsl:if>
            <xsl:if test="not(contains(phone_number, '-'))">
              <error>Телефон некорректен (ожидается формат с дефисами)</error>
            </xsl:if>
          </validation>
        </item>
      </xsl:for-each>
    </validated_data>
  </xsl:template>

</xsl:stylesheet>
