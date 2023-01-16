# Validates the wallet_id (if it is string and leng 42).
def wallet_id_validation(wallet_id: str) -> bool:
    wallet_id = wallet_id.strip()
    return (len(wallet_id) == 42)    
