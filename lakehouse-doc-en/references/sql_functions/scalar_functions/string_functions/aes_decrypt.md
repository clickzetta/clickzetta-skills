### AES_DECRYPT 
```
aes_decrypt(expr, key [, mode [, padding]])
```
####  Description
The AES_DECRYPT function is used to perform AES (Advanced Encryption Standard) decryption on binary data. This function supports multiple modes and padding methods to meet different security needs.

#### Parameter Description
* **expr** (binary): The binary ciphertext to be decrypted.
* **key** (binary): The key used for decryption, the key length must be 16, 24, or 32 bytes.
* **mode** (string, optional): The encryption mode, options include 'ECB' and 'GCM'. The default value is 'ECB'.
* **padding** (string, optional): The padding method, options include 'NONE', 'PKCS', and 'DEFAULT'. 'NONE' means no padding, 'PKCS' means using the Public Key Cryptography Standards algorithm for padding, 'DEFAULT' means no padding in 'GCM' mode and using 'PKCS' padding in 'ECB' mode. The default value is 'DEFAULT'.

#### Return Result
Returns the decrypted binary data.

#### Usage Example
1. Decrypt data using ECB mode and PKCS padding:
```sql
SELECT CAST(aes_decrypt(unbase64('xrsSNC1NEmSaAUjrTV7VlA=='), '0000111122223333', 'ECB') AS string);
```
Results:
```
Hello World
```
2. Decrypt data using GCM mode and no padding:
```sql
SELECT CAST(aes_decrypt(unbase64('t6rWxtWMvIP9zNTFpVUEcpphuGdBTnUx+jOKrbNfHThVlB1DMzlt'), '0000111122223333', 'GCM' ) AS string);
```
Results:
```
Hello World
```
#### Precautions
* Please ensure to provide the correct key and padding method, otherwise the decryption result may be incorrect.
* When using GCM mode, pay attention to the choice of padding method, as different padding methods may affect the decryption result.
* To ensure data security, it is recommended to use complex keys and appropriate encryption modes.