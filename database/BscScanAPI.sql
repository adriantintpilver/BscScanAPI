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
--
-- Table bep721_token_transfer_events script
--
CREATE TABLE `bep721_token_transfer_events` (
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
      `tokenID` varchar(100) NOT NULL
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='table for bep721_token_transfer_events.';
--
-- Table coins_history script
--
    CREATE TABLE IF NOT EXISTS coins_history
(
    `id_coin` varchar(200) NOT NULL,
    `price` decimal(65,20),
    `market_cap` decimal(65,20),
    `date_price` date NOT NULL,
    `money` varchar(50) NOT NULL,
    CONSTRAINT coins_history_pkey PRIMARY KEY (id_coin, date_price, money)
)
--
-- Stored procedure to count transaccion form and to by day by wallet id
--
USE `BscScanAPI_DB` $$
DROP procedure IF EXISTS `transsaction_from_to_day_by_wallet`$$
CREATE PROCEDURE `transsaction_from_to_day_by_wallet`(IN id_wallet VARCHAR(42))
    BEGIN
    SELECT 
            DATE_FORMAT(FROM_UNIXTIME(e.timestamp), '%y-%m-%d') as date, 
                COUNT(CASE WHEN e.fromwallet = id_wallet THEN 0 ELSE NULL END) 'fromwallet',
                COUNT(CASE WHEN e.towallet = id_wallet THEN 0 ELSE NULL END) 'towallet'
            FROM BscScanAPI_DB.bep20_token_transfer_events as e 
            where e.fromwallet = id_wallet or e.towallet = id_wallet
            group by date
            order by date DESC;
    END$$
--
-- Stored procedure to count transaccion form and to by month by wallet id
--
USE `BscScanAPI_DB` $$
DROP procedure IF EXISTS `transsaction_from_to_month_by_wallet`$$
CREATE PROCEDURE `transsaction_from_to_month_by_wallet`(IN id_wallet VARCHAR(42))
    BEGIN
    SELECT 
            DATE_FORMAT(FROM_UNIXTIME(e.timestamp), '%y-%M') as date, 
                COUNT(CASE WHEN e.fromwallet = id_wallet THEN 0 ELSE NULL END) 'fromwallet',
                COUNT(CASE WHEN e.towallet = id_wallet THEN 0 ELSE NULL END) 'towallet'
            FROM BscScanAPI_DB.bep20_token_transfer_events as e 
            where e.fromwallet = id_wallet or e.towallet = id_wallet
            group by date
            order by date DESC;
    END$$
--
-- Stored procedure to count transaccion form and to by month by wallet id
--
USE `BscScanAPI_DB` $$
DROP procedure IF EXISTS `transactions_bep20_by_day_money_valuated`$$
CREATE DEFINER=`root`@`%` PROCEDURE `transactions_bep20_by_day_money_valuated`(IN id_wallet VARCHAR(42), IN money VARCHAR(50))
BEGIN
	SELECT 
            DATE_FORMAT(FROM_UNIXTIME(e.timestamp), '%y-%m-%d') as date, 
                SUM(CASE WHEN e.fromwallet = @id_wallet THEN (e.value * (select ch.price from coins_history as ch where ch.id_coin = e.tokenName and ch.money=@money and date_price=DATE_FORMAT(FROM_UNIXTIME(e.timestamp), '%y-%m-%d')))  ELSE NULL END) 'fromwallet',
                SUM(CASE WHEN e.towallet = @id_wallet THEN (e.value * (select ch.price from coins_history as ch where ch.id_coin = e.tokenName and ch.money=@money and date_price=DATE_FORMAT(FROM_UNIXTIME(e.timestamp), '%y-%m-%d')))  ELSE NULL END) 'towallet'
            FROM BscScanAPI_DB.bep20_token_transfer_events as e 
            where e.fromwallet = @id_wallet or e.towallet = @id_wallet
            group by date
            order by date DESC;
END$$