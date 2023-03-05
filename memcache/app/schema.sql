DROP DATABASE IF EXISTS image_key;

CREATE DATABASE image_key;

USE image_key;

DROP TABLE IF EXISTS image_key_table1;
DROP TABLE IF EXISTS cache_config;
DROP TABLE IF EXISTS cache_stats;

CREATE TABLE image_key_table1 (image_key VARCHAR(255)) ;


CREATE TABLE cache_config (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  capacity FLOAT NOT NULL,
  replacement_policy TEXT NOT NULL
);

CREATE TABLE cache_status (
  id INTEGER PRIMARY KEY,
  is_active BOOLEAN NOT NULL,
  cache_host TEXT NOT NULL,
  last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

/* NOTE: The cache_config table must contain at least one initial entry when the memcache app is started in order to
configure the MemCache object. */
INSERT INTO cache_config (capacity, replacement_policy) VALUES (50, 'RR');
