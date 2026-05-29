### AES_ENCRYPT 
```sql
aes_encrypt(expr, key [, mode])
```
####  Description
The `aes_encrypt` function is used to perform AES (Advanced Encryption Standard) encryption on binary strings. This function supports multiple encryption modes, including ECB and GCM.

#### Parameter Description
- `expr` (binary): The binary string to be encrypted.
- `key` (binary): The key used for encryption, the key length must be 16, 24, or 32 bytes.
- `mode` (string): The encryption mode, optional values include 'ECB' and 'GCM'. The default value is 'ECB'.

#### Return Value
Returns the encrypted binary string.

#### Usage Example
```sql
-- Encrypt using ECB mode
SELECT base64(aes_encrypt('Hello World', '0000111122223333', 'ECB'));
-- Result: xrsSNC1NEmSaAUjrTV7VlA==

-- Encrypt using GCM mode (Note: Due to the presence of a random initialization vector, the result may vary each time it is run)
SELECT base64(aes_encrypt('Hello World', '0000111122223333', 'GCM'));
-- Example result: 56vW7s/LqMLZ7dSdkshLNDSM6uo40nd3hUM1N5CpGAj1IL0xhebZ

-- Perform Base64 encoding on the encryption result
SELECT base64(aes_encrypt('MoonshotAI', '1234567890123456', 'GCM'));
-- Example result: sIGnurS00ovS4c+Ic8btSanlSvvWUBIixkakCSonEA6vE7aakfY=
```
#### Notes
- The key length must be 16, 24, or 32 bytes, otherwise encryption will fail.
- In GCM mode, a random initialization vector is generated each time encryption is performed, so the encryption results may vary.
- Using Base64 encoding makes it easy to transfer and store binary encrypted data in different environments.