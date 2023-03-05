// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import { ScalarTarrifERC721 } from "./ScalarTarrifERC721.sol";

error InvalidCount();
error NotEnoughEther();

/*
 * ScalarToken
 *
 * Proof of Concept ERC-721 token that gives the creator mint rights scaled
 * with marketplace trades.
 */
contract ScalarToken is ScalarTarrifERC721 {
    uint256 public price = 0;

    /*
     * @param name_ NFT Token name
     * @param symbol_ NFT Token symbol
     * @param price_ Price in wei for each token
     * @param tariffRate_ Amount of tokens to mint per 1e18 trades
     * @param maxSupply_ Max supply of tokens (excluding tariffs)
     * @param exchanges_ Array of addresses that will be recognized as
     *      exchanges for purposes of calculating tariffs.
     */
    constructor(
        string memory name_,
        string memory symbol_,
        uint256 price_,
        uint256 tariffRate_,
        uint256 maxSupply_,
        address[] memory exchanges_
    ) ScalarTarrifERC721(name_, symbol_, tariffRate_, maxSupply_, exchanges_) {
        price = price_;
    }

    /*
     * @notice for owner to withdraw funds paid to the contract
     */
    function withdraw() public onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }

    /*
     * @notice mint tokens for as part of the initial sale.
     */
    function mint(address to, uint256 count) public payable {
        if (count < 1) {
            revert InvalidCount();
        }

        if (msg.value < price * count) {
            revert NotEnoughEther();
        }

        for (uint256 i = 0; i < count; ) {
            _mintSale(to);

            unchecked {
                ++i;
            }
        }
    }

    /*
     * @notice mint multiple tokens for owner tariff. This will only allow
     *      mints after the initial sale max supply has been sold.
     */
    function mintTariff(address to, uint256 count) public onlyOwner {
        if (count < 1) {
            revert InvalidCount();
        }

        for (uint256 i = 0; i < count; ) {
            _mintTariff(to);

            unchecked {
                ++i;
            }
        }
    }
}
