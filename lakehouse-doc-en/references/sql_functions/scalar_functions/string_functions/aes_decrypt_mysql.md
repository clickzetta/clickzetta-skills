### AES_DECRYPT_MYSQL 
```
aes_decrypt_mysql(expr binary, key binary, mode string, [iv binary])
```
####  Description
The AES_DECRYPT_MYSQL function is used to perform AES decryption on binary data. This function is compatible with MySQL's AES encryption algorithm, ensuring seamless integration with encrypted data in MySQL databases.

#### Parameter Description
* expr (binary): The binary ciphertext data to be decrypted.
* key (binary): The key used for decryption, which must be 16, 24, or 32 bytes in length.
* mode (string): The AES encryption mode, formatted as "aes-bits-mode", defaulting to "aes-128-ecb". Optional modes include "aes-128-ecb", "aes-192-ecb", "aes-256-ecb", "aes-128-cbc", "aes-192-cbc", "aes-256-cbc".
* iv (binary, optional): The Initial Vector in the AES encryption algorithm, which should be the same length as the encryption block size. Defaults to empty.

#### Return Result
Returns the decrypted binary data.

#### Usage Example
Using AES-128-ECB mode to decrypt data:

```sql
SELECT CAST(AES_DECRYPT_MYSQL(UNBASE64('fOltPBoMXnbhu54SSxaaAQ=='), 'namePURPMEF4uI2mQSbrWOhpAvu6OGbE4U') AS STRING);
```
Results:
```
1234
```
#### Notes
* Please ensure that the provided key and mode are the same as those used during encryption, otherwise decryption will fail.
* When using CBC mode, a correct initialization vector (IV) must be provided, otherwise the decryption result may be incorrect.
* Considering security, it is recommended to use 256-bit AES encryption combined with an appropriate encryption mode, such as AES-256-CBC.