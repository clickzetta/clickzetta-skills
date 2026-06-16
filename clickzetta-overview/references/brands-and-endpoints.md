# ClickZetta Brand Relationships and Service Endpoints

## Brand Relationships

ClickZetta is the technology brand name. The same product uses different brands in different markets:

| Brand | Market | Website | Documentation |
|---|---|---|---|
| **Yunqi** | China | www.yunqi.tech | www.yunqi.tech/documents |
| **Singdata** | International | www.singdata.com | www.singdata.com/documents |
| **ClickZetta** | Technology brand (universal) | — | — |

> **Yunqi Lakehouse = ClickZetta Lakehouse = Singdata Lakehouse** — all three refer to the same product.
> When users mention "Yunqi", "Singdata", or "ClickZetta", they all refer to the same Lakehouse platform.

---

## China (Yunqi) Service Endpoints

Console: `https://<instance_name>.app.clickzetta.com`

JDBC URL format: `jdbc:clickzetta://<instance_name>.<region_code>.api.clickzetta.com/<workspace>`

| Cloud Provider | Region | Region Code | API Endpoint |
|---|---|---|---|
| Alibaba Cloud | Shanghai | `cn-shanghai-alicloud` | `<instance>.cn-shanghai-alicloud.api.clickzetta.com` |
| Alibaba Cloud | Hangzhou | `cn-hangzhou-alicloud` | `<instance>.cn-hangzhou-alicloud.api.clickzetta.com` |
| Alibaba Cloud | Beijing | `cn-beijing-alicloud` | `<instance>.cn-beijing-alicloud.api.clickzetta.com` |
| Tencent Cloud | Shanghai | `cn-shanghai-tencentcloud` | `<instance>.cn-shanghai-tencentcloud.api.clickzetta.com` |
| AWS Cloud | Beijing | `cn-north-1-aws` | `<instance>.cn-north-1-aws.api.clickzetta.com` |

---

## International (Singdata) Service Endpoints

Account console: `https://accounts.app.singdata.com` or `https://<account_name>.accounts.app.singdata.com`

Instance console: `https://<instance_name>.app.singdata.com`

Workspace list: `https://<instance_name>.app.lakehouse.singdata.com/workspace`

JDBC URL format: `jdbc:clickzetta://<instance_name>.<region_code>.api.singdata.com/<workspace>`

| Cloud Provider | Region | Region Code | API Endpoint |
|---|---|---|---|
| Alibaba Cloud | Singapore | `ap-southeast-1-alicloud` | `<instance>.ap-southeast-1-alicloud.api.singdata.com` |
| Amazon Web Services | Singapore | `ap-southeast-1-aws` | `<instance>.ap-southeast-1-aws.api.singdata.com` |

---

## SDK / Connection Parameter Endpoints

The `service` parameter in the Python SDK (`clickzetta-connector-python`) takes the API endpoint (without the `jdbc:clickzetta://` prefix and instance name):

```python
# China (Yunqi)
conn = connect(service='cn-shanghai-alicloud.api.clickzetta.com', instance='your_instance', ...)

# International (Singdata)
conn = connect(service='ap-southeast-1-alicloud.api.singdata.com', instance='your_instance', ...)
```

The `.service()` parameter in the Java SDK (`clickzetta-java`) works the same way:

```java
// China (Yunqi)
ClickZettaClient.newBuilder()
    .service("cn-shanghai-alicloud.api.clickzetta.com")
    .instance("your_instance")
    ...

// International (Singdata)
ClickZettaClient.newBuilder()
    .service("ap-southeast-1-alicloud.api.singdata.com")
    .instance("your_instance")
    ...
```
