-- MySQL dump 10.13  Distrib 8.0.44, for Linux (x86_64)
--
-- Host: localhost    Database: vehicle_management
-- ------------------------------------------------------
-- Server version	8.0.44-0ubuntu0.22.04.2

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
-- Table structure for table `loan_records`
--

DROP TABLE IF EXISTS `loan_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loan_records` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `vehicle_id` int NOT NULL COMMENT '关联车辆ID',
  `borrower_name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '借车人姓名',
  `phone_number` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '手机号码',
  `loan_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '借出时间',
  `expected_return_time` datetime DEFAULT NULL COMMENT '预计归还时间',
  `actual_return_time` datetime DEFAULT NULL COMMENT '实际归还时间',
  `remark` text COLLATE utf8mb4_general_ci COMMENT '备注',
  PRIMARY KEY (`id`),
  KEY `fk_vehicle_id` (`vehicle_id`),
  CONSTRAINT `fk_vehicle_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='车辆借用记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loan_records`
--

LOCK TABLES `loan_records` WRITE;
/*!40000 ALTER TABLE `loan_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `loan_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vehicles`
--

DROP TABLE IF EXISTS `vehicles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehicles` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `model_name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '项目(车型)，例: S31L-M0',
  `vehicle_code` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '车辆编码，例: AATI25SVV633',
  `vin` varchar(20) COLLATE utf8mb4_general_ci NOT NULL COMMENT '车架号(VIN)',
  `phase` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '阶段，例: PPV, VP',
  `configuration` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '车辆配置，例: 6座 AWD 51',
  `chip_platform` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '芯片平台(Thor/Orinx)',
  `wheel_size` int DEFAULT NULL COMMENT '轮毂大小(单位:寸)',
  `has_data_device` tinyint(1) DEFAULT '0' COMMENT '是否有数采设备: 0-无, 1-有',
  `current_status` enum('空闲','使用中','维修中','已报废') COLLATE utf8mb4_general_ci DEFAULT '空闲' COMMENT '当前车辆状态',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据录入时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `vehicle_code` (`vehicle_code`),
  UNIQUE KEY `vin` (`vin`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='车辆资产基础信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehicles`
--

LOCK TABLES `vehicles` WRITE;
/*!40000 ALTER TABLE `vehicles` DISABLE KEYS */;
INSERT INTO `vehicles` VALUES (2,'S31L-M0','AATI25SVV633','LSJEH43C9SZ993202','PPV','6座 AWD 51','Orinx',20,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(3,'S31L-M0','AATI25SVV642','LSJEH43C0SZ993170','PPV','6座 AWD 64','Thor',21,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(4,'S31L-M0','AATI25SOV646','LSJEH43C1SG992802','EP2','6座 AWD 64','Thor',21,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(5,'S32L-M0','AATI25SVV510','LSJEL4398SZ994070','PPV','Ultra 5座 AWD 大电池','Thor',21,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(6,'S32L-M0','AATI25SVV545','LSJEL4390SZ994208','PPV','Max 5座 RWD 小电池','ADCU',21,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(7,'S12L-M2','AATI25SNV013','LSJWR4094SS000286','PP100','AWD空悬814W','Thor',20,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(8,'S12L-M2','AATI25SIV041','LSJWR4097SS992469','EP180','0V/100kWh AWD O1+O2(标配O4)','Thor',20,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(9,'S11L-M1','AATI23SNV503','LSJWL4093PS008002','Mule(P)','Pro（四驱）_100Kwh_P90','Orinx',22,0,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(10,'S11L-M2','AATI24SUV401','LSJWL4092RS998000','Simu+MAX','标准续航版（两驱）83','Orinx',20,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(11,'S12L-X1','AATI24SSV003','LSJWR4094SS034082','PPV','左驾-100 RWD','Orinx',20,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(12,'P12L-M0','AATI22PNV332','LSJWT4099PS992370','PPV','800V/100kWh 4WD (P42）','Orinx',20,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(13,'P12L-M1','AATI24PVV568','LSJWT4093SS992535','PPV','800V/100kWh AWD','Orinx',20,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(14,'427-BNB','TTVX25SVV013','LSVCCAZP5S2010022','EP2','MAIN','Orinx',20,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(15,'427-BNB','TTVX25SPV009','LSVCEAZP8S2010218','PTOP','TOP','Orinx',20,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(16,'427-BNB','TTVX25SVV017','LSVCEAZP8S2010025','PPV','TOP','Orinx',20,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(17,'427-CSUV L2','TTVX25UOV103','LSVVDAVAXS2000402','EP2','Flagship-109kWh AC-AWD-800V','Orinx',22,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(18,'427-CSUV L2','TTVX25UVV079','LSVUBAVA6S2010054','PPV','109kWh AC-AWD-800V Flagship','Orinx',21,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(19,'427-CSUV L2','TTVX25UVV080','LSVVDAVA7S2010045','PPV','109kWh C-RWD-800V Top Long Range','Orinx',22,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(20,'427-CSUV L3','TTVX25UOV121','LSVVDAVA1S2000420','EP2','Flagship(L3)-109kWh AC-AWD-800V','Orinx',22,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(21,'427-CSUV L3','TTVX25UOV125','LSVVDAVA9S2000424','EP2','Flagship(L3)-109kWh AC-AWD-800V','Orinx',22,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38'),(22,'427-CSUV L3','TTVX25UOV117','LSVVDAVAXS2000416','EP2','Flagship(L3)-109kWh AC-AWD-800V','Orinx',22,1,'空闲','2026-01-06 16:19:38','2026-01-06 16:19:38');
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

-- Dump completed on 2026-01-07  1:21:33
