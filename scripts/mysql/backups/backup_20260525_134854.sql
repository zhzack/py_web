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
  `id` bigint NOT NULL AUTO_INCREMENT,
  `msg_id` char(36) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  `device_id` bigint DEFAULT NULL,
  `action_type` varchar(64) DEFAULT NULL,
  `payload_json` json DEFAULT NULL,
  `status` enum('pending','sent','acked','failed') NOT NULL DEFAULT 'pending',
  `exec_time_ms` int DEFAULT NULL,
  `error_code` varchar(16) DEFAULT NULL,
  `error_message` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `msg_id` (`msg_id`),
  KEY `idx_action_device` (`device_id`),
  KEY `idx_action_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='åŠ¨ä½œæ—¥å¿—';
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
  `id` bigint NOT NULL AUTO_INCREMENT,
  `device_id` bigint NOT NULL,
  `ip` varchar(64) DEFAULT NULL,
  `session_id` varchar(128) DEFAULT NULL,
  `connected_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `disconnected_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_conn_device` (`device_id`),
  CONSTRAINT `fk_conn_device` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='è®¾å¤‡è¿žæŽ¥åŽ†å²';
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
  `group_id` bigint NOT NULL,
  `device_id` bigint NOT NULL,
  PRIMARY KEY (`group_id`,`device_id`),
  KEY `fk_dgm_device` (`device_id`),
  CONSTRAINT `fk_dgm_device` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_dgm_group` FOREIGN KEY (`group_id`) REFERENCES `device_groups` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='è®¾å¤‡ç»„æˆå‘˜';
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
  `id` bigint NOT NULL AUTO_INCREMENT,
  `owner_user_id` bigint NOT NULL,
  `name` varchar(128) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_grp_owner` (`owner_user_id`),
  CONSTRAINT `fk_grp_owner` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='è®¾å¤‡ç»„';
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
  `id` bigint NOT NULL AUTO_INCREMENT,
  `device_uuid` varchar(128) NOT NULL COMMENT 'è®¾å¤‡å”¯ä¸€æ ‡è¯†(NVS ä¸­æŒä¹…åŒ–)',
  `owner_user_id` bigint DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  `capabilities` json DEFAULT NULL COMMENT 'è®¾å¤‡èƒ½åŠ›ï¼šusb_keyboard / usb_mouse / ble_*',
  `status` enum('offline','online','busy','error') NOT NULL DEFAULT 'offline',
  `last_online_at` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_uuid` (`device_uuid`),
  KEY `idx_device_owner` (`owner_user_id`),
  CONSTRAINT `fk_device_owner` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='è®¾å¤‡è¡¨';
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
  `id` int NOT NULL AUTO_INCREMENT,
  `vehicle_id` int NOT NULL,
  `borrower_name` varchar(50) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `loan_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `expected_return_time` datetime DEFAULT NULL,
  `actual_return_time` datetime DEFAULT NULL,
  `remark` text,
  PRIMARY KEY (`id`),
  KEY `fk_vehicle_id` (`vehicle_id`),
  CONSTRAINT `fk_vehicle_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='å€Ÿç”¨è®°å½•';
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
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `name` varchar(128) NOT NULL,
  `content_json` json NOT NULL COMMENT '{steps: [...]}',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_macro_user` (`user_id`),
  CONSTRAINT `fk_macro_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='å®å®šä¹‰';
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
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL COMMENT 'ç”¨æˆ·å',
  `password_hash` varchar(255) NOT NULL COMMENT 'bcrypt å“ˆå¸Œ',
  `role` enum('admin','user') NOT NULL DEFAULT 'user',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ç”¨æˆ·è¡¨';
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
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ä¸»é”®ID',
  `model_name` varchar(50) NOT NULL COMMENT 'é¡¹ç›®(è½¦åž‹)',
  `vehicle_code` varchar(50) NOT NULL COMMENT 'è½¦è¾†ç¼–ç ',
  `vin` varchar(20) NOT NULL COMMENT 'è½¦æž¶å·',
  `phase` varchar(20) DEFAULT NULL COMMENT 'é˜¶æ®µ',
  `configuration` varchar(100) DEFAULT NULL COMMENT 'é…ç½®',
  `chip_platform` varchar(50) DEFAULT NULL COMMENT 'èŠ¯ç‰‡å¹³å°',
  `wheel_size` int DEFAULT NULL COMMENT 'è½®æ¯‚',
  `has_data_device` tinyint(1) DEFAULT '0',
  `current_status` enum('ç©ºé—²','ä½¿ç”¨ä¸­','ç»´ä¿®ä¸­','å·²æŠ¥åºŸ') DEFAULT 'ç©ºé—²',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `vehicle_code` (`vehicle_code`),
  UNIQUE KEY `vin` (`vin`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='è½¦è¾†èµ„äº§';
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

-- Dump completed on 2026-05-25 13:48:54
