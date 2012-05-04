CREATE TABLE IF NOT EXISTS `books` (
  `Id` bigint(20) NOT NULL AUTO_INCREMENT,
  `Title` varchar(600) COLLATE utf8_unicode_ci NOT NULL,
  `Authors` varchar(600) COLLATE utf8_unicode_ci NOT NULL,
  `Description` mediumtext COLLATE utf8_unicode_ci NOT NULL,
  `Thumbnail` varchar(450) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `files` (
  `Id` bigint(20) NOT NULL AUTO_INCREMENT,
  `Format` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `BookId` bigint(20) NOT NULL,
  `Url` varchar(700) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;