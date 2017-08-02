-- Keeping this file to show that I did do the table setup manually, easier to rebuild with the export file though
CREATE DATABASE rv_database;

USE rv_database;

CREATE TABLE rv_states (
	id INT NOT NULL AUTO_INCREMENT,
	name VARCHAR(25),
	abbreviation VARCHAR(4),
	datetime_added DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
	last_updated DATETIME ON UPDATE CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE rv_cities(
	id INT NOT NULL AUTO_INCREMENT,
	name VARCHAR(50),
	state_id INT NOT NULL,
	status VARCHAR(15) DEFAULT 'unverified' NOT NULL,
	latitude VARCHAR(30),
	longitude VARCHAR(30),
	datetime_added DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
	last_updated DATETIME ON UPDATE CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (state_id) REFERENCES rv_states(id)
);

CREATE TABLE rv_users(
	id INT NOT NULL AUTO_INCREMENT,
	first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50) NOT NULL,
	datetime_added DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
	last_updated DATETIME ON UPDATE CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE rv_visits(
	id INT NOT NULL AUTO_INCREMENT,
	city_id INT NOT NULL,
	user_id INT NOT NULL,
	datetime_added DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (city_id) REFERENCES rv_cities(id),
	FOREIGN KEY (user_id) REFERENCES rv_users(id)
);