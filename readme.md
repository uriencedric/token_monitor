# Token Monitoring Script

This Python script monitors the Solana blockchain for new token mint events and validates the tokens against a set of predefined criteria. It logs all relevant activities and validations to both the console and a log file.

---

## Features

1. **Token Monitoring**:
   - Scans new blocks on the Solana blockchain for SPL token mint events.
   - Identifies and logs potential token candidates.

2. **Token Validation**:
   - Validates mint authority and freeze authority of tokens.
   - Checks the supply and associated token accounts.

3. **Logging**:
   - Logs messages to a file (`monitor_log.txt`) and the console.
   - Includes timestamps and log levels for better traceability.

---

## Requirements

### Python Packages
Install the required dependencies using `pip`:

```bash
pip install solana pybase58
```

### Environment
- Replace sensitive details like private keys in the `config` file.
- Ensure the Solana node URL is accessible (default: `https://api.mainnet-beta.solana.com`).

---

## Configuration

1. **Wallet Details**:
   - Store your Solana wallet's private key in the `config.py` file:
     ```python
     solana_wallet_private_key = "<your_base58_encoded_private_key>"
     ```

2. **Node URL**:
   - Ensure the script points to your preferred Solana node provider:
     ```python
     NODE_URL = "https://api.mainnet-beta.solana.com"
     ```

---

## How to Use

1. Clone the repository or download the script.
2. Install the required dependencies.
3. Update the `config.py` file with your private key.
4. Run the script:

```bash
python run.py
```

5. Monitor logs in the console or the `monitor_log.log` file.

---

## Log File

- All events and errors are logged to `monitor_log.log`.
- Log entries include:
  - **Timestamps**: When the event occurred.
  - **Log Level**: Severity (INFO, WARNING, ERROR).
  - **Message**: Details of the event.

---

## Example Output

### Console Output
```plaintext
2024-12-17 12:00:00 [INFO] Monitoring for new token mint events...
2024-12-17 12:05:00 [INFO] Potential new token detected in slot 12345678: recent block hash: abc123...
2024-12-17 12:05:01 [INFO] Mint address with supply found: 123abc...
2024-12-17 12:05:02 [INFO] Validation passed for token: 123abc...
```

### Log File Output (`monitor_log.log`)
```plaintext
2024-12-17 12:00:00 [INFO] Monitoring for new token mint events...
2024-12-17 12:05:00 [INFO] Potential new token detected in slot 12345678: recent block hash: abc123...
2024-12-17 12:05:01 [INFO] Mint address with supply found: 123abc...
2024-12-17 12:05:02 [INFO] Validation passed for token: 123abc...
```

---

## Notes

- **Security**:
  - Never hardcode sensitive information directly in the script. Use environment variables or secure vaults for private keys.
  - Validate the source and authenticity of tokens before interacting with them.

- **Performance**:
  - The script uses a polling mechanism to fetch new blocks. For high-performance requirements, consider subscribing to real-time events using a websocket-based implementation.

---

## Future Enhancements

- Add support for interacting with Serum DEX to automate token purchases.
- Implement a websocket-based event listener for real-time token detection.
- Enhance token validation criteria with more detailed metadata analysis.

---

## License
This project is licensed under the MIT License.

