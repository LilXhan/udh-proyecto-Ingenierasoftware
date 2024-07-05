
CREATE DATABASE dbCentrosTuristicos;

USE dbCentrosTuristicos;

DROP TABLE servicios;

CREATE TABLE IF NOT EXISTS `servicios` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255),
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `usuarios` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255),
  `apellidos` VARCHAR(255),
  `email` VARCHAR(255) UNIQUE NOT NULL,
  `contraseña` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `establecimientos` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255),
  `ubicacion` VARCHAR(255),
  `responsable` VARCHAR(255),
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `establecimiento_servicio` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `establecimiento_id` INT(11) NOT NULL,
  `servicio_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `establecimiento_id` (`establecimiento_id`),
  KEY `servicio_id` (`servicio_id`),
  CONSTRAINT `fk_establecimiento` FOREIGN KEY (`establecimiento_id`) REFERENCES `establecimientos` (`id`),
  CONSTRAINT `fk_servicio` FOREIGN KEY (`servicio_id`) REFERENCES `servicios` (`id`)
);


INSERT INTO `servicios` (`nombre`) VALUES 
('Restaurante'),
('Recreo Turístico'),
('Cafetería'),
('Sándwiches');

INSERT INTO `establecimientos` (`nombre`, `ubicacion`, `responsable`) VALUES 
('Recreo Falcón', 'Jirón 2 de Mayo, 190, Huánuco', 'Juan Pérez'),
('La Casona Huanuqueña', 'Parque Amarilis, Huánuco', 'María López'),
('Cafe San Ignacio', 'Jirón Bolívar 308, Huánuco', 'Luis Gutiérrez'),
('Facucho', 'Jirón 2 de Mayo 871, Huánuco', 'Ana Rodríguez');

INSERT INTO `establecimiento_servicio` (`establecimiento_id`, `servicio_id`) VALUES 
(1, 2),
(1, 1),
(2, 1),
(3, 3),
(3, 1),
(4, 4),
(4, 3);

SELECT * FROM establecimiento_servicio;




