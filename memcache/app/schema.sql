DROP TABLE IF EXISTS cache_config;
DROP TABLE IF EXISTS cache_stats;

CREATE TABLE cache_config (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  capacity INTEGER NOT NULL,
  replacement_policy TEXT NOT NULL
);

CREATE TABLE cache_stats (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  cache_count INTEGER NOT NULL,
  cache_size FLOAT NOT NULL,
  miss_rate FLOAT NOT NULL,
  hit_rate FLOAT NOT NULL,
  requests_served INTEGER NOT NULL
);
