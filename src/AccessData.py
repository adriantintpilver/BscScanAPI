sql_querys = {
    # list_bep20_token_transfer_events query
    'sql_from-to_read_bep20_token_transfer_events_by_address_db' : """SELECT MAX(e.timeStamp) FROM BscScanAPI_DB.bep20_token_transfer_events as e where e.fromwallet = '{0}' or e.towallet = '{0}'""",
    # list_bep721_token_transfer_events query
    'sql_from-to_read_bep721_token_transfer_events_by_address_db' : """SELECT MAX(e.timeStamp) FROM bep721_token_transfer_events as e where e.fromwallet = '{0}' or e.towallet = '{0}'""",
    # insert new bep20_token_transfer_events query
    'sql_insert_bep20_token_transfer_events_by_address' : """INSERT INTO bep20_token_transfer_events (blockHash,blockNumber,confirmations,contractAddress,cumulativeGasUsed,fromwallet,gas,gasPrice,gasUsed,hash,input,nonce,timeStamp,towallet,tokenDecimal,tokenName,tokenSymbol,transactionIndex,value) VALUES ('{0}',{1},{2},'{3}',{4},'{5}',{6},'{7}',{8},'{9}','{10}',{11},{12},'{13}',{14},'{15}','{16}',{17},'{18}')""",
    # insert new bep721_token_transfer_events query
    'sql_insert_bep721_token_transfer_events_by_address' : """INSERT INTO bep721_token_transfer_events (blockHash,blockNumber,confirmations,contractAddress,cumulativeGasUsed,fromwallet,gas,gasPrice,gasUsed,hash,input,nonce,timeStamp,towallet,tokenDecimal,tokenName,tokenSymbol,transactionIndex,tokenID) VALUES ('{0}',{1},{2},'{3}',{4},'{5}',{6},'{7}',{8},'{9}','{10}',{11},{12},'{13}',{14},'{15}','{16}',{17},'{18}')""",
    # select read_coins_history query
    'sql_read_coins_history_db': """SELECT * FROM coins_history as ch where ch.id_coin = '{0}' and ch.date_price = '{1}' and ch.money = '{2}'""",
    # select read_coins_history query
    'sql_insert_coins_history_db': """INSERT INTO coins_history (id_coin, price, market_cap, date_price, money) VALUES ('{0}',{1},{2},'{3}','{4}')"""
}