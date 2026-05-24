-- HID Gateway Platform schema (initial)
-- Auto-loaded by MySQL container on first start (mounted to /docker-entrypoint-initdb.d/).
-- Database `blue_db` is created by MYSQL_DATABASE env; here we just add tables.

USE `blue_db`;

-- ============================================================
-- 1. 用户 / 设备 / HID 网关核心表
-- ============================================================

CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(64) NOT NULL UNIQUE COMMENT '用户名',
    `password_hash` VARCHAR(255) NOT NULL COMMENT 'bcrypt 哈希',
    `role` ENUM('admin','user') NOT NULL DEFAULT 'user',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

CREATE TABLE IF NOT EXISTS `devices` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `device_uuid` VARCHAR(128) NOT NULL UNIQUE COMMENT '设备唯一标识(NVS 中持久化)',
    `owner_user_id` BIGINT NULL,
    `name` VARCHAR(128),
    `capabilities` JSON COMMENT '设备能力：usb_keyboard / usb_mouse / ble_*',
    `status` ENUM('offline','online','busy','error') NOT NULL DEFAULT 'offline',
    `last_online_at` DATETIME NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_device_owner` FOREIGN KEY (`owner_user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_device_owner` (`owner_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';

CREATE TABLE IF NOT EXISTS `device_connections` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `device_id` BIGINT NOT NULL,
    `ip` VARCHAR(64),
    `session_id` VARCHAR(128),
    `connected_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `disconnected_at` DATETIME NULL,
    CONSTRAINT `fk_conn_device` FOREIGN KEY (`device_id`) REFERENCES `devices`(`id`) ON DELETE CASCADE,
    INDEX `idx_conn_device` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备连接历史';

CREATE TABLE IF NOT EXISTS `action_logs` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `msg_id` CHAR(36) NOT NULL UNIQUE,
    `user_id` BIGINT NULL,
    `device_id` BIGINT NULL,
    `action_type` VARCHAR(64),
    `payload_json` JSON,
    `status` ENUM('pending','sent','acked','failed') NOT NULL DEFAULT 'pending',
    `exec_time_ms` INT NULL,
    `error_code` VARCHAR(16) NULL,
    `error_message` VARCHAR(255) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_action_device` (`device_id`),
    INDEX `idx_action_user`   (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='动作日志';

CREATE TABLE IF NOT EXISTS `macros` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL,
    `name` VARCHAR(128) NOT NULL,
    `content_json` JSON NOT NULL COMMENT '{steps: [...]}',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_macro_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_macro_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='宏定义';

CREATE TABLE IF NOT EXISTS `device_groups` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `owner_user_id` BIGINT NOT NULL,
    `name` VARCHAR(128) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_grp_owner` FOREIGN KEY (`owner_user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备组';

CREATE TABLE IF NOT EXISTS `device_group_members` (
    `group_id` BIGINT NOT NULL,
    `device_id` BIGINT NOT NULL,
    PRIMARY KEY (`group_id`, `device_id`),
    CONSTRAINT `fk_dgm_group`  FOREIGN KEY (`group_id`)  REFERENCES `device_groups`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_dgm_device` FOREIGN KEY (`device_id`) REFERENCES `devices`(`id`)       ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备组成员';

-- ============================================================
-- 2. 旧业务（车辆资产）—— 保留作为示例
-- ============================================================

CREATE TABLE IF NOT EXISTS `vehicles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `model_name` VARCHAR(50) NOT NULL COMMENT '项目(车型)',
    `vehicle_code` VARCHAR(50) NOT NULL UNIQUE COMMENT '车辆编码',
    `vin` VARCHAR(20) NOT NULL UNIQUE COMMENT '车架号',
    `phase` VARCHAR(20) COMMENT '阶段',
    `configuration` VARCHAR(100) COMMENT '配置',
    `chip_platform` VARCHAR(50) COMMENT '芯片平台',
    `wheel_size` INT COMMENT '轮毂',
    `has_data_device` TINYINT(1) DEFAULT 0,
    `current_status` ENUM('空闲','使用中','维修中','已报废') DEFAULT '空闲',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='车辆资产';

CREATE TABLE IF NOT EXISTS `loan_records` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `vehicle_id` INT NOT NULL,
    `borrower_name` VARCHAR(50) NOT NULL,
    `phone_number` VARCHAR(20),
    `loan_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `expected_return_time` DATETIME,
    `actual_return_time` DATETIME NULL,
    `remark` TEXT,
    CONSTRAINT `fk_vehicle_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='借用记录';

-- 示例车辆
INSERT IGNORE INTO `vehicles` (model_name, vehicle_code, vin, phase, configuration, chip_platform, wheel_size, has_data_device, current_status)
VALUES ('S31L-M0','AATI25SVV633','LSJEH43C9SZ993202','PPV','6座 AWD 51','Orinx',20,1,'空闲');
