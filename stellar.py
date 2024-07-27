import requests
from sqlalchemy.orm import Session
from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset
from datetime import datetime

server = Server("https://horizon-testnet.stellar.org")
FAKE_USD = Asset("FAKEUSD", "GBRBND3YJDB3V55DL5M5UCDE22HXVCX6FFJAWZ55XAF4OW3RW7JS546V")


def create_wallet(db: Session, user_id: str):
    keypair = Keypair.random()
    public_key = keypair.public_key
    secret_key = keypair.secret

    # Fund the wallet using Friendbot for testnet
    url = f"https://friendbot.stellar.org?addr={public_key}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fund wallet")

    # Trust the fake USD asset
    source_account = server.load_account(public_key)
    base_fee = server.fetch_base_fee()
    transaction = TransactionBuilder(
        source_account=source_account,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=base_fee
    ).append_change_trust_op(
        asset=FAKE_USD
    ).build()
    transaction.sign(secret_key)
    response = server.submit_transaction(transaction)
    if not response.get("successful"):
        raise Exception("Failed to create trustline")

    # Perform a transaction to buy fake USD with Lumens
    transaction = TransactionBuilder(
        source_account=source_account,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=base_fee
    ).append_path_payment_strict_receive_op(
        send_asset=Asset.native(),
        send_max="9990",  # Max amount of Lumens to send
        destination=public_key,
        dest_asset=FAKE_USD,
        dest_amount="10000",  # Amount of fake USD to receive
        path=[]
    ).build()
    transaction.sign(secret_key)
    response = server.submit_transaction(transaction)
    if response.get("successful") != True:
        raise Exception("Failed to buy fake USD with Lumens")

    stellar_account = StellarAccount(user_id=user_id, public_key=public_key, secret_key=secret_key)
    db.add(stellar_account)
    db.commit()
    db.refresh(stellar_account)


def get_wallet_balance(db: Session, user_id: str) -> WalletBalanceResponse:
    account = db.query(StellarAccount).filter(StellarAccount.user_id == user_id).first()
    if not account:
        raise Exception("Wallet not found")

    stellar_account = server.accounts().account_id(account.public_key).call()
    balances = [
        balance for balance in stellar_account['balances']
    ]

    return WalletBalanceResponse(user_id=user_id, balances=balances)


def make_transaction(db: Session, request: TransactionRequest) -> TransactionResponse:
    sender_account = db.query(StellarAccount).filter(StellarAccount.user_id == request.sender_id).first()
    receiver_account = db.query(StellarAccount).filter(StellarAccount.user_id == request.receiver_id).first()

    if not sender_account or not receiver_account:
        raise Exception("Sender or receiver wallet not found")

    sender_public_key = sender_account.public_key
    sender_secret_key = sender_account.secret_key
    receiver_public_key = receiver_account.public_key

    source_account = server.load_account(sender_public_key)
    base_fee = server.fetch_base_fee()

    transaction_builder = TransactionBuilder(
        source_account=source_account,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=base_fee
    ).append_payment_op(
        destination=receiver_public_key,
        amount=request.amount,
        asset=FAKE_USD
    )

    if request.memo:
        transaction_builder.add_text_memo(request.memo)

    transaction = transaction_builder.build()
    transaction.sign(sender_secret_key)
    response = server.submit_transaction(transaction)

    if not response:
        raise Exception("Transaction failed")

    transaction_record = Transaction(
        sender_id=request.sender_id,
        receiver_id=request.receiver_id,
        amount=request.amount,
        transaction_hash=response['hash'],
        timestamp=datetime.now(),
        memo=request.memo  # Store the memo in the transaction record
    )
    db.add(transaction_record)
    db.commit()
    db.refresh(transaction_record)

    return TransactionResponse(
        transaction_hash=response['hash'],
        sender=request.sender_id,
        receiver=request.receiver_id,
        amount=request.amount,
        memo=request.memo,
        timestamp=datetime.utcnow()
    )


def get_recent_transactions(db: Session, user_id: str, limit: int):
    account = db.query(StellarAccount).filter(StellarAccount.user_id == user_id).first()
    if not account:
        raise ValueError("Wallet not found")

    transactions = db.query(Transaction).filter(
            (Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id)
        ).order_by(Transaction.timestamp.desc()).limit(limit).all()

    return transactions


def get_outgoing_transactions_count(db: Session, business_id: str) -> int:
    return db.query(Transaction).filter(Transaction.sender_id == business_id).count()
