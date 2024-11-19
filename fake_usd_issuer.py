from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset
from security import safe_requests

server = Server("https://horizon-testnet.stellar.org")

# Step 1: Create Issuer Account
issuer_keypair = Keypair.random()
FAKE_USD_ISSUER_PUBLIC_KEY = issuer_keypair.public_key
FAKE_USD_ISSUER_SECRET_KEY = issuer_keypair.secret

# Fund the issuer account using Friendbot for testnet
url = f"https://friendbot.stellar.org?addr={FAKE_USD_ISSUER_PUBLIC_KEY}"
response = safe_requests.get(url)
if response.status_code != 200:
    raise Exception("Failed to fund issuer account")

# Define the fake USD asset
FAKE_USD = Asset("FAKEUSD", FAKE_USD_ISSUER_PUBLIC_KEY)

# Create a distributor account
distributor_keypair = Keypair.random()
FAKE_USD_DISTRIBUTOR_PUBLIC_KEY = distributor_keypair.public_key
FAKE_USD_DISTRIBUTOR_SECRET_KEY = distributor_keypair.secret

# Fund the distributor account using Friendbot for testnet
url = f"https://friendbot.stellar.org?addr={FAKE_USD_DISTRIBUTOR_PUBLIC_KEY}"
response = safe_requests.get(url)
if response.status_code != 200:
    raise Exception("Failed to fund distributor account")

# Trust the fake USD asset from the distributor account
distributor_account = server.load_account(FAKE_USD_DISTRIBUTOR_PUBLIC_KEY)
transaction = TransactionBuilder(
    source_account=distributor_account,
    network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
    base_fee=server.fetch_base_fee()
).append_change_trust_op(
    asset=FAKE_USD
).build()
transaction.sign(distributor_keypair)
response = server.submit_transaction(transaction)
if response.get("successful") != True:
    raise Exception("Failed to create trustline for fake USD")

# Issue the fake USD asset to the distributor account
issuer_account = server.load_account(FAKE_USD_ISSUER_PUBLIC_KEY)
transaction = TransactionBuilder(
    source_account=issuer_account,
    network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
    base_fee=server.fetch_base_fee()
).append_payment_op(
    destination=FAKE_USD_DISTRIBUTOR_PUBLIC_KEY,
    amount="10000000",  # Large amount for issuing
    asset=FAKE_USD
).build()
transaction.sign(FAKE_USD_ISSUER_SECRET_KEY)
response = server.submit_transaction(transaction)
if response.get("successful") != True:
    raise Exception("Failed to issue fake USD")

# Create an offer to exchange Lumens for fake USD
offer_transaction = TransactionBuilder(
    source_account=distributor_account,
    network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
    base_fee=server.fetch_base_fee()
).append_manage_sell_offer_op(
    selling=FAKE_USD,
    buying=Asset.native(),
    amount="10000000",
    price="0.9"  # Higher rate: 1 fake USD = 100 Lumens
).build()
offer_transaction.sign(distributor_keypair)
response = server.submit_transaction(offer_transaction)

print("Exchange offer created successfully")
print("Distribution account:", FAKE_USD_DISTRIBUTOR_PUBLIC_KEY)
print("Issuer account:", FAKE_USD_ISSUER_PUBLIC_KEY)
if response.get("successful") != True:
    raise Exception("Failed to create exchange offer")

