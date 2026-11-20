# Singdata Product Service Level Agreement (SLA)

This Service Level Agreement (hereinafter referred to as "SLA") stipulates the service availability level indicators and compensation plans for Lakehouse provided by Singdata to clients.

## 1. Definition

- **Service Cycle:** One service cycle is one calendar month.
- **Total Minutes in Service Cycle:** Calculated as the total number of days in the service cycle multiplied by 24 (hours) multiplied by 60 (minutes).
- **Agreed Service Access Endpoints:** The service access endpoints designated for a Workspace and agreed between Singdata and the customer for accessing the Singdata Lakehouse service, including the JDBC endpoint and the Ingest Service (IGS) interface, as applicable to that Workspace.
- **Successful Access:** Successful access to the agreed service access endpoints of a Workspace using the relevant service's normal access methods, including JDBC and IGS, as applicable.
- **Five-Minute Statistical Period:** Service availability is measured in consecutive, non-overlapping five-minute intervals within a Service Cycle.
- **Service Unavailable:** If, due to reasons attributable to Singdata, all of the customer's continuous attempts to access every Agreed Service Access Endpoint of a designated Workspace fail throughout a Five-Minute Statistical Period, that Workspace is considered unavailable for that five-minute period.
- **Service Unavailable Minutes:** The sum of the minutes corresponding to all Five-Minute Statistical Periods in which the Workspace is determined to be Service Unavailable within a Service Cycle. Each qualifying period contributes five minutes and is counted only once, regardless of the number of affected endpoints or failed access attempts. Periods excluded under Section 2 or Section 4 are not included.
- **Workspace Monthly Consumption:** The service consumption amount actually incurred by the Workspace during the calendar month.
- **Workspace Average Daily Consumption:** The Workspace Monthly Consumption for a Service Cycle divided by the total number of calendar days in that Service Cycle.

## 2. Service Availability

Service availability is calculated using a single Workspace as the statistical unit, based on the definitions in Section 1, in the following manner:

**Service Availability = ((Total Minutes in Service Cycle − Service Unavailable Minutes) / Total Minutes in Service Cycle) × 100%**

**Lakehouse service availability, as defined and calculated above, is not less than 99.9%.** If the Lakehouse service fails to meet the above availability commitment, the customer may obtain compensation in accordance with the provisions of Section 3 of this Agreement.

| Classification | Subitem | Coverage Content |
|---|---|---|
| SLA | Workspace Access Availability | Not less than 99.9%, measured in accordance with the definitions and calculation method in Sections 1 and 2 |
| Service Response | Fault Response | Provide 7×24 hour remote fault response service |

**The following are excluded from the calculation of service unavailable time and are not eligible for compensation:**

(1) Caused by Singdata's prior notice to the customer, and system upgrades and system maintenance carried out during the agreed upgrade window;

(2) Caused by network, device failures, or configuration adjustments outside of any equipment owned by Singdata;

(3) Caused by a hacker attack on the client's application;

(4) Caused by improper customer maintenance or improper confidentiality, resulting in the loss or leakage of data, passwords, etc.;

(5) Caused by the customer's negligence or operations authorized by the customer;

(6) Caused by the customer's failure to follow the usage documentation or usage recommendations of the Singdata product;

(7) Caused by force majeure;

(8) Abnormal or malicious traffic, including excessive request bursts beyond the documented rate limits;

(9) Caused by insufficient or unavailable compute resources under the customer's control, including Virtual Clusters (VCluster) that are undersized, suspended, stopped, or have reached their configured resource limits, and workspace or account quotas that have been exhausted;

(10) Unavailability affecting features, services, or regions designated as Private-Preview, Public-Preview, or otherwise not generally available;

(11) Unavailability affecting free trials, free tiers, or any other services provided to the customer free of charge;

(12) Suspension or termination of the service by Singdata due to the customer's overdue payment or breach of the applicable service agreement.

## 3. Compensation Plan

### 3.1 Compensation Standard

Compensation will be issued in the form of vouchers, which cannot be cashed out, redeemed for cash, or transferred.

Service availability is calculated per Workspace in accordance with Sections 1 and 2, and the compensation amount is calculated as a multiple of the Workspace Average Daily Consumption (as defined in Section 1) according to the table below. Compensation is determined by the single applicable tier based on the Workspace's final service availability for the Service Cycle and is not accumulated separately for each incident. The total compensation for a Workspace in any Service Cycle shall not exceed seven (7) times its Workspace Average Daily Consumption for that Service Cycle.

| Service Availability | Compensation Voucher Amount |
|---|---|
| Less than 99.9% but equal to or greater than 99.0% | 1 × Workspace Average Daily Consumption |
| Less than 99.0%, but equal to or greater than 95.0% | 3 × Workspace Average Daily Consumption |
| Less than 95.0% | 7 × Workspace Average Daily Consumption |

### 3.2 Time Limit for Compensation Application

Customers may submit a compensation claim for a Workspace that failed to meet the service availability commitment after the end of the calendar month in which the failure occurred. Singdata must receive the claim within twenty-one (21) calendar days after the end of that month. Claims received after this deadline will not be accepted. This deadline applies only to compensation claims and does not restrict the reporting of faults or requests for technical support.

## 4. Disclaimer

1. Failures caused by factors beyond the control of Singdata are not counted within the scope of Singdata's SLA;
2. Failures not caused by Singdata's product components are not counted within Singdata's SLA scope;
3. If the data storage is hosted under the customer's own account, data unavailability failures caused by the customer's reasons are not counted within the scope of Singdata's SLA.

## 5. Security Incident Notification

### Definition

"Security Incident" means a breach of security leading to the accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to, Customer Data. A Security Incident shall not include unsuccessful attempts or activities that do not compromise the security of Customer Data, including but not limited to: pings and other broadcast attacks on firewalls or edge servers, port scans, unsuccessful log-on attempts, denial of service attacks, packet sniffing (or other unauthorized access to traffic data that does not result in access beyond headers), or similar incidents.

### Notification Commitment

In accordance with applicable data protection laws, Singdata will notify Customer of a Security Incident affecting that Customer without undue delay after becoming aware of the Security Incident, and take appropriate measures to address the Security Incident, including measures to mitigate any adverse effects resulting from the Security Incident.

### Notification Timeframe

1. **High-Risk Security Incidents:** For security incidents likely to result in a high risk to the rights and freedoms of individuals, Singdata will notify affected Customers within 72 hours of confirming the incident. High-risk incidents include but are not limited to:

   - Breaches involving sensitive personal data (such as financial information, health data, or identity credentials)
   - Incidents likely to result in identity theft, fraud, or significant financial loss
   - Large-scale data breaches (affecting more than 1,000 data subjects)
   - Incidents where encryption keys or security credentials have been compromised

2. **General Security Incidents:** For Security Incidents unlikely to result in a risk to the rights and freedoms of individuals, Singdata will notify affected customers as soon as reasonably practicable based on impact assessment, but no later than 30 calendar days after confirming the incident.

### Notification Content

Security Incident notifications will include:

- A description of the nature of the Security Incident, including the categories and approximate number of affected data subjects and data records
- The likely consequences of the Security Incident
- The measures taken or proposed to be taken by Singdata to address the Security Incident and mitigate its possible adverse effects

### Delayed Notification

Notification timing may be delayed under the following circumstances:

- Law enforcement requests delay to accommodate investigation needs
- Additional time is required to determine the scope and impact of the incident
- Time is needed to restore reasonable integrity of the system

In case of delay, Singdata will provide reasons for the delay in the notification and provide information in phases as circumstances permit.

## 6. Other

Singdata reserves the right to modify this SLA clause. If there are any modifications to this SLA clause, Singdata will notify you 30 days in advance by means of website announcement or email. If you do not agree to the modifications made by Singdata to the SLA, you have the right to stop using the Singdata Lakehouse service. If you continue to use the Singdata Lakehouse service, it will be deemed that you have accepted the modified SLA.
