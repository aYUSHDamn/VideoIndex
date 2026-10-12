-- Run this file in MySQL Workbench before running the Python importer.
CREATE DATABASE IF NOT EXISTS video_index_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE video_index_db;

CREATE TABLE IF NOT EXISTS users (
  user_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  username VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id),
  UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS channels (
  channel_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  channel_name VARCHAR(150) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (channel_id),
  UNIQUE KEY uq_channels_user_name (user_id, channel_name),
  CONSTRAINT fk_channels_user
    FOREIGN KEY (user_id) REFERENCES users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categories (
  category_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  category_name VARCHAR(100) NOT NULL,
  PRIMARY KEY (category_id),
  UNIQUE KEY uq_categories_name (category_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS videos (
  video_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  channel_id INT UNSIGNED NOT NULL,
  category_id INT UNSIGNED NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT NULL,
  language VARCHAR(20) NULL,
  duration INT UNSIGNED NOT NULL COMMENT 'Duration in whole seconds',
  views BIGINT UNSIGNED NOT NULL DEFAULT 0,
  is_public BOOLEAN NOT NULL DEFAULT FALSE,
  uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  video_path VARCHAR(512) NOT NULL,
  audio_path VARCHAR(512) NOT NULL,
  transcript LONGTEXT NOT NULL,
  PRIMARY KEY (video_id),
  UNIQUE KEY uq_videos_video_path (video_path),
  KEY ix_videos_channel_id (channel_id),
  KEY ix_videos_category_id (category_id),
  CONSTRAINT fk_videos_channel
    FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_videos_category
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
    ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS comments (
  comment_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  video_id INT UNSIGNED NOT NULL,
  user_id INT UNSIGNED NOT NULL,
  comment_text TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (comment_id),
  KEY ix_comments_video_id (video_id),
  KEY ix_comments_user_id (user_id),
  CONSTRAINT fk_comments_video
    FOREIGN KEY (video_id) REFERENCES videos (video_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_comments_user
    FOREIGN KEY (user_id) REFERENCES users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS watch_history (
  history_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  video_id INT UNSIGNED NOT NULL,
  watched_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  watch_duration INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Watched duration in seconds',
  PRIMARY KEY (history_id),
  KEY ix_watch_history_user_id (user_id),
  KEY ix_watch_history_video_id (video_id),
  CONSTRAINT fk_watch_history_user
    FOREIGN KEY (user_id) REFERENCES users (user_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_watch_history_video
    FOREIGN KEY (video_id) REFERENCES videos (video_id)
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tags (
  tag_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  tag_name VARCHAR(100) NOT NULL,
  PRIMARY KEY (tag_id),
  UNIQUE KEY uq_tags_name (tag_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS video_tags (
  video_id INT UNSIGNED NOT NULL,
  tag_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (video_id, tag_id),
  CONSTRAINT fk_video_tags_video
    FOREIGN KEY (video_id) REFERENCES videos (video_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_video_tags_tag
    FOREIGN KEY (tag_id) REFERENCES tags (tag_id)
    ON DELETE CASCADE
) ENGINE=InnoDB;
