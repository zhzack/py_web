-- Active: 1767716117018@@127.0.0.1@3306@mysql
-- 1. 如果存在旧数据库则删除，然后创建新数据库
DROP DATABASE IF EXISTS vehicle_management;

CREATE DATABASE vehicle_management DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 2. 切换到该数据库
USE vehicle_management;

-- 3. 创建车辆资产表 (存放车辆固有属性)
CREATE TABLE `vehicles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `model_name` VARCHAR(50) NOT NULL COMMENT '项目(车型)，例: S31L-M0',
    `vehicle_code` VARCHAR(50) NOT NULL UNIQUE COMMENT '车辆编码，例: AATI25SVV633',
    `vin` VARCHAR(20) NOT NULL UNIQUE COMMENT '车架号(VIN)',
    `phase` VARCHAR(20) COMMENT '阶段，例: PPV, VP',
    `configuration` VARCHAR(100) COMMENT '车辆配置，例: 6座 AWD 51',
    `chip_platform` VARCHAR(50) COMMENT '芯片平台(Thor/Orinx)',
    `wheel_size` INT COMMENT '轮毂大小(单位:寸)',
    `has_data_device` TINYINT(1) DEFAULT 0 COMMENT '是否有数采设备: 0-无, 1-有',
    `current_status` ENUM('空闲', '使用中', '维修中', '已报废') DEFAULT '空闲' COMMENT '当前车辆状态',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '数据录入时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间'
) ENGINE = InnoDB COMMENT = '车辆资产基础信息表';

-- 4. 创建借用记录表 (存放流转历史)
CREATE TABLE `loan_records` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    `vehicle_id` INT NOT NULL COMMENT '关联车辆ID',
    `borrower_name` VARCHAR(50) NOT NULL COMMENT '借车人姓名',
    `phone_number` VARCHAR(20) COMMENT '手机号码',
    `loan_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '借出时间',
    `expected_return_time` DATETIME COMMENT '预计归还时间',
    `actual_return_time` DATETIME DEFAULT NULL COMMENT '实际归还时间',
    `remark` TEXT COMMENT '备注',
    -- 外键约束：如果车辆被删除了，相关的借车记录也会报错，保证数据完整性
    CONSTRAINT `fk_vehicle_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`) ON DELETE CASCADE
) ENGINE = InnoDB COMMENT = '车辆借用记录表';

-- 5. 插入一条示例数据 (对应你图片中的那行数据)
INSERT INTO
    `vehicles` (
        model_name,
        vehicle_code,
        vin,
        phase,
        configuration,
        chip_platform,
        wheel_size,
        has_data_device,
        current_status
    )
VALUES (
        'S31L-M0',
        'AATI25SVV633',
        'LSJEH43C9SZ993202',
        'PPV',
        '6座 AWD 51',
        'Orinx',
        20,
        1,
        '空闲'
    );

---------------------------------------------------------
-- 查看表结构说明 (DESC)
---------------------------------------------------------
SELECT '--- 车辆表结构 ---' AS '';

DESC vehicles;

SELECT '--- 借用记录表结构 ---' AS '';

DESC loan_records;