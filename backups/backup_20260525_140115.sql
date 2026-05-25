-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: blue_db
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `action_logs`
--

DROP TABLE IF EXISTS `action_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `action_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `msg_id` char(36) NOT NULL COMMENT '消息唯一ID(UUID)',
  `user_id` bigint DEFAULT NULL COMMENT '操作用户ID',
  `device_id` bigint DEFAULT NULL COMMENT '目标设备ID',
  `action_type` varchar(64) DEFAULT NULL COMMENT '动作类型',
  `payload_json` json DEFAULT NULL COMMENT '动作参数(JSON)',
  `status` enum('pending','sent','acked','failed') NOT NULL DEFAULT 'pending' COMMENT '执行状态: pending待发/sent已发/acked已确认/failed失败',
  `exec_time_ms` int DEFAULT NULL COMMENT '执行耗时(毫秒)',
  `error_code` varchar(16) DEFAULT NULL COMMENT '错误码',
  `error_message` varchar(255) DEFAULT NULL COMMENT '错误信息',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `msg_id` (`msg_id`),
  KEY `idx_action_device` (`device_id`),
  KEY `idx_action_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='动作日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `action_logs`
--

LOCK TABLES `action_logs` WRITE;
/*!40000 ALTER TABLE `action_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `action_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_connections`
--

DROP TABLE IF EXISTS `device_connections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `device_connections` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `device_id` bigint NOT NULL COMMENT '设备ID',
  `ip` varchar(64) DEFAULT NULL COMMENT '连接IP地址',
  `session_id` varchar(128) DEFAULT NULL COMMENT 'WebSocket会话ID',
  `connected_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '连接时间',
  `disconnected_at` datetime DEFAULT NULL COMMENT '断开时间',
  PRIMARY KEY (`id`),
  KEY `idx_conn_device` (`device_id`),
  CONSTRAINT `fk_conn_device` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='设备连接历史';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_connections`
--

LOCK TABLES `device_connections` WRITE;
/*!40000 ALTER TABLE `device_connections` DISABLE KEYS */;
/*!40000 ALTER TABLE `device_connections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_group_members`
--

DROP TABLE IF EXISTS `device_group_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `device_group_members` (
  `group_id` bigint NOT NULL COMMENT '设备组ID',
  `device_id` bigint NOT NULL COMMENT '设备ID',
  PRIMARY KEY (`group_id`,`device_id`),
  KEY `fk_dgm_device` (`device_id`),
  CONSTRAINT `fk_dgm_device` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_dgm_group` FOREIGN KEY (`group_id`) REFERENCES `device_groups` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='设备组成员';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_group_members`
--

LOCK TABLES `device_group_members` WRITE;
/*!40000 ALTER TABLE `device_group_members` DISABLE KEYS */;
/*!40000 ALTER TABLE `device_group_members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_groups`
--

DROP TABLE IF EXISTS `device_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `device_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `owner_user_id` bigint NOT NULL COMMENT '创建用户ID',
  `name` varchar(128) NOT NULL COMMENT '分组名称',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `fk_grp_owner` (`owner_user_id`),
  CONSTRAINT `fk_grp_owner` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='设备组';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_groups`
--

LOCK TABLES `device_groups` WRITE;
/*!40000 ALTER TABLE `device_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `device_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devices`
--

DROP TABLE IF EXISTS `devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `devices` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `device_uuid` varchar(128) NOT NULL COMMENT '设备唯一标识(NVS中持久化)',
  `owner_user_id` bigint DEFAULT NULL COMMENT '归属用户ID',
  `name` varchar(128) DEFAULT NULL COMMENT '设备名称',
  `capabilities` json DEFAULT NULL COMMENT '设备能力: usb_keyboard / usb_mouse / ble_*',
  `status` enum('offline','online','busy','error') NOT NULL DEFAULT 'offline' COMMENT '设备状态: offline/online/busy/error',
  `last_online_at` datetime DEFAULT NULL COMMENT '最后在线时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_uuid` (`device_uuid`),
  KEY `idx_device_owner` (`owner_user_id`),
  CONSTRAINT `fk_device_owner` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='设备表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devices`
--

LOCK TABLES `devices` WRITE;
/*!40000 ALTER TABLE `devices` DISABLE KEYS */;
/*!40000 ALTER TABLE `devices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loan_records`
--

DROP TABLE IF EXISTS `loan_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loan_records` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `vehicle_id` int NOT NULL COMMENT '关联车辆ID',
  `borrower_name` varchar(50) NOT NULL COMMENT '借用人姓名',
  `phone_number` varchar(20) DEFAULT NULL COMMENT '借用人电话',
  `loan_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '借出时间',
  `expected_return_time` datetime DEFAULT NULL COMMENT '预计归还时间',
  `actual_return_time` datetime DEFAULT NULL COMMENT '实际归还时间',
  `remark` text COMMENT '备注',
  PRIMARY KEY (`id`),
  KEY `fk_vehicle_id` (`vehicle_id`),
  CONSTRAINT `fk_vehicle_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='借用记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loan_records`
--

LOCK TABLES `loan_records` WRITE;
/*!40000 ALTER TABLE `loan_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `loan_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `macros`
--

DROP TABLE IF EXISTS `macros`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `macros` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint NOT NULL COMMENT '归属用户ID',
  `name` varchar(128) NOT NULL COMMENT '宏名称',
  `content_json` json NOT NULL COMMENT '宏内容 {steps: [...]}',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_macro_user` (`user_id`),
  CONSTRAINT `fk_macro_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='宏定义';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `macros`
--

LOCK TABLES `macros` WRITE;
/*!40000 ALTER TABLE `macros` DISABLE KEYS */;
/*!40000 ALTER TABLE `macros` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` varchar(64) NOT NULL COMMENT '用户名',
  `password_hash` varchar(255) NOT NULL COMMENT 'bcrypt 哈希密码',
  `role` enum('admin','user') NOT NULL DEFAULT 'user' COMMENT '角色: admin管理员/user普通用户',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否启用: 1启用/0禁用',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'alice','$2b$12$WpAeFaIK.e8oVTA4jIvCeuwLyFAtcn5gdw4oARSZ8UC1XVrvhBeL.','user',1,'2026-05-25 05:28:54','2026-05-25 05:28:54');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vehicles`
--

DROP TABLE IF EXISTS `vehicles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehicles` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `model_name` varchar(50) DEFAULT NULL COMMENT '项目(车型)',
  `vehicle_code` varchar(50) DEFAULT NULL COMMENT '车辆编码',
  `vin` varchar(20) DEFAULT NULL COMMENT '车架号',
  `phase` varchar(20) DEFAULT NULL COMMENT '阶段',
  `configuration` varchar(100) DEFAULT NULL COMMENT '配置',
  `chip_platform` varchar(50) DEFAULT NULL COMMENT '芯片平台',
  `wheel_size` int DEFAULT NULL COMMENT '轮毂',
  `has_data_device` tinyint(1) DEFAULT NULL COMMENT '是否有数采设备',
  `current_status` varchar(20) DEFAULT NULL COMMENT '当前状态',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `vehicle_code` (`vehicle_code`),
  UNIQUE KEY `vin` (`vin`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='车辆资产';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehicles`
--

LOCK TABLES `vehicles` WRITE;
/*!40000 ALTER TABLE `vehicles` DISABLE KEYS */;
INSERT INTO `vehicles` VALUES (1,'S31L-M0','AATI25SVV633','LSJEH43C9SZ993202','PPV','6åº§ AWD 51','Orinx',20,1,'ç©ºé—²','2026-05-25 03:11:59','2026-05-25 03:11:59');
/*!40000 ALTER TABLE `vehicles` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-25 14:01:15
