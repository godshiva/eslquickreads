-- MySQL dump 10.13  Distrib 8.0.29, for Linux (x86_64)
--
-- Host: algorithmguy.mysql.pythonanywhere-services.com    Database: algorithmguy$default
-- ------------------------------------------------------
-- Server version	8.0.32

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
-- Table structure for table `access_granted`
--

DROP TABLE IF EXISTS `access_granted`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `access_granted` (
  `id` int NOT NULL AUTO_INCREMENT,
  `resource_string` varchar(255) NOT NULL,
  `resource_type` int NOT NULL,
  `timestamp` timestamp(3) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=190 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `access_granted`
--

LOCK TABLES `access_granted` WRITE;
/*!40000 ALTER TABLE `access_granted` DISABLE KEYS */;
INSERT INTO `access_granted` VALUES (187,'f57b7295068c51debd3fa40927d9786d61cff1fcf68e5cf5527eb88dd5fd6dd5',25,'2023-05-07 18:23:29.000'),(189,'f57b7295068c51debd3fa40927d9786d61cff1fcf68e5cf5527eb88dd5fd6dd5',25,'2023-05-07 18:24:42.000');
/*!40000 ALTER TABLE `access_granted` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lessons`
--

DROP TABLE IF EXISTS `lessons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lessons` (
  `id` int NOT NULL AUTO_INCREMENT,
  `lesson_number` int NOT NULL,
  `lesson_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lesson_number` (`lesson_number`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lessons`
--

LOCK TABLES `lessons` WRITE;
/*!40000 ALTER TABLE `lessons` DISABLE KEYS */;
INSERT INTO `lessons` VALUES (1,1,'Lesson 1');
/*!40000 ALTER TABLE `lessons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `password_resets`
--

DROP TABLE IF EXISTS `password_resets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `password_resets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userhash` char(64) NOT NULL,
  `resetcode` varchar(64) NOT NULL,
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `password_resets`
--

LOCK TABLES `password_resets` WRITE;
/*!40000 ALTER TABLE `password_resets` DISABLE KEYS */;
/*!40000 ALTER TABLE `password_resets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_progress`
--

DROP TABLE IF EXISTS `student_progress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_progress` (
  `id` int NOT NULL AUTO_INCREMENT,
  `lesson_id` int DEFAULT NULL,
  `student_id` int DEFAULT NULL,
  `lesson_finished` tinyint(1) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `lesson_id` (`lesson_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `student_progress_ibfk_1` FOREIGN KEY (`lesson_id`) REFERENCES `lessons` (`id`) ON DELETE CASCADE,
  CONSTRAINT `student_progress_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `user_credentials` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_progress`
--

LOCK TABLES `student_progress` WRITE;
/*!40000 ALTER TABLE `student_progress` DISABLE KEYS */;
INSERT INTO `student_progress` VALUES (10,1,19,1,'2023-05-06 22:36:22'),(12,1,7,1,'2023-05-06 23:54:53'),(13,1,16,1,'2023-05-07 00:09:05'),(14,1,17,1,'2023-05-07 00:17:15'),(15,1,20,1,'2023-05-07 00:19:06');
/*!40000 ALTER TABLE `student_progress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_credentials`
--

DROP TABLE IF EXISTS `user_credentials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_credentials` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `sha256user` char(64) NOT NULL,
  `salt` char(64) NOT NULL,
  `sha256password` char(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sha256user` (`sha256user`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_credentials`
--

LOCK TABLES `user_credentials` WRITE;
/*!40000 ALTER TABLE `user_credentials` DISABLE KEYS */;
INSERT INTO `user_credentials` VALUES (1,'2023-04-22 04:41:59','a3a6d2abcd0252c42b7db36362d7432c7213c7fb03a3f903c29d859bdce4f6c4','3ed05bbb8cb31c0ad171a7a5b048bd8dd8daefc2a5a5f6ff9cfb04d800e81b6a','2150d6054f8cb24589dae67da9f35404dd9c74149126290c4dafaf3c17321efe'),(2,'2023-04-22 06:42:15','8b2c126e98beae9884191b94af1e54eda866a02dc822cee35a62492008106909','c66221d4b6e3b000f25fffa268aa5becef9839891a2541f6b2324f9d1c2b508f','c4eecca802ceb77d8ef78e4b7d67cba8b2b95e60ffa486f3886ca661e7884de0'),(3,'2023-04-22 17:32:34','3cd2a1f1fdfc11ec9ce795caaed9e0d7a1cc673b0faa109fac57a8a065326118','3dce95d298e2136b8efd8f0bcd3c023a8ba3a983ea92d482e6a6f6f58a707448','5043357226cda5dabec5cb18ac609307798bd841ca1436f4054c37fd1e538342'),(4,'2023-04-22 17:34:37','f22d4cc1e94001c91c8ad8e6b1f5d63f20e7cf266b8ad809133903335613aea8','eb3e3fd0359482fadbae1474a2bf455f767e1b1612ffcb0e96b5df3e2501a253','fb58e7f2548b89f394f721aebafe9d6258d884e7ddac00b12df32ec32f2d79e4'),(5,'2023-04-22 19:42:19','3b8464b74173833623b65ad789178e1b196e7dfbe924e6bdd29d9ebe30b1fc1d','5d74d91cd4ea33211591cbfaca90f254cac63150e1f42788a73fe99f567964ac','1edb63e5d774c11db65d0409090b7e89c77986ec0ce53debaecf0fa7845709c4'),(7,'2023-04-22 20:31:42','9af7ff1538e3061c79d6f938d9ab28ff1c7521935a6fe964f5702cd6cd5a5540','b5e2a13087d7d287303073649fe1e0787589bcb550941885423f66d54d941889','1564dbac9172cafa6fc1d6f052ac949e678381104f1b849384f2f55560fd6c54'),(8,'2023-04-22 20:32:49','1ea73f4ef4dfb566e6a54351a7c64241f1cad7e311cf0ad7213e14f19f9d8735','702224dfb2770c694242814c5915eb0d3a44698dc9000505d9a025e441731758','760786c0cf3a92e2a034def19a090afe21caf4b4a50cc73f0a33a5d49f18eed1'),(9,'2023-04-22 20:33:59','4b1227ea5a2a4ca45e08bdaf5031f33589813b2ccf65822617c0805bfac1443d','879f9caedcf912121e1ab8f60581da1b174b50cb84350ec29f27b6dda95ad3b9','8ab0906a85a1634f5ea56fd0ef1575d6819e0d80740d366e4de9f5dffceb6a08'),(14,'2023-04-23 06:02:39','e710682cf527ec1ce351dbf8848886b833553346325e3d4887e9251fea02ec39','9e3868ecb78d9e77672d9a4041233462dbc4267cd7c0544e010b8765fe93a37b','22e6dd4e1bc87a1e71595f77d466ce90a5625e205fc0e5c1841c1d546d6ece0f'),(15,'2023-04-24 08:09:06','c7eb60cbaea088b040fc7315e94f4a2729da769eda7ddb535eec519250b94ee3','cf02b09d771eec1c884e3f839e7c194652dabf8180c0679bfdecb940bab7a3ad','d8ccc51a3c39e1c6476a85edf9f04b74e70d4c03fd21b3b491504202032b9848'),(16,'2023-04-30 02:04:45','b695d7050e32e4ee0144e11edc4870b7b2df850dc482fb0afc596a057278fdf9','c2b9389a85d73c5a34676df5c99c35e19251e360db78c7371d29452677d41cbe','2c755d861292203a3bd6788eeb83e1895c12cecfd7856eb0369199627010f7f0'),(17,'2023-04-30 02:18:02','4836165f208c27eef08360fdded9a79d5c881eb84b667316eacd9c9266937c7e','eb4769845b922d47afbe85fcfab7fa9674f0e66413fb7c963cc7741f6520342b','5114888afe7f6103225879d63921933d8ff790b374315f44c61aef9d661701cc'),(18,'2023-04-30 02:45:07','223b0c968ac5bab1dd35ed89b8c925f56620d9e9a821b72edd862050e95426ee','08b2afc7fd265b49f3d6d027971b8f11a046ca21bc89e05ad2bf8d2d34f570bc','69dd369409c00951bbd29bac6febf76e500f2289c15fdb1e5f9e3aa79cbb8c91'),(19,'2023-04-30 02:46:47','7ef2587a77ec6b3df853ac97eaa9c3ece94f1233c26fb47091b2fdba8687ea3c','ff044ea528e342154a46d31a7734c9b7d305f068010a70c2015f11c64eb94f05','ec60b24513c533500b8619aceb23ed11b1b2eb07e90cab3b5a6f977c9dc262f7'),(20,'2023-05-07 00:18:04','9c42c82383edc2512d066e5891404430655a979c7ffe25338da7fe1bf3204d24','793b50b341146805856fbd8f112cb33b2adac623df63316cb2936c554ce82584','ab3bbb9a861376c7850cb5efe3c154f0ade2e17a2dc6e2b806a22aaf2b69cbce');
/*!40000 ALTER TABLE `user_credentials` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-05-07 18:53:10
