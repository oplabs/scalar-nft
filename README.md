# Scalar NFT

Proof of Concept ERC-721 token that gives the creator mint rights scaled with marketplace trades.

## How it works

The contract is an EIP-721 token contract that handles mint sales for a set price. Instead of relying on traditional royalties enforced by exchanges, it grants the owner mint rights that scale with DEX trades.

Exchanges are identified by the caller address during a transfer. For instance, a Seaport conduit will call `safeTransferFrom()` which will increment a trade counter when detected. For every N trades, the creator is granted permission to mint M tokens beyond the max supply.

## Deploy

You can deploy using the provided deployment script:

```bash
$ ape run deploy --network ethereum:goerli --price_wei 150000000000000000 --max_supply 1024 Scalar SCL
```

## Development

Setup the Ape env:

```bash
python3 -m venv /path/to/venv
. /path/to/venv/bin/activate
pip install -r requirements.lock.txt
```

You can run tests like this:

```bash
ape compile
ape test --network ethereum:local:test
```
