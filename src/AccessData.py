sql_querys = {
    # list_hired_employees query
    'sql_from-to_read_bep20_token_transfer_events_by_address_db' : """SELECT MAX(e.timeStamp) FROM BscScanAPI_DB.bep20_token_transfer_events as e where e.fromwallet = '{0}' or e.towallet = '{0}'""",
    # insert new hired employees query
    'sql_insert_bep20_token_transfer_events_by_address' : """INSERT INTO bep20_token_transfer_events (blockHash,blockNumber,confirmations,contractAddress,cumulativeGasUsed,fromwallet,gas,gasPrice,gasUsed,hash,input,nonce,timeStamp,towallet,tokenDecimal,tokenName,tokenSymbol,transactionIndex,value) VALUES ('{0}',{1},{2},'{3}',{4},'{5}',{6},'{7}',{8},'{9}','{10}',{11},{12},'{13}',{14},'{15}','{16}',{17},'{18}')"""
}