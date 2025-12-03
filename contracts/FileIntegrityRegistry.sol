// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title File Integrity Registry
/// @notice Menyimpan hash file pada blockchain untuk deteksi perubahan (tamper detection)
contract FileIntegrityRegistry {
    struct FileRecord {
        address owner;
        uint256 timestamp;
        string fileHash;   // SHA-256 hash (hex)
        string metadata;   // keterangan opsional
    }

    // mapping dari hash ke record
    mapping(bytes32 => FileRecord) private records;

    event FileRegistered(
        bytes32 indexed id,
        address indexed owner,
        string fileHash,
        string metadata,
        uint256 timestamp
    );

    /// @notice Mendaftarkan file ke blockchain berdasarkan hash-nya
    function registerFile(
        string calldata fileHash,
        string calldata metadata
    ) external returns (bytes32) {
        require(bytes(fileHash).length > 0, "File hash required");

        bytes32 id = keccak256(abi.encodePacked(fileHash));
        FileRecord storage rec = records[id];

        require(rec.timestamp == 0, "File already registered");

        rec.owner = msg.sender;
        rec.timestamp = block.timestamp;
        rec.fileHash = fileHash;
        rec.metadata = metadata;

        emit FileRegistered(id, msg.sender, fileHash, metadata, block.timestamp);
        return id;
    }

    /// @notice Mengambil informasi file berdasarkan hash
    function getFileRecord(
        string calldata fileHash
    )
        external
        view
        returns (
            address owner,
            uint256 timestamp,
            string memory storedHash,
            string memory metadata
        )
    {
        bytes32 id = keccak256(abi.encodePacked(fileHash));
        FileRecord storage rec = records[id];
        require(rec.timestamp != 0, "File not found");

        return (rec.owner, rec.timestamp, rec.fileHash, rec.metadata);
    }

    /// @notice Mengecek apakah hash file sudah ada
    function isFileRegistered(
        string calldata fileHash
    ) external view returns (bool) {
        bytes32 id = keccak256(abi.encodePacked(fileHash));
        return records[id].timestamp != 0;
    }
}
