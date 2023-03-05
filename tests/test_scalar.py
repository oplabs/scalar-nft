# test Scalar token
import ape
import pytest
from eth_utils import decode_hex, encode_hex
from web3 import Web3


def four_byte(s):
    return decode_hex(Web3.keccak(text=s).hex()[2:10])


InvalidCountError = four_byte("InvalidCount()")
MaxSupplyReachedError = four_byte("MaxSupplyReached()")
NotEnoughEthertError = four_byte("NotEnoughEther()")


@pytest.fixture
def owner(accounts):
    return accounts[0]


@pytest.fixture
def alice(accounts):
    return accounts[1]


@pytest.fixture
def bob(accounts):
    return accounts[2]


@pytest.fixture
def seaport(accounts):
    return accounts[3]


@pytest.fixture
def looksrare(accounts):
    return accounts[4]


@pytest.fixture
def scalar(looksrare, owner, project, seaport):
    # 1e17 == 1:10
    return owner.deploy(
        project.ScalarToken,
        "Scalar",
        "SCL",
        int(1e16),  # 0.01 ETH
        int(1e17),
        100,
        [looksrare, seaport],
    )


def simulate_sale(contract, exchange, seller, buyer, token_id):
    if not contract.isApprovedForAll(seller, exchange):
        contract.setApprovalForAll(exchange, True, sender=seller)
    return contract.safeTransferFrom(seller, buyer, token_id, sender=exchange)


def mint_max_supply(contract, owner, recipient):
    price = contract.price()
    max_supply = contract.maxSupply()
    contract.mint(recipient, max_supply, sender=owner, value=price * max_supply)


def test_deploy(project, owner, seaport):
    name = "DeployTest"
    symbol = "DT"
    price = int(1e16)
    tarrif_rate = int(1e15)

    scalar = owner.deploy(
        project.ScalarToken, name, symbol, price, tarrif_rate, 666, [seaport]
    )

    assert scalar.name() == name
    assert scalar.symbol() == symbol
    assert scalar.price() == price
    assert scalar.owner() == owner
    assert scalar.totalSupply() == 0
    assert scalar.maxSupply() == 666
    assert scalar.tariffEarned() == 0
    assert scalar.tariffRate() == tarrif_rate
    assert scalar.exchanges(seaport)


def test_mint_single(alice, owner, scalar):
    assert scalar.balanceOf(alice) == 0

    scalar.mint(alice, 1, sender=owner, value=scalar.price())

    assert scalar.balanceOf(alice) == 1
    assert scalar.totalSupply() == 1
    assert scalar.tariffEarned() == 0

    # Verify withdraw works and revenue is expected
    owner_balance_before = owner.balance
    assert scalar.balance == scalar.price()

    tx = scalar.withdraw(sender=owner)
    tx_fee = tx.gas_used * tx.gas_price
    expected_diff = scalar.price() - tx_fee
    owner_balance_after = owner.balance
    assert owner.balance == owner_balance_before + expected_diff
    assert scalar.balance == 0


def test_mint_batch(alice, owner, scalar):
    assert scalar.balanceOf(alice) == 0

    scalar.mint(alice, 19, sender=owner, value=scalar.price() * 19)

    assert scalar.balanceOf(alice) == 19
    assert scalar.totalSupply() == 19
    assert scalar.tariffEarned() == 0


def test_tarrif(alice, bob, owner, scalar, seaport):
    assert scalar.balanceOf(alice) == 0
    scalar.mint(alice, 1, sender=owner, value=scalar.price())
    assert scalar.balanceOf(alice) == 1

    tariff_rate = scalar.tariffRate()
    tx_per_tariff = int(1e18) // tariff_rate
    count = tx_per_tariff // 2

    for i in range(0, count + 1):
        simulate_sale(scalar, seaport, alice, bob, 0)
        simulate_sale(scalar, seaport, bob, alice, 0)

    assert scalar.tariffEarned() == 1


def test_tarrif2(alice, bob, looksrare, owner, scalar, seaport):
    assert scalar.balanceOf(alice) == 0
    scalar.mint(alice, 1, sender=owner, value=scalar.price())
    assert scalar.balanceOf(alice) == 1

    tariff_rate = scalar.tariffRate()
    tx_per_tariff = int(1e18) // tariff_rate
    count = tx_per_tariff * 4

    for i in range(0, count + 1):
        simulate_sale(scalar, seaport, alice, bob, 0)
        simulate_sale(scalar, looksrare, bob, alice, 0)

    assert scalar.tariffEarned() == 8


def test_tarrif_mint(alice, bob, owner, scalar, seaport):
    mint_max_supply(scalar, owner, alice)

    tariff_rate = scalar.tariffRate()
    tx_per_tariff = int(1e18) // tariff_rate
    count = tx_per_tariff * 2

    for i in range(0, count + 1):
        simulate_sale(scalar, seaport, alice, bob, 0)
        simulate_sale(scalar, seaport, bob, alice, 0)

    assert scalar.tariffEarned() == 4

    scalar.mintTariff(owner, 1, sender=owner)
    assert scalar.balanceOf(owner) == 1


def test_tarrif_mint_batch(alice, bob, looksrare, owner, scalar, seaport):
    mint_max_supply(scalar, owner, alice)

    tariff_rate = scalar.tariffRate()
    tx_per_tariff = int(1e18) // tariff_rate
    count = tx_per_tariff * 4

    for i in range(0, count + 1):
        simulate_sale(scalar, seaport, alice, bob, 0)
        simulate_sale(scalar, looksrare, bob, alice, 0)

    assert scalar.tariffEarned() == 8
    scalar.mintTariff(owner, 8, sender=owner)
    assert scalar.balanceOf(owner) == 8


def test_tarrif_mint_fail(alice, bob, owner, scalar, seaport):
    assert scalar.balanceOf(alice) == 0
    mint_max_supply(scalar, owner, alice)
    assert scalar.balanceOf(alice) == scalar.maxSupply()
    assert scalar.totalSupply() == scalar.maxSupply()

    tariff_rate = scalar.tariffRate()
    tx_per_tariff = int(1e18) // tariff_rate
    count = tx_per_tariff // 2

    for i in range(0, count + 1):
        simulate_sale(scalar, seaport, alice, bob, 0)
        simulate_sale(scalar, seaport, bob, alice, 0)

    assert scalar.tariffEarned() == 1
    assert scalar.totalSupply() == scalar.maxSupply()

    scalar.mintTariff(owner, 1, sender=owner)
    assert scalar.totalSupply() == scalar.maxSupply() + scalar.tariffEarned()

    print(
        "InvalidCountError:", InvalidCountError, encode_hex(InvalidCountError)
    )
    print(
        "MaxSupplyReachedError:",
        MaxSupplyReachedError,
        encode_hex(MaxSupplyReachedError),
    )
    print(
        "NotEnoughEthertError:",
        NotEnoughEthertError,
        encode_hex(NotEnoughEthertError),
    )

    with ape.reverts(str(MaxSupplyReachedError)):
        scalar.mintTariff(owner, 1, sender=owner)

    with ape.reverts(str(MaxSupplyReachedError)):
        scalar.mintTariff(owner, 4, sender=owner)


def test_tarrif_mint_batch_fail(alice, bob, looksrare, owner, scalar, seaport):
    assert scalar.balanceOf(alice) == 0
    mint_max_supply(scalar, owner, alice)
    assert scalar.balanceOf(alice) == scalar.maxSupply()

    tariff_rate = scalar.tariffRate()
    tx_per_tariff = int(1e18) // tariff_rate
    count = tx_per_tariff * 4

    for i in range(0, count + 1):
        simulate_sale(scalar, seaport, alice, bob, 0)
        simulate_sale(scalar, looksrare, bob, alice, 0)

    assert scalar.tariffEarned() == 8
    assert scalar.totalSupply() == scalar.maxSupply()

    scalar.mintTariff(owner, 8, sender=owner)
    assert scalar.totalSupply() == scalar.maxSupply() + scalar.tariffEarned()

    with ape.reverts(str(MaxSupplyReachedError)):
        scalar.mintTariff(owner, 1, sender=owner)

    with ape.reverts(str(MaxSupplyReachedError)):
        scalar.mintTariff(owner, 4, sender=owner)
