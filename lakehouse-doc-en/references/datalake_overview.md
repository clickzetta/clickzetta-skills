# Data Lake

## Overview

Singdata Lakehouse, as an integrated data platform, can seamlessly connect to cloud object storage (currently supported cloud object storage products include: Alibaba Cloud OSS, Tencent Cloud COS, Google GCS, AWS S3), and utilize its integrated data processing engine combined with industry-leading AI capabilities to efficiently process semi-structured and unstructured data in the data lake. In this process, we adopt a unified permission management method to ensure data security and compliance. Specific capabilities include:

1. **Ability to perceive and acquire external data**: As the amount of data continues to grow, the proportion of semi-structured and unstructured data in the data is increasing, and their importance is becoming more prominent.
2. **Ability to conveniently utilize cutting-edge AI technology**: The multimodal capabilities of deep learning models and large language models (LLM) greatly reduce the threshold for practitioners to analyze semi-structured and unstructured data. Allowing the data platform to conveniently utilize these capabilities expands the scope of data analysis from two-dimensional table data to almost all data (ALL Data), which is an important enhancement in the dimension of analytical capabilities.
3. **Ability to manage and govern data and files uniformly**: Applying the mature, complete, and universal permission system in the data warehouse to data and files (such as AI model files), for example: controlling specific users to use specified model files and processing authorized data. At the same time, it can achieve a global view of data from an organizational perspective.

The following is a detailed introduction to specific product features:

1. [Data Lake Volume Object](datalake_volume.md): By integrating the data platform with unstructured data, it solves the problem of the data platform accessing unstructured data and the fragmentation of AI/BI data. For example, users can easily import unstructured data such as images and text into the data platform through Volume objects for further analysis and processing.
2. [Remote Function](remotefunction-on-acr.md): Provides users with a low-threshold method to call AI models and large language models (LLM) to analyze data. For example, users can easily call pre-trained deep learning models through Remote Function to perform tasks such as image classification and recognition.
3. [Unified Lakehouse Metadata System](datalake_privilege.md): Integrates structured and unstructured data into a unified Catalog-Schema view, solving the problem of unified lakehouse metadata management and permission management, simplifying data organization and access. For example, administrators can assign corresponding data access permissions to employees of different departments through the metadata system to ensure data security and compliance.

^
