import click
from ape import accounts, project
from ape.cli import network_option, NetworkBoundCommand


def si(s):
    return str(int(s))


DEFAULT_PRICE = int(1e16)  # 0.01 ETH
DEFAULT_RATE = int(1e15)  # 1:1000 (mints:trades)
DEFAULT_MAX_SUPPLY = int(1e3)  # 1,000
DEFAULT_EXCHANGES = [
    "0x1E0049783F008A0085193E00003D00cd54003c71",  # OpenSea (Seaport Conduit)
    "0x4feE7B061C97C9c496b01DbcE9CDb10c02f0a0Be",  # Rarible TransferProxy
    "0xf42aa99F011A1fA7CDA90E5E98b277E306BcA83e",  # LooksRare TransferManagerERC721
]


@click.command(cls=NetworkBoundCommand)
@network_option()
@click.argument("name")
@click.argument("symbol")
@click.option("-a", "--account", help="Account to use for deployment")
@click.option(
    "-p",
    "--price_wei",
    type=int,
    default=DEFAULT_PRICE,
    help="The price (in wei) to mint a single token",
)
@click.option(
    "-t",
    "--tariff_rate",
    type=int,
    default=DEFAULT_RATE,
    help="The tariff rate (1e15 == 1:1000, 1e18 == 1:1)",
)
@click.option(
    "-m",
    "--max_supply",
    type=int,
    default=DEFAULT_MAX_SUPPLY,
    help="The max supply (excluding tariff)",
)
@click.option(
    "-e",
    "--exchange",
    multiple=True,
    default=DEFAULT_EXCHANGES,
    help="Exchanges that will accrue tariff upon transfer",
)
def cli(
    network,
    name,
    symbol,
    max_supply,
    price_wei,
    tariff_rate,
    exchange,
    account,
):
    deployer = accounts.load(account) if account else accounts[0]

    print(f"Minting {name} ({symbol})")
    print(f"=====================================")
    print(f"Price: {int(price_wei) / 1e18} ETH")
    print(f"Tarrif Rate: 1 mint per {int(1e18) // int(tariff_rate)} trades")
    print(f"Exchanges: {', '.join(exchange)}")
    print(f"Deployer: {deployer}")

    constructor_args = [
        name,
        symbol,
        price_wei,
        tariff_rate,
        max_supply,
        list(exchange),
    ]

    scalar = deployer.deploy(project.ScalarToken, *constructor_args)

    assert scalar.name() == name
    assert scalar.symbol() == symbol
    assert scalar.price() == price_wei
    assert scalar.maxSupply() == max_supply
    assert scalar.tariffRate() == tariff_rate
