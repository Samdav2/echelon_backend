-- ============================================================================
-- Database Schema for Ticket Booking System (Industry Standard)
-- Generated from SQLAlchemy ORM Models
-- ============================================================================

-- Create database if not exists
-- CREATE DATABASE IF NOT EXISTS `biznexco_appsamdavweb101`;
-- USE `biznexco_appsamdavweb101`;

-- ============================================================================
-- Table: user_credential
-- Purpose: User authentication and account information
-- ============================================================================
CREATE TABLE IF NOT EXISTS `user_credential` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL UNIQUE,
  `email` varchar(255) NOT NULL UNIQUE,
  `password` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uc_user_credential_email` (`email`),
  UNIQUE KEY `uc_user_credential_username` (`username`),
  INDEX `idx_email` (`email`),
  INDEX `idx_username` (`username`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='User authentication credentials table';

-- ============================================================================
-- Table: creatorprofile
-- Purpose: Creator/Event organizer profiles
-- ============================================================================
CREATE TABLE IF NOT EXISTS `creatorprofile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL UNIQUE,
  `name` varchar(255) NOT NULL,
  `phoneno` varchar(255) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `brandname` varchar(255) DEFAULT NULL,
  `email` varchar(255) NOT NULL UNIQUE,
  `bio` text DEFAULT NULL,
  `profile_picture` varchar(500) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uc_creatorprofile_user_id` (`user_id`),
  UNIQUE KEY `uc_creatorprofile_email` (`email`),
  FOREIGN KEY (`user_id`) REFERENCES `user_credential`(`id`) ON DELETE CASCADE,

  INDEX `idx_creator_user_id` (`user_id`),
  INDEX `idx_creator_email` (`email`),
  INDEX `idx_creator_brandname` (`brandname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Event creator and organizer profiles';

-- ============================================================================
-- Table: userprofiles
-- Purpose: Regular user profiles for event attendees
-- ============================================================================
CREATE TABLE IF NOT EXISTS `userprofiles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL UNIQUE,
  `name` varchar(255) NOT NULL,
  `phoneno` varchar(255) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `email` varchar(255) NOT NULL UNIQUE,
  `profile_picture` varchar(500) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uc_userprofiles_user_id` (`user_id`),
  UNIQUE KEY `uc_userprofiles_email` (`email`),
  FOREIGN KEY (`user_id`) REFERENCES `user_credential`(`id`) ON DELETE CASCADE,

  INDEX `idx_user_profile_user_id` (`user_id`),
  INDEX `idx_user_profile_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Regular user profiles for attendees';

-- ============================================================================
-- Table: eventcreation
-- Purpose: Event details, pricing, and payment information
-- ============================================================================
CREATE TABLE IF NOT EXISTS `eventcreation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11) DEFAULT NULL,
  `brand_name` varchar(255) DEFAULT NULL,
  `event_name` varchar(255) NOT NULL,
  `event_address` varchar(255) NOT NULL,
  `time_in` time DEFAULT NULL,
  `time_out` time DEFAULT NULL,
  `summary` text DEFAULT NULL,
  `picture` varchar(500) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL CHECK (`price` >= 0),
  `category` varchar(255) NOT NULL,
  `date` date NOT NULL,

  -- Bank information
  `account_name` varchar(255) DEFAULT NULL,
  `account_number` varchar(255) DEFAULT NULL,
  `bank` varchar(255) DEFAULT NULL,

  -- Pricing tiers
  `vip_price` decimal(10,2) DEFAULT NULL CHECK (`vip_price` >= 0),
  `vvip_price` decimal(10,2) DEFAULT NULL CHECK (`vvip_price` >= 0),
  `vvvip_price` decimal(10,2) DEFAULT NULL CHECK (`vvvip_price` >= 0),
  `table_price` decimal(10,2) DEFAULT NULL CHECK (`table_price` >= 0),

  -- Metadata
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,

  PRIMARY KEY (`id`),
  FOREIGN KEY (`creator_id`) REFERENCES `creatorprofile`(`id`) ON DELETE CASCADE,

  INDEX `idx_event_name` (`event_name`),
  INDEX `idx_event_category` (`category`),
  INDEX `idx_event_date` (`date`),
  INDEX `idx_event_creator_id` (`creator_id`),
  FULLTEXT INDEX `ft_event_name_summary` (`event_name`, `summary`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Event creation and management';

-- ============================================================================
-- Table: table_categories
-- Purpose: Table categories for event seating arrangements
-- ============================================================================
CREATE TABLE IF NOT EXISTS `table_categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `capacity` int(11) NOT NULL CHECK (`capacity` > 0),
  `price` decimal(10,2) NOT NULL CHECK (`price` >= 0),
  `available_tables` int(11) NOT NULL DEFAULT 0 CHECK (`available_tables` >= 0),
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  FOREIGN KEY (`event_id`) REFERENCES `eventcreation`(`id`) ON DELETE CASCADE,

  INDEX `idx_table_event_id` (`event_id`),
  INDEX `idx_table_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Table categories for events';

-- ============================================================================
-- Table: user_events
-- Purpose: User ticket purchases and attendance records
-- ============================================================================
CREATE TABLE IF NOT EXISTS `user_events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `attended_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `email` varchar(255) DEFAULT NULL,
  `qrcode_url` varchar(500) DEFAULT NULL,
  `token` varchar(500) DEFAULT NULL UNIQUE,
  `ticket_type` varchar(50) DEFAULT NULL,
  `isVerified` tinyint(1) NOT NULL DEFAULT 0,
  `verified_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `user_credential`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`event_id`) REFERENCES `eventcreation`(`id`) ON DELETE CASCADE,

  INDEX `idx_user_event_user_id` (`user_id`),
  INDEX `idx_user_event_event_id` (`event_id`),
  INDEX `idx_user_event_token` (`token`),
  INDEX `idx_user_event_email` (`email`),
  INDEX `idx_user_event_isVerified` (`isVerified`),
  UNIQUE KEY `uc_user_events_token` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='User event tickets and attendance';

-- ============================================================================
-- Table: user_interests
-- Purpose: User interest preferences for event recommendations
-- ============================================================================
CREATE TABLE IF NOT EXISTS `user_interests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL UNIQUE,
  `interests` json NOT NULL DEFAULT '[]',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uc_user_interests_user_id` (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user_credential`(`id`) ON DELETE CASCADE,

  INDEX `idx_user_interests_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='User interest preferences as JSON';

-- ============================================================================
-- Views for Common Operations
-- ============================================================================

-- View: Creator Events Summary
CREATE OR REPLACE VIEW `v_creator_events_summary` AS
SELECT
  cp.id as creator_id,
  cp.brandname as brand_name,
  cp.email as creator_email,
  COUNT(e.id) as total_events,
  COUNT(CASE WHEN e.is_active = 1 THEN 1 END) as active_events,
  COUNT(CASE WHEN e.date > CURDATE() THEN 1 END) as upcoming_events,
  SUM(CASE WHEN ue.id IS NOT NULL THEN 1 ELSE 0 END) as total_attendees
FROM `creatorprofile` cp
LEFT JOIN `eventcreation` e ON cp.id = e.creator_id
LEFT JOIN `user_events` ue ON e.id = ue.event_id
GROUP BY cp.id, cp.brandname, cp.email;

-- View: Event Attendance Summary
CREATE OR REPLACE VIEW `v_event_attendance_summary` AS
SELECT
  e.id as event_id,
  e.event_name,
  e.date,
  e.price,
  COUNT(ue.id) as total_tickets_sold,
  COUNT(CASE WHEN ue.isVerified = 1 THEN 1 END) as verified_attendees,
  SUM(e.price) as revenue_regular,
  SUM(CASE WHEN ue.ticket_type = 'VIP' THEN e.vip_price ELSE 0 END) as revenue_vip,
  SUM(CASE WHEN ue.ticket_type = 'VVIP' THEN e.vvip_price ELSE 0 END) as revenue_vvip
FROM `eventcreation` e
LEFT JOIN `user_events` ue ON e.id = ue.event_id
GROUP BY e.id, e.event_name, e.date, e.price;
    time_in DATETIME NOT NULL,
    time_out DATETIME NOT NULL,
    summary TEXT NOT NULL,
    picture VARCHAR(500),
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    date DATETIME NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    bank VARCHAR(100) NOT NULL,
    vip_price DECIMAL(10, 2),
    vvip_price DECIMAL(10, 2),
    vvvip_price DECIMAL(10, 2),
    table_price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_date (date)
);

-- 5. User Events (Tickets) Table
CREATE TABLE IF NOT EXISTS user_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    qrcode_url VARCHAR(500),
    token VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_credential(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES eventcreation(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_event (event_id),
    INDEX idx_token (token)
);

-- 6. User Interests Table
CREATE TABLE IF NOT EXISTS user_interests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    interests JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_credential(id) ON DELETE CASCADE
);

-- Create Indexes for performance
CREATE INDEX idx_user_email ON user_credential(email);
CREATE INDEX idx_event_brand ON eventcreation(brand_name);
CREATE INDEX idx_event_creator ON eventcreation(brand_name);

-- Add any additional constraints or views as needed
