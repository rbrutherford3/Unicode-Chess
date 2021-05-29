DROP DATABASE IF EXISTS `chess`;
CREATE DATABASE `chess`;
DROP USER IF EXISTS `chessplayer`@localhost;
CREATE USER `chessplayer`@localhost IDENTIFIED BY 'time4chess!';
GRANT SELECT, INSERT ON `chess`.* TO `chessplayer`@localhost;
FLUSH PRIVILEGES;

DROP TABLE IF EXISTS `chess`.`moves`;
CREATE TABLE `chess`.`moves` (
  `id` int(8) NOT NULL AUTO_INCREMENT,
  `player` tinyint(1) DEFAULT NULL,
  `row1` tinyint(1) NOT NULL,
  `col1` tinyint(1) NOT NULL,
  `row2` tinyint(1) NOT NULL,
  `col2` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=112 DEFAULT CHARSET=utf8mb4;
