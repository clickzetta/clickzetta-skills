# System Built-in Role Permission List

A Singdata Lakehouse account provides various system preset roles after creation. Different preset roles have different operation permission restrictions across various functional pages within the product. The specific permission list is as follows:

## Preset Role Permission Function List

### Studio Menu Permissions

| Role / Menu | Home | Workspace | Develop | Task Ops | Monitoring & Alerting | Data Catalog | Data Quality | Data Sharing | Cluster | Job History | Security | Approval | Workspace | Data Source | Private Link |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| instance_admin | Y | | | | Y | Y | Y | Y | | | Y | Y | Y | Y | Y |
| instance_user | Y | | | | | | | | | | | | | | |
| instance_datasource_admin (formerly datasource_admin) | Y | | | | | | | | | | | | | Y | |
| instance_datamap_admin (formerly datacatalog_admin) | Y | | | | | Y | | | | | | Y | | | |
| instance_datamap_user (formerly datacatalog_user) | Y | | | | | Y | | | | | | Y | | | |
| instance_sre | Y | Y | Y | Y | Y | Y | Y | | | | | | | | |
| instance_sensitivedata_viewer | Y | | | | | | | | | | | | | | |
| system_admin (to be deprecated) | Y | | | | | | | | | | | | | | |
| workspace_admin | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | | |
| workspace_analyst | Y | Y | Y | Y | Y | Y | Y | | Y | Y | | Y | Y | | |
| workspace_dev | Y | Y | Y | Y | Y | Y | Y | | Y | Y | | Y | Y | | |
| workspace_sre | Y | Y | Y | Y | Y | Y | Y | | Y | Y | | Y | Y | | |

### Development & Operations

| Category | Function Operation | instance_sre | workspace_admin | workspace_analyst | workspace_dev | workspace_sre |
| --- | --- | --- | --- | --- | --- | --- |
| Ops Center | Ops operations (series) | Y | Y | | | Y |
| Edit | | Y | | Y | | |
| Development > Task Group | Create task group | | Y | Y | Y | |
| | Submit task group | | Y | Y | Y | |
| | Modify task group | | Y | Y | Y | |
| | Delete task group | | Y | Y | Y | |
| | Create task group parameter | | Y | Y | Y | |
| | Add task node to task group | | Y | Y | Y | |
| | Remove from task group | | Y | Y | Y | |
| | View task group | Y | Y | Y | Y | Y |
| | View task group content | Y | Y | Y | Y | Y |
| Development > Folder | Create folder | | Y | Y | Y | |
| | Delete folder | | Y | Y | Y | |
| | Modify folder | | Y | Y | Y | |
| | View folder info | Y | Y | Y | Y | Y |
| Development > Task Node | Create script | | Y | Y | Y | |
| | Delete script | | Y | Y | Y | |
| | Modify script | | Y | Y | Y | |
| | Save script | | Y | Y | Y | |
| | View script content | Y | Y | Y | Y | Y |
| | Run script | | Y | Y | Y | |
| | View result info | | Y | Y | Y | |
| | Download data result | | Y | Y | Y | |
| | Copy data result | | Y | Y | Y | |
| | Configure schedule info | | Y | | Y | |
| | Submit task | | Y | | Y | |

### Data Integration

| Function Operation | instance_sre | datasource_admin | workspace_admin | workspace_analyst | workspace_dev | workspace_sre |
| --- | --- | --- | --- | --- | --- | --- |
| Create source data source | | Y | | | | |
| Preview source data source | Y | | Y | Y | Y | Y |
| Create target data source | | Y | Y | | Y | |
| Preview target data source | Y | | Y | Y | Y | Y |
| | | | | | | |
| | | | | | | |

### Data Assets

| Function Operation | instance_datamap_admin | instance_datamap_user | workspace_admin | workspace_analyst | workspace_dev |
| --- | --- | --- | --- | --- | --- |
| Data Assets home page | No permission restriction; all roles can open | | | | |
| Data Management | No permission restriction; all roles can open; content displayed according to data permissions | | | | |
| Data Management / Detail page | Y | Y | Y | Y | Y |
| Asset Overview | Y | | | | |
| Data Search | Y | Y | | | |
| | | | | | |

### Clusters

| Function Operation | workspace_admin | workspace_analyst | workspace_dev | workspace_sre |
| --- | --- | --- | --- | --- |
| View VC | Y | Y | Y | Y |
| Use VC | Y | Y | Y | |
| Create | Y | | | |
| Modify | Y | | | |
| Start/Stop | Y | | | |
| Delete | Y | | | |
| Set as default | Y | | | |

### Data Sources

| Function Operation | instance_datasource_admin | instance_admin | instance_user | instance_datamap_admin | instance_datamap_user | instance_sre | instance_sensitivedata_viewer | workspace_admin | workspace_dev | workspace_sre |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| View | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| Create | Y | Y | | | | | | | | |
| Modify | Y | | | | | | | Y | Y | |
| Test connectivity | Y | | | | | | | Y | Y | |
| Delete | Y | | | | | | | Y | Y | |

### Data Quality

| Function Operation | instance_admin | instance_sre | workspace_admin | workspace_dev | workspace_sre |
| --- | --- | --- | --- | --- | --- |
| Overview | Y | Y | Y | Y | Y |
| Create rule | | | Y | Y | |
| Dry run | Y | Y | Y | Y | Y |
| Delete | Y | | Y | Y | |
| Edit | | | Y | Y | |
| Mark check result as failed | Y | Y | Y | Y | |
| Re-check validation result | Y | Y | Y | Y | |

##

### Data Permissions

| **Role** | **Workspace** | **Virtual Cluster** | **Schema** | **Volume** | **Synonym** | **Function** | **Job** | **Table, Dynamic Table, View, etc.** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **instance_admin** | create workspace&#xA;drop workspace&#xA;read metadata | / | / | / | / | / | / | / |
| **instance_sre** | / | / | / | / | / | / | read metadata | / |
| **workspace_admin** | read metadata | all [with grant option] | all [with grant option] | all [with grant option] | all [with grant option] | all [with grant option] | all [with grant option] | all [with grant option] |
| **workspace_dev** | read metadata | read metadata&#xA;use | all | all | all | create&#xA;read metadata | read metadata | all |
| **workspace_sre** | read metadata | / | / | / | / | / | read metadata | / |

For the business meaning of data permission points, refer to: [Metadata and Permission Points](meta-objects-and-privileges.md)

## Q&A

Question 1: Why can some `workspace_dev` users in the same account create, modify, delete, start, and stop clusters while others cannot?

Answer: The preset role function permission restrictions listed in this document take effect in the new version (Release 2025.03.05). If a user's role configuration was set before this version, permissions follow the old version's logic. If you encounter detailed issues during use, please contact our technical support team for assistance.
