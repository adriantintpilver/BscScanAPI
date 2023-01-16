-- Data base scripts
-- -> docker run --name mysql-db-BscScanAPI -e MYSQL_ROOT_PASSWORD=BscScanAPI_PasSWoRd -p 3306:3306 -d mysql:latest

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "-03:00";
--
-- Base de datos: `BscScanAPI_DB`
-- 
-- --------------------------------------------------------
    CREATE DATABASE IF NOT EXISTS `BscScanAPI_DB`;
        
    USE BscScanAPI_DB;
--
-- Table bep20_token_transfer_events script
--
CREATE TABLE `bep20_token_transfer_events` (
	  `id` INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
      `blockHash` varchar(100) NOT NULL,
      `blockNumber` int NOT NULL,
      `confirmations` int NOT NULL,
      `contractAddress` varchar(42) NOT NULL,
      `cumulativeGasUsed` int NOT NULL,
      `fromwallet` varchar(42) NOT NULL,
      `gas` int NOT NULL,
      `gasPrice` varchar(50) NOT NULL,
      `gasUsed` int NOT NULL,
      `hash` varchar(100) NOT NULL,
      `input` varchar(50) NOT NULL,
      `nonce` int NOT NULL,
      `timeStamp` int NOT NULL,
      `towallet` varchar(42) NOT NULL,
      `tokenDecimal` INT,
      `tokenName` varchar(50) NOT NULL,
      `tokenSymbol` varchar(50) NOT NULL,
      `transactionIndex` INT,
      `value` varchar(100) NOT NULL
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='table for bep20_token_transfer_events.';