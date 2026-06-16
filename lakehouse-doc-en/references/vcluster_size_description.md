# Calculation Cluster Specification Code Change Description

As more and more customers use Singdata Lakehouse's calculation clusters, we found that the original calculation cluster specifications, which grew exponentially by a factor of 2, might cause too large a gap between specifications and resource waste. Therefore, we have modified the calculation cluster specifications to allow for more granular planning of calculation cluster specifications, improving resource utilization efficiency and reducing costs.

The specific adjustments to the specifications are as follows:

## **Original Calculation Cluster Specifications**

From XS to 5XLarge, each level increase doubles the computing resources and also doubles the resource consumption:

|                   |                  |                                            |
| ----------------- | ---------------- | ------------------------------------------ |
| **Specification** | **Abbreviation** | **Hourly Consumption** (**CRU**\***hour**) |
| XSMALL            | XS               | 1                                          |
| SMALL             | S                | 2                                          |
| MEDIUM            | M                | 4                                          |
| LARGE             | L                | 8                                          |
| XLARGE            | XL               | 16                                         |
| 2XLARGE           | 2XL              | 32                                         |
| 3XLARGE           | 3XL              | 64                                         |
| 4XLARGE           | 4XL              | 128                                        |
| 5XLARGE           | 5XL              | 256                                        |

## **New Calculation Cluster Specifications**

Each type of calculation cluster is represented by CRU (Compute Resource Unit). Different types of calculation clusters, due to their suitable tasks and resource configurations, can be specified differently.

The detailed specifications of various calculation clusters are as follows:

| **Type**                                | **Minimum Specification** (**CRU**) | **Maximum Specification** (**CRU**) | **Default Value** (**CRU**) | **Step Size**&#xA; (Minimum unit of specification increase/decrease)                                                                                                                                   |
| --------------------------------------- | ----------------------------------- | ----------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| General Purpose&#xA; (GP Vcluster)      | 1                                   | 256                                 | 1                           | 1 (Specification examples: 1, 2, 3, 4, 5, 6...256)                                                                                                                                                     |
| Analytical&#xA; (AP Vcluster)           | 1                                   | 256                                 | 1                           | Powers of 2 (Specification examples: 1, 2, 4, 8, 16, 32, 64, 128, 256)                                                                                                                                 |
| Integration&#xA; (Integration Vcluster) | 0.25                                | 256                                 | 0.5                         | 1 (Specification sequence: there are two special small specifications of 0.25 CRU and 0.5 CRU, the step size for other specifications is 1. Specification examples: 0.25, 0.5, 1, 2, 3, 4, 5, 6...256) |

The amount of computing resources consumed by each cluster per hour is its CRU specification\*1 hour, i.e., the unit is CRU\*hour. For example, an analytical calculation cluster with a specification of 3 CRU running for 1 hour consumes 3 CRU \* 1 hour = 3 CRU\*hour. The cost is also calculated according to the "CRU\*hour" unit price in the region where the calculation cluster is located.

## **Compatibility Description**

### Correspondence between New and Old Calculation Cluster Specifications

The specifications of existing calculation clusters will be automatically converted to the new specifications, and the computing resource consumption and costs per unit time will not change. The specific correspondence of specifications is as follows:

|                    |               |                      |
| ------------------ | ------------- | -------------------- |
| **Original Value** | **New Value** | **Applicable Scope** |
| XSMALL             | 1             | All types of VC      |
| SMALL              | 2             | All types of VC      |
| MEDIUM             | 4             | All types of VC      |
| LARGE              | 8             | All types of VC      |
| XLARGE             | 16            | All types of VC      |
| 2XLARGE            | 32            | All types of VC      |
| 3XLARGE            | 64            | All types of VC      |
| 4XLARGE            | 128           | All types of VC      |
| 5XLARGE            | 256           | All types of VC      |

### SQL Create New Compute Cluster

After the new specification code is launched, the SQL statements for creating and modifying compute clusters will temporarily be compatible with the old specification codes. That is, the Vcluster\_size parameter can support both numerical expressions and code expressions like 'XSMALL, SMALL' for compute cluster specifications. Please migrate to using numerical expressions for compute cluster specifications as soon as possible to avoid affecting the normal creation of compute clusters when switching to an incompatible version.

Example code for creating a new cluster is as follows:

```SQL
-- Create a compute cluster
CREATE VCLUSTER [IF NOT EXISTS] vc_name
objectProperties
[COMMENT '']
[WITH PROPERRIES ("key"="value"  "key"="value" ...)]
-- Parameter changes   
objectProperties ::=
            VCLUSTER_SIZE = NUM --0.25-256. Compatible with XSMALL | SMALL | MEDIUM | LARGE | XLARGE | 2XLARGE | 3XLARGE | 4XLARGE | 5XLARGE 
```

### Create a New Compute Cluster on the Web

When creating and modifying compute clusters on the web, the specifications of the compute cluster are now expressed in numerical terms. An example is shown below:

^

### Query Compute Cluster via SQL

When querying compute cluster specifications via SQL, all fields representing compute cluster specifications (vcluster\_size, min\_vcluster\_size, max\_vcluster\_size, and current\_vcluster\_size) are converted to numerical expressions of cluster size. For conversion rules, see the "Correspondence Between Old and New Compute Cluster Specifications" section above.

### Query Compute Cluster on the Web

The specifications of the compute cluster on the web are now expressed in numerical terms.

^

## Billing Instructions

Before and after the change in compute cluster specification codes, the resource consumption and hourly cost of compute clusters of the same specification **will not change**. The change only involves the billing unit: the compute specification changes from letters like "XS, S" to numerical expressions like 1CRU, 2CRU; the unit of compute resource consumption changes from CRU to CRU\*hour.

After the change, estimating the hourly resource consumption and cost of a cluster becomes simpler.

There is no need to remember that the "S" specification corresponds to 2 CRU per hour, and then multiply by the unit price to estimate the cost.

A compute cluster of 2 CRU consumes "2 CRU\*hour" per hour, and you only need to match the unit price to calculate the hourly cost.
