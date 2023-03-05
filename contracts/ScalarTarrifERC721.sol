// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

error MaxSupplyReached();

/*
 * ScalarTarrifERC721
 *
 * ERC-721 that gives the creator mint rights scaled with trades on known
 * marketplaces.  See ScalarToken.sol for usage.
 */
contract ScalarTarrifERC721 is ERC721, ERC721Burnable, Ownable {
    using Counters for Counters.Counter;

    // Max supply, not including the tariff
    uint256 public maxSupply = 0;
    // The amount of tokens that are reserved for the creator as trading fees
    uint256 public tariffEarned = 0;
    // The amount of tokens granted per 1e18 trades (1e15 = 0.1%, 1e18 = 100%)
    uint256 public tariffRate = 0;
    // Total transfers made by recognized exchanges
    Counters.Counter private _tradeCounter;
    // The current token ID
    Counters.Counter private _tokenIdCounter;
    // The known exchanges that will accrue tariff fees
    mapping(address => bool) public exchanges;

    constructor(
        string memory name_,
        string memory symbol_,
        uint256 tariffRate_,
        uint256 maxSupply_,
        address[] memory exchanges_
    ) ERC721(name_, symbol_) {
        tariffRate = tariffRate_;
        maxSupply = maxSupply_;

        for (uint256 i = 0; i < exchanges_.length; ++i) {
            exchanges[exchanges_[i]] = true;
        }
    }

    // @notice total tokens minted
    function totalSupply() public view returns (uint256) {
        return _tokenIdCounter.current();
    }

    // @notice total trades counted
    function tradeCount() public view returns (uint256) {
        return _tradeCounter.current();
    }

    // @notice enable/disable tariffs for given address
    function setExchange(address exchange, bool val) public onlyOwner {
        exchanges[exchange] = val;
    }

    // @dev mint a token
    function _mintSale(address to) internal {
        uint256 tokenId = _tokenIdCounter.current();

        if (tokenId >= maxSupply) {
            revert MaxSupplyReached();
        }

        _tokenIdCounter.increment();
        _safeMint(to, tokenId);
    }

    // @dev mint a token
    function _mintTariff(address to) internal {
        uint256 tokenId = _tokenIdCounter.current();

        if (tokenId < maxSupply || tokenId >= maxSupply + tariffEarned) {
            revert MaxSupplyReached();
        }

        _mintUnsafe(to, tokenId);
    }

    /*
     * @dev mint a specific token ID without taking supply restrictions into
     *      consideration.  Use _mintSale() or _mintTariff() instead.
     */
    function _mintUnsafe(address to, uint256 tokenId) internal {
        _tokenIdCounter.increment();
        // oh the ironing
        _safeMint(to, tokenId);
    }

    function _afterTokenTransfer(
        address from,
        address to,
        uint256 firstTokenId,
        uint256 batchSize
    ) internal override {
        super._afterTokenTransfer(from, to, firstTokenId, batchSize);

        // If the transfer is from a known exchange, accrue tariff fees
        if (exchanges[msg.sender]) {
            uint256 expectedTariff = (tariffRate * _tradeCounter.current()) /
                1e18;

            if (expectedTariff > tariffEarned) {
                tariffEarned = expectedTariff;
            }

            _tradeCounter.increment();
        }
    }
}
