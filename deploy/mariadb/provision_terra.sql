-- Least-privilege MariaDB provisioning script for Terra Physics Lab (Debian 13)
-- Usage:
--   sudo mariadb < deploy/mariadb/provision_terra.sql
--   (Replace CHANGE_ME_STRONG_RANDOM_PASSWORD before executing)

CREATE DATABASE IF NOT EXISTS terra
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'terra_app'@'localhost'
  IDENTIFIED BY 'CHANGE_ME_STRONG_RANDOM_PASSWORD';

CREATE USER IF NOT EXISTS 'terra_app'@'127.0.0.1'
  IDENTIFIED BY 'CHANGE_ME_STRONG_RANDOM_PASSWORD';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX
  ON terra.* TO 'terra_app'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX
  ON terra.* TO 'terra_app'@'127.0.0.1';

FLUSH PRIVILEGES;
