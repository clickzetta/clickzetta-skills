### AES\_ENCRYPT\_MYSQL 
```
aes_encrypt_mysql(expr, key [, mode [, iv]])
```
####  Description

The AES\_ENCRYPT\_MYSQL function is used to perform AES encryption on binary data. This function is compatible with MySQL's AES encryption function, making it convenient to implement data encryption in SQL statements.

#### Parameter Description

* **expr** (binary): The binary data to be encrypted.
* **key** (binary): The key used for encryption, the key length must be 16, 24, or 32 bytes.
* **mode** (string, optional): AES encryption mode, formatted as "aes-bits-mode", default is "aes-128-ecb". Optional modes are "aes-128-ecb", "aes-192-ecb", "aes-256-ecb", "aes-128-cbc", "aes-192-cbc", "aes-256-cbc".
* **iv** (binary, optional): The initialization vector (IV) in the AES encryption algorithm, the length should be the same as the key length, default is empty.

#### Return Result

Returns the encrypted binary data.

####  Example

1. Encrypt the string "1234" using AES-128-ECB mode:
```sql
SELECT base64(aes_encrypt_mysql('1234', 'namePURPMEF4uI2mQSbrWOhpAvu6OGbE4U', 'aes-128-ecb'));
+--------------------------+
|           res            |
+--------------------------+
| fOltPBoMXnbhu54SSxaaAQ== |
+--------------------------+
```
2. Encrypt the string "Hello, world!" using AES-256-CBC mode:
```sql
SELECT base64(aes_encrypt_mysql('Hello, world!', 'mySecretKey12345678', 'aes-256-cbc', '1234567890123456'));
+--------------------------+
|           res            |
+--------------------------+
| AiVMpzHAOQdAEGgVjP60ig== |
+--------------------------+
```
#### Precautions

* The key length must be 16, 24, or 32 bytes; otherwise, the encryption process will fail.
* The initialization vector (IV) is only effective in CBC mode; in ECB mode, the IV parameter will be ignored.
* To ensure security, please use a sufficiently strong key and a randomly generated initialization vector (IV).
* The encryption result is binary data, which can be converted to a printable string form using the base64 function.

^