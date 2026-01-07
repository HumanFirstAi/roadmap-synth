# Next Gen CPQ Functionality List

A comprehensive requirements document for Zuora's Next Generation CPQ (Configure-Price-Quote) system.

---

## Table of Contents

1. [Catalog End User](#1-catalog-end-user)
2. [Catalog Admin](#2-catalog-admin)
3. [Product Configurator End User](#3-product-configurator-end-user)
4. [Solution Configurator End User](#4-solution-configurator-end-user)
5. [Configurator Admin](#5-configurator-admin)
6. [Price Guidance](#6-price-guidance)
7. [Quote Experience](#7-quote-experience)
8. [Quote Metrics](#8-quote-metrics)
9. [Deal Engine](#9-deal-engine)
10. [Deal Room](#10-deal-room)
11. [Deal Desk](#11-deal-desk)
12. [Approval Workflow](#12-approval-workflow)
13. [AI Framework](#13-ai-framework)
14. [Quote Rules & Admin](#14-quote-rules--admin)
15. [Self Service](#15-self-service)
16. [Indirect Channel](#16-indirect-channel)
17. [User Management](#17-user-management)
18. [Priority and Ranking](#18-priority-and-ranking)

---

## Priority Legend

| Priority | Description |
|----------|-------------|
| 1 | Must Have |
| 2 | Very Important |
| 3 | Important |
| 4 | Optional |
| 5 | Nice to Have |

---

## 1. Catalog End User

*Sales reps can find, compare, and select products and price plans. Self-service can have the same UI and experience, although their experience will be in their own eCommerce Portal.*

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 10.10 | Sales Rep shall be able to view Product Detail Page in Z-Commerce Widgets | 2 | Yes | Users can view details of the product, like product descriptions, features of the product, price plans, images, and attached documents. |
| 10.20 | Sales Rep shall be able to view similar, complementary, and recommended Products in Z-Commerce Widgets | 4 | Yes | AI generates a list of similar, recommended alternatives, and complementary products to be shown on the product detail page (similar to the Amazon catalog experience "Customers also liked.") |
| 10.30 | Sales Rep shall be able to initiate and view a Product Comparison in Z-Commerce Widgets | 4 | No | Users can compare products, feature by feature, and their price plans |
| 10.40 | Sales Rep shall be able to execute a Google-like Product Search in Z-Commerce Widgets | 1 | Yes | Users can utilize a Google-like search (e.g., Elastic Search) |
| 10.50 | Sales Rep shall be able to set product/plan Features/Entitlements for Parametric Filtering in Z-Commerce Widgets | 3 | Yes | Users can filter products by features or attributes. Filters indicate how many products are still left if a filter value is selected |
| 10.60 | Sales Rep shall be able to set predefined Guided Selling Filters in Z-Commerce Widgets | 4 | No | Users can utilize pre-defined filter value combinations, the same functionality as today |
| 10.70 | System shall be able to Enforce Product Availability according to Z-Commerce Catalog | 3 | Yes | Show only products that can be sold. Check product effectivity and status. This includes functionality that checks product availability rules and shows only products that are available for certain types of customers or regions, etc. |
| 10.80 | Sales Rep shall be able to add product plans into a temporary cart in Customer Commerce System | 2 | Yes | Users can add a product to a temporary cart so they can see what will be added to the quote when they select multiple products and plans at once. Some basic functions to manage the temporary cart are required (delete action). |
| 10.90 | Sales Rep shall be able to configure a product-plan combination in Customer Commerce System | 3 | Yes | If a product is configurable, the user must configure the product and the selected plan if they want to place an order. If they request a quote, the configuration does not have to be completed; it should be optional, or the configuration can have errors. |
| 10.100 | Sales Rep shall be able to add product and plan to the quote in Customer Commerce System | 3 | Yes | After the product configuration, the user can add the configured item to the quote. |

---

## 2. Catalog Admin

*The assumption is that this area is handled by the Commerce Catalog.*

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 20.10 | Sales Ops Admin shall be able to CRUD Product in Z-Commerce Catalog | 1 | Yes | Typical ability to create and maintain products of various types (e.g., Regular, Configurable, Preconfigured for modeling of Hard and Dynamic bundles) |
| 20.20 | Sales Ops Admin shall be able to CRUD Product Category Hierarchy in Z-Commerce Catalog | 2 | Yes | Admin creates a product category hierarchy; a sub-category can only belong to one parent category. |
| 20.30 | Sales Ops Admin shall be able to assign Products to Categories in Z-Commerce Catalog | 2 | Yes | Admin assigns a product to one or more product categories |
| 20.40 | Sales Ops Admin shall be able to define Attributes, Features, and Entitlements in Z-Commerce Catalog | 1 | Yes | Admin defines attributes (format, mandatory/options, single/multi-value, etc.), and if enumerated, it allows a list of attribute values |
| 20.50 | Sales Ops Admin shall be able to assign Attributes, Features, and Entitlements to Categories, Product, and Plans in Z-Commerce Catalog | 4 | No | Admin assigns attributes, features, and entitlements to the appropriate object (category, product, plan, etc). The system works according to the catalog design |
| 20.60 | Sales Ops Admin shall be able to assign Attribute and Attribute Values to Categories with inheritance in Z-Commerce Catalog | 4 | No | Admins can assign an attribute value for an attribute that is assigned to a product category. The Attribute value is inherited from the parent category to all sub-categories |
| 20.70 | Sales Ops Admin shall be able to configure for a Product a Rate Plan in Z-Commerce Catalog | 1 | Yes | Admins can assign an attribute value to a product. If an attribute value is inherited from the category to the product, then admins cannot change that value (enforced value) |

---

## 3. Product Configurator End User

*Allows to configure a price plan, the components of a bundle, or BOM.*

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 30.10 | Sales Rep shall be able to go through a Question/Answer selection in Z-CPQ system | 3 | Yes | Users select an answer to a question. Behind the scene, the system sets facts (=attributes values) |
| 30.20 | Sales Rep shall be able to go through a Product selection via Product Category in Z-CPQ system | 2 | Yes | Users select a product from a product category. The system adds the product as a component to a configurable product. |
| 30.30 | Sales Rep shall be able to go through a Product selection as discrete items in Z-CPQ system | 2 | Yes | Users select a product from a list of discrete products. The system adds the product as a component to a configurable product. |
| 30.40 | Sales Rep shall be able to go through an Attribute Value selection in Z-CPQ system | 1 | Yes | Users select an attribute value from an attribute. |
| 30.50 | Sales Rep shall be able to enter Input values into fields in Z-CPQ system | 2 | Yes | Users can enter numeric, integer, or alphanumeric values into fields. Values are captured as attribute values |
| 30.60 | Sales Rep shall be able to navigation to selections in Z-CPQ system | 3 | Yes | Questions, products, and attributes are organized in sections on the config page, and a panel allows users to navigate to get to sections. |
| 30.70 | System shall be able to validate Configuration in Z-CPQ system | 1 | Yes | The system runs the rules to validate the user selections and derive facts from user selections and inputs. |
| 30.80 | System shall be able to show Config Messages in Z-CPQ system | 1 | Yes | Users can see errors and warnings and suggest messages triggered by config rules |
| 30.90 | System shall be able to show Config result in Z-CPQ system | 3 | Yes | UI displays a mini cart that shows the configuration result. Display price plan as configured and components as added by configuration. For Zuora, the configurator output should also include what charge item is included, the quantity of charge item, features and attributes of components and configurable products, and entitlements as configured. |
| 30.100 | System shall be able to select mandatory attributes, answers, products in Z-CPQ system | 2 | Yes | The system auto-selects for mandatory questions, product selections, and attributes the best fitting answers, products, and attribute values. |
| 30.110 | System shall be able to provide prompt for user to describe requirements in Z-CPQ system | 2 | Yes | Sales reps can enter in text what they heard from the customer, such as 'need a Windows server with the latest designer software'; the system then selects the software and configures enough memory to run the software. |
| 30.120 | System shall be able to calculate Config product prices from component prices in Z-CPQ system | 4 | Yes | Additional logic, rules, and UI are needed for the price item transformation. |
| 30.130 | System shall have a set of public configurator APIs in Z-CPQ system | 4 | Yes | A set of public configurator APIs is available to configure a product, validate a configuration, and persist a configuration of a product and plan. This allows Zuora customers to expose the product/plan configurator to other systems. |

---

## 4. Solution Configurator End User

*Allows to combine freely products in a quote (solution), and provides access to individual product configurations, ensures all products and their configurations are compatible.*

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 40.10 | Sales Rep shall be able to indicate that a new solution configuration will be started in Z-CPQ system | 2 | Yes | Sales reps need the ability to explicitly initiate a solution configuration. This is in contrast to a product configuration where sales reps get into configuration experience after selecting a configurable product. |
| 40.20 | Sales Rep shall be able to select from a set of pre-defined, saved (pre)configured solutions in Z-CPQ system | 4 | Yes | Sales reps have an easier time starting a solution configuration if they can select from a list of pre-defined solutions to use as starting points |
| 40.30 | Sales Rep shall be able to select products via catalog experience in Z-CPQ system | 2 | Yes | After a sales rep indicates that they want to start a solution configuration, they then select products from the catalog. |
| 40.40 | Sales Rep shall be able to offer guided selling to select products for a solution in Z-CPQ system | 4 | Yes | The system can offer a guided selling experience like a questionnaire, recommend products, and pre-filtered products in the catalog to help the user select products that are valuable to add to the solution |
| 40.50 | Sales Rep shall be able to configure individual products of solution in Z-CPQ system | 2 | Yes | When users select configurable products from the catalog, they will be prompted to check the product configuration. |
| 40.60 | Sales Rep shall be able to ensure solution is complete and consistent in Z-CPQ system | 2 | Yes | The system indicates for a product of a solution that there are issues with its rules. Errors can occur due to many actions, e.g., if other incompatible products are being added to the same solution, etc |
| 40.70 | Sales Rep shall be able to calculate price items of a solution in Z-CPQ system | 3 | Yes | The system calculates the QRPCs of a solution based on the content of the quote. This is needed to calculate outcome-based prices; see the hospital example |
| 40.80 | Sales Rep shall be able to copy/delete Solution from quote in Z-CPQ system | 2 | Yes | Sales reps need the ability to CRUD solutions in quote |

---

## 5. Configurator Admin

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 50.10 | Sales Ops Admin shall be able to create Questions Answers in Z-CPQ system | 3 | Yes | Create questions and answers globally and reuse them in multiple models |
| 50.20 | Sales Ops Admin shall be able to create Model Structure in Z-CPQ system | 1 | Yes | Admin puts questions, answers, product categories, and attributes together |
| 50.30 | Sales Ops Admin shall be able to define UI appearance in Z-CPQ system | 1 | Yes | Admin can define how a question, attribute, or product should be displayed (list, check box, hidden, mandatory input, etc.) |
| 50.40 | Sales Ops Admin shall be able to define sequence of Q/A, attributes, products in Z-CPQ system | 2 | Yes | Admin can build sections of Q/A, attributes, products, and in what sequence they are displayed on the UI |
| 50.50 | Sales Ops Admin shall be able to test Model in Z-CPQ system | 3 | Yes | Users can test the config model. |
| 50.60 | Sales Ops Admin shall be able to analyze test log in Z-CPQ system | 4 | Yes | Users can review a test log that shows what rule fired, which ones did not, and the facts that are evaluated and produced by the rules. |
| 50.70 | Sales Ops Admin shall be able to publish Model in Z-CPQ system | 1 | Yes | When the model is tested, the user can publish the model, and later, the model changes to staging or production. |
| 50.80 | Sales Ops Admin shall be able to create Rules of various types in Z-CPQ system | 1 | Yes | Admin can create rules in an easy-to-use UI (we can copy concepts that Commerce Catalog already developed for pricing rules) |
| 50.90 | Sales Ops Admin shall be able to create Preconfiguration in Z-CPQ system | 4 | Yes | The product admin can create one specific configuration for a product. Preconfigured products can then be sold on the quote with that specific configuration. |

---

## 6. Price Guidance

*The sales rep knows little about the account and has spoken only a few times with the prospect. Based on the preliminary information he got, he was asked to provide some price guidance to the prospective buyer.*

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 60.10 | Sales Rep shall be able to create a Price Guidance in Z-CPQ system | 1 | Yes | The sales rep adds prospect/customer information to the system. He also added a description of what he understood the customer needed. The system proposes a high-level sketch of quote content. The price guidance is not on the product level but explains on a higher level (product category) what price range the customer can expect the final quote to fall into. |
| 60.20 | Sales Rep shall be able to generate Presales Price Guidance in Z-CPQ system | 1 | Yes | A sales rep can generate a high-level slide from the price guidance the system generated. The sales rep can download and use it in his presentation, email, and deal room for this prospect. |
| 60.30 | Sales Rep shall be able to customer Research in Z-CPQ system | 3 | Yes | Sales reps can, for existing customers, understand important metrics that will help them to finalize an amendment and renewal with up/down/cross-sell. Metrics that are shown in the quote are also relevant to this activity. |
| 60.40 | Sales Rep shall be able to convert Price Guidance in Z-CPQ system | 1 | Yes | Sales reps can decide to seamlessly convert the price guidance into a quote. He can select various quotes as starting points. |

---

## 7. Quote Experience

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 70.10 | Sales Rep shall be able to interact with Quote Portal Widgets in Z-CPQ system | 1 | Yes | Provide a handful of quote-related widgets that can be shown on a quote management portal. The same widgets (if technology allows) can be used in the CRM systems. E.g. i-Frame in SFDC under 'Zuora Quote' tab. |
| 70.20 | Sales Rep shall be able to have access to a Quote Portal in Z-CPQ system | 4 | Yes | Usually quoting will be performed from an opportunity in a CRM system, but it would be good to have a quote portal page where we also expose the portal widgets in the Zuora system. |
| 70.30 | Sales Rep shall be able to start a quote from an opportunity (SFDC CRMs) in Z-CPQ system | 1 | Yes | Initiate a quote from an SFDC opportunity. |
| 70.40 | Sales Rep shall be able to start a quote from an opportunity (various CRMs) in Z-CPQ system | 3 | Yes | Initiate quote from MS Dynamics, Deal Hub CRM. |
| 70.50 | Sales Rep shall be able to create a quote for a new or existing account in Z-CPQ system | 1 | Yes | Users need a page where they can select an account (sold-to and bill-to), create a new billing account, and select a subscription, similar to the current 'Accounts and Subscription' page. |
| 70.60 | Sales Rep shall be able to create a quote that combines a new subscription sales with an amendment or a renewal in Z-CPQ system | 2 | Yes | The current CPQ does not allow sales reps to combine a net new subscription sale with a renewal or an amendment. Customers might have multiple subscriptions with our customers, and hence sales reps might combine a new sale with a renewal of an existing subscription. |
| 70.70 | Sales Rep shall be able to create a quote from a prompt input in Z-CPQ system | 2 | Yes | The system collects info from various sources (email, Slack, recorded meetings) and generates the best quote. |
| 70.80 | Sales Rep shall be able to suggest the best-fitting quote templates to start a quote in Z-CPQ system | 2 | Yes | The system suggests the best-fitting quote templates based on account context. |
| 70.90 | Sales Rep shall be able to create and edit multiple subscriptions for a quote in Z-CPQ system | 1 | Yes | Users need a flow to create a subscription or edit the field values of an existing one. The quote shall allow the addition of more than one subscription. Subscription can be replaced with the term agreement. |
| 70.100 | Sales Rep shall be able to add and assign products to subscriptions in Z-CPQ system | 1 | Yes | Provide a 'Quick Add' experience and a catalog browse/search/filter experience to add products and price plans to a subscription. |
| 70.110 | Sales Rep shall be able to amend a subscription in Z-CPQ system | 1 | Yes | Users can make amendments to existing subscriptions. There is logic around dates and pricing that applies during an amendment of a subscription. |
| 70.120 | Sales Rep shall be able to renew a subscription in Z-CPQ system | 1 | Yes | Users can make renewals to existing subscriptions. There is logic around dates and pricing that applies during the renewal of a subscription. |
| 70.130 | Sales Rep shall be able to display price and components of hard bundles in Z-CPQ system | 3 | Yes | Users can add a hard bundle and price plans. The quote line UI needs to show the components of a hard bundle. The UI indicates that these components are included as part of the bundle. |
| 70.140 | Sales Rep shall be able to add products and system detects a soft bundle in Z-CPQ system | 2 | Yes | As user adds products to the quote the quote UI informs the user that there are other products if also added to the quote will form a bundle and might apply bundle discounts. |
| 70.150 | Sales Rep shall be able to add a configured product (dynamic bundle) to a quote in Z-CPQ system | 4 | Yes | Users can configure products and price plans. After the configuration, they can add the configured product and its components and populate information about the QPRCs (qty, pricing relevant attributes), features, and entitlements to the quote. |
| 70.160 | Sales Rep shall be able to create and edit a ramp for a subscription in Z-CPQ system | 1 | Yes | Ramps are used to increase the value of the subscription (add product, add qty, change discount) over defined intervals. The user can decide if a ramp should be used. Ramp intervals can be defined by user. |
| 70.170 | Sales Rep shall be able to manage one-time product Lines in Z-CPQ system | 1 | Yes | Provide a 'Quick Add' experience and a catalog browse/search/filter experience to add products to a quote. Provide typical line operations to edit, copy, and delete. Change qty and apply discounts to a product. |
| 70.180 | Sales Rep shall be able to display QPRC prices for Charge Item Totals in Z-CPQ system | 1 | Yes | Display the price waterfall portion for each charge item (QPRCs) |
| 70.190 | Sales Rep shall be able to display interval prices for (Ramp) Interval Totals in Z-CPQ system | 1 | Yes | Display the price waterfall portion for each ramp interval |
| 70.200 | Sales Rep shall be able to display Product prices for Product Totals in Z-CPQ system | 3 | Yes | Display the price waterfall portion for each product/plan |
| 70.210 | Sales Rep shall be able to display Subscription prices for Subscription Totals in Z-CPQ system | 2 | Yes | Display the price waterfall portion for each subscription |
| 70.220 | Sales Rep shall be able to display quote prices for Quote Totals in Z-CPQ system | 1 | Yes | Display the price waterfall portion for the quote |
| 70.230 | Sales Rep shall be able to change the plan on a Quote Line in Z-CPQ system | 4 | Yes | Users can change the plan of a product |
| 70.240 | Sales Rep shall be able to provide a deal score auto-improvement function in Z-CPQ system | 4 | Yes | The user has a function available that allows him to improve the deal score with the press of one button; the system makes a new deal version with a higher deal score. |
| 70.250 | Sales Rep shall be able to provide an 'avoid approvals' function in Z-CPQ system | 3 | Yes | The system provides a one-button help to fix the quote so it does not require approvals. |
| 70.260 | Sales Rep shall be able to designate a product in the quote to be an alternate product in Z-CPQ system | 3 | Yes | Users can designate a product and rate plan in the quote as an alternative product, which means the product is not included in the deal but suggested. The product will be printed as suggested in the quote proposal. |
| 70.270 | Sales Rep shall be able to offer 'Also liked Products' for display and an add to the quote function in Z-CPQ system | 2 | Yes | Users can add products that are recommended by the system as line items to the subscription. |
| 70.280 | Sales Rep shall be able to provide flexible grouping of quote lines in Z-CPQ system | 2 | Yes | It helps to navigate and understand the content of a large quote (lots of quote lines) if a sales rep can select grouping criteria, e.g., Install location, billing account, etc, to group the quote lines. |
| 70.290 | Sales Rep shall be able to provide the ability to define an ad-hoc grouping criterion for quote lines in Z-CPQ system | 4 | Yes | Sales reps get requests from customers to group quote lines based on criteria that are not predefined in the system. |
| 70.300 | Sales Rep shall be able to offer a Goal Seek function in Z-CPQ system | 2 | Yes | Users can apply a discount to price items to all or selected line items via a single action. |
| 70.310 | Sales Rep shall be able to offer Discount Guidance function in Z-CPQ system | 3 | Yes | Discount Guidance shows the recommended or the enforced discount band for a price item. |
| 70.320 | Sales Rep shall be able to enter in tabular form COGS (Cost of Goods Sold) in Z-CPQ system | 4 | Yes | Provide a simple tabular UI where sales reps view pre-determined COGS and can also enter more COGS. |
| 70.330 | Sales Rep shall be able to display a Margin Indicator per quote line in Z-CPQ system | 3 | Yes | Display a margin indicator for a product (Traffic Light: red - margin is negative, yellow - margin is below a certain threshold, green - margin is within the expected range) |
| 70.340 | Sales Rep shall be able to flexibly group, search, and filter quote lines in Z-CPQ system | 2 | Yes | Users can group line items by Subscriptions (default), products, product types, price plans, price item types, etc. |
| 70.350 | Sales Rep shall be able to display Mediation info in Z-CPQ system | 3 | Yes | Display mediation info for usage-based price items. This helps sales reps in up-sell scenarios to recommend increased qty or other products if usage is high. |
| 70.360 | Sales Rep shall be able to validate ramp, product, subscription, and quote rules in Z-CPQ system | 1 | Yes | The system shall apply rules created by admins to check for consistency and compliance with business rules of ramps, products, subscriptions, and quote levels. |
| 70.370 | Sales Rep shall be able to show Error, Warnings, and Suggest Messages, with easy-to-understand explanations in Z-CPQ system | 1 | Yes | Display and provide access to errors and warnings and suggest messages for products, subscriptions, and quotes. |
| 70.380 | Sales Rep shall be able to generate a PDF Proposal in Z-CPQ system | 1 | Yes | User generate a PDF proposal. One example template that can handle all the various product types is part of the system. |
| 70.390 | Sales Rep shall be able to publish a quote to the Deal Room in Z-CPQ system | 1 | Yes | In addition to generating a PDF proposal, the sales rep can send an email to the prospect with a link to the Deal Room. |
| 70.400 | System shall manage quotes with typical functions like copy and delete in Z-CPQ system | 1 | Yes | Users can clone and delete quotes. |
| 70.410 | System shall sync necessary data objects from Z-CPQ to CRM in Z-CPQ system | 1 | Yes | Sync product 2 and quotes from Zuora to SFDC |
| 70.420 | System shall sync z-CPQ Quote to CRM Opportunity in Z-CPQ system | 1 | Yes | The system syncs quote products from the quote to the opportunity (SFDC opportunity only) |
| 70.430 | Sales Rep shall be able to sync product lines from CRM opportunity to quote in Z-CPQ system | 4 | No | The system syncs opportunity products from the opportunity to the quote (SFDC opportunity only). |
| 70.440 | Sales Rep shall be able to manage Quote Templates in Z-CPQ system | 3 | Yes | Users can save a quote as a sample quote. Sample quotes help to start a new quote quickly. |
| 70.450 | Sales Rep shall be able to access an audit log in Z-CPQ system | 4 | Yes | Sales reps and admins would like to see who made changes to a quote and what changes have been made over time. |
| 70.460 | Sales Rep shall be able to request interactive in app help in Z-CPQ system | 3 | Yes | A contextual help function can be used when users are uncertain or don't know how to accomplish a task during quoting. |
| 70.470 | Sales Rep shall be able to save and retrieve a quote version in Z-CPQ system | 3 | Yes | A sales rep can decide to save a quote as a version. |
| 70.480 | Sales Rep shall be able to save an alternative quote version in Z-CPQ system | 1 | Yes | During the development of a deal, many different versions and alternative quotes might be necessary to show alternatives to the prospect. |
| 70.490 | System shall auto-save changes a sales rep is making on a quote in Z-CPQ system | 1 | Yes | All UI and, most importantly, the Quote Line Page shall have auto-save. |

---

## 8. Quote Metrics

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 80.10 | System shall show in Z-CPQ TCB, TCV, MRR, ARR from Z-Metrics aaS | 1 | Yes | Sales reps need basic metric data. |
| 80.20 | System shall show in Z-CPQ a derived or calculated Deal Score from Z-Metrics aaS | 3 | Yes | The deal score is dependent on many factors, e.g., vertical, region, size of the deal, customer size, deal size, margins, products sold, etc. |
| 80.30 | System shall show in Z-CPQ a high-risk and a low-risk indicator from Z-Metrics aaS | 4 | Yes | This indicator only focuses on the potential risk (to deliver on time, to run into legal issues, to collect payments from customers, etc.) for the company. |
| 80.40 | System shall show a margin Indicator on quote lines from Z-Metrics aaS | 4 | Yes | Provide a traffic light margin indicator for sales reps to show if a line item is cutting into the margin. |
| 80.50 | System shall show an estimated Approval Time from Z-Metrics aaS | 3 | Yes | The sales rep gives discounts that need approval; how long does it take to get the quote approved? |
| 80.60 | Sales Rep shall be able to allow quote metrics level comparison to other quote alternatives and versions in Z-CPQ system | 3 | Yes | The system compares the quote against similar quotes and provides information on the likelihood of winning this deal. |
| 80.70 | System shall display Fund info from Z-Billing aaS | 3 | Yes | Sales Reps quoting amendment or renewal deals can see prepaid drawdown charges because it exposes what the customer has consumed from what they prepaid for at the beginning of the Subscription. |
| 80.80 | System shall display the contract value of the billing account across all subscriptions they own from Z-Billing aaS | 3 | Yes | This would be beneficial when co-terming or "merging" subscriptions becomes possible. |
| 80.90 | System shall display Billing Account change information from Z-Billing aaS | 3 | Yes | A rep can see that a billing account used to have a payment term of net 30 and now has a payment term of net 45. |
| 80.100 | System shall show account payment info from Z-AR aaS | 3 | Yes | Insights into customer payment history. Did the customer pay their invoices on time, or are they getting behind on invoices? |
| 80.110 | System shall show sales reps an approximate calculated sales compensation from Z-CPQ system | 4 | Yes | Sales reps would like to understand how much money they earn when they sell a deal. |
| 80.120 | System shall identify and show churn risk of this customer from Z-Metrics aaS | 2 | Yes | How many support tickets, how many calls to customer service, ratings of the product, etc.? Consumption is declining and not meeting the ramp criteria, so give more favorable discounts in case the churn risk is high. |

---

## 9. Deal Engine

*A Deal Engine allows sales reps to simulate different financial outcomes in regard to a quote and its content.*

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 90.10 | Sales Rep shall be able to create a deal version in Z-CPQ system | 2 | Yes | Sales reps can optionally decide to create a deal version. A deal version is not an alternate quote; a deal version is a set of parameters that get applied to the quote lines to alter quote metrics. |
| 90.20 | Sales Rep shall be able to specify deal key agreement parameters in Z-CPQ system | 2 | Yes | Sales reps can alter important parameters in a deal version, such as agreement terms and whether the deal is ramped or not ramped. |
| 90.30 | Sales Rep shall be able to specify deal value targets in Z-CPQ system | 2 | Yes | Sales rep defines specific quote values like Interval Total (if ramped), Agreement (Subscription) Total, and Quote Total. |
| 90.40 | Sales Rep shall be able to manipulate agreement key parameters in Z-CPQ system | 2 | Yes | Sales reps can further change the values of the quote, like quantities of certain PRPCs, to further manipulate the quote prices. |
| 90.50 | Sales Rep shall be able to lock specific quote lines from being changed by the deal engine logic in Z-CPQ system | 3 | Yes | Sales reps can lock a quote line (QRPC) if they want a deal version, not change its quantity or discounts. |
| 90.60 | Sales Rep shall be able to view key metrics of the deal version in Z-CPQ system | 3 | Yes | The system calculates the quote metrics value based on the quote version parameters, and the sales rep can view them. |
| 90.70 | Sales Rep shall be able to compare key metrics of two or more deal versions in Z-CPQ system | 4 | Yes | The sales rep needs to understand how one quote version compares to another quote version. For that purpose, the system allows the sales rep to see the quote metrics side-by-side. |
| 90.80 | Sales Rep shall be able to apply deal version to a quote in Z-CPQ system | 2 | Yes | Sales reps must be able to apply a quote version to the quote. This means that the quote lines will be changed according to the quote version. Discretionary discounts and qty are updated. |
| 90.90 | Sales Rep shall be able to manage deal versions in Z-CPQ system | 3 | Yes | Sales reps need the ability to name a quote version (e.g., Good, Better, Best, All-in, Minimal, Long term, Short Term) |

---

## 10. Deal Room

*A deal room, also known as a virtual sales room or data room, is a secure online space designed for collaboration and information-sharing during business transactions. It is commonly used in B2B sales.*

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 100.10 | Sales Rep shall be able to publish a quote proposal to the Deal Room in Z-CPQ system | 2 | Yes | Sales reps can publish a quote as a proposal in a Deal Room. |
| 100.20 | Sales Rep shall be able to define key display characteristics of the quote proposal, and how it is displayed in the deal room in Z-CPQ system | 3 | Yes | Sales reps can decide what values and quote lines they want to show to the customer. For example, they might decide not to show list prices and discounts but just effective Prices. |
| 100.30 | System shall send notification via email with a link to the Deal Room to the Account sold-to Contact in Z-CPQ system | 2 | Yes | The sold-to contact will receive an email with a link to the secure Deal Room. |
| 100.40 | Customer Buyer shall be able to allow account sold-to contact to access the Deal Room in Z-CPQ system | 2 | Yes | Allow the contact to view the Deal Room content. Not every sold-to contact is allowed to sign the agreement. |
| 100.50 | System shall display the quote proposal in deal room in Z-CPQ system | 2 | Yes | The system displays the proposal as generated by the sales rep from the quote to the customer contact. |
| 100.60 | Customer Buyer shall be able to compare various quote alternatives in Z-CPQ system | 2 | Yes | Allow prospect user to compare two (or more) quote versions to understand how they differ in their key metrics. |
| 100.70 | System shall display related marketing materials about products and company in Z-CPQ system | 4 | Yes | The sales rep might decide to add marketing-related content (Product Datasheets, Whitepapers, etc) to be available for the contact to view in the Deal Room. |
| 100.80 | Customer Buyer procurement shall be able to allow contact to comment on a quote proposal in Z-CPQ system | 2 | Yes | Contact can place comments on the quote lines of the proposal |
| 100.90 | Customer Buyer shall be able to allow contact to deselect products from quote proposal in Z-CPQ system | 3 | Yes | Contact can remove products from the quote, marking them as not applicable. They can select a reason why they don't want the product. |
| 100.100 | Customer Buyer shall be able to allow contact to add products (recommended) to a quote proposal in Z-CPQ system | 3 | Yes | Contact can add products. One way how to add is by making a recommended product active for the quote. |
| 100.110 | Customer Buyer manager shall be able to allow contact to invite coworkers to view quote proposal in Z-CPQ system | 3 | Yes | Contact might have others in his organization that need to see the proposal (e.g., corporate lawyer, engineers, purchase org) to decide if the proposal is what they need |
| 100.120 | Customer Buyer shall be able to allow contact to reject a quote proposal in Z-CPQ system | 2 | Yes | If a contact rejects a proposal, they also need to indicate why they reject it, needs further clarification, the price is not met, the product does not fit, lost interest, etc |
| 100.130 | Customer Buyer procurement shall be able to allow contact to view T&Cs of the quote proposal in Z-CPQ system | 3 | Yes | Contact can review the T&Cs that are associated with the quote |
| 100.140 | Customer Buyer procurement shall be able to Allow contact to edit (redline) T&Cs of the quote proposal in Z-CPQ system | 4 | Yes | Contact can make edits to the T&Cs, initiating a red-line process. A paragraph representing a T&C can be changed |
| 100.150 | Customer Buyer manager shall be able to allow contact to eSign the quote proposal in Z-CPQ system | 3 | Yes | Enable integration with common eSignature solutions like DocuSign and Certify. Not every buyer person might be allowed to sign the final contract. |
| 100.160 | Customer Buyer shall be able to allow contact to place an order in Z-CPQ system | 3 | Yes | The order shall be placed into Z-Order Management. The user gets confirmation that the order has been placed. The system sends a confirmation email with an order acknowledgment form. |

---

## 11. Deal Desk

*Quotes with low deals or high discounts will be flagged by regular workflow rules that require them to be reviewed by a deal desk person. The system assigns quotes to the appropriate deal desk group of people.*

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 110.10 | System shall provide task list for rule-based flagged quotes | 2 | Yes | Users can easily create another alternate quote from an existing quote. They can make changes to the quote and then compare key metrics data. |
| 110.20 | System shall provide quote exception reports | 2 | Yes | Provide a flexible way to generate a deal score (on the quote level). MVP will allow customers to define their own deal score formula in an extension point |
| 110.30 | System shall create and compare quote versions | 2 | Yes | Users can write notes on the line item level. If possible, users can mention them, and the system sends an alert email to the mentioned user. |
| 110.40 | System shall view Deal Score | 2 | Yes | Users can request approval and review from another user who is not part of the approval workflow. |
| 110.50 | System shall capture internal notes | 3 | Yes | The user approves or rejects a quote after review. This is a typical workflow action. |
| 110.60 | System shall request ad-hoc approval | 4 | Yes | Users can request approval and review from another user who is not part of the approval workflow |
| 110.70 | System shall accept and reject quote | 2 | Yes | User approves or rejects a quote after review. This is a typical workflow action. A rejection will send the quote back to the sales rep, an approval will route the quote to the next approver. |
| 110.80 | System shall override certain quote rules | 3 | Yes | There are certain business policies that are enforced by quote rules. A deal desk person shall be able to override those rules and make changes to a quote. |

---

## 12. Approval Workflow

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 120.10 | Sales Rep shall be able to request a Quote Approval (only sequential tasks) in Z-Workflow | 1 | Yes | Enable a sequential approval flow that requests approvals from users one at a time, determining approval levels based on quote attributes. |
| 120.11 | Sales Rep shall be able to determine user or user group who needs to approve an approval task in Z-Workflow | 3 | Yes | Supports administrators to use relationships e.g. quotes that are created by a sales rep who belongs to the west coast sales team shall be approved by the sales manager who leads the west coast sales team. |
| 120.20 | Sales Rep shall be able to request a Quote Approval (with parallel tasks) in Z-Workflow | 3 | Yes | Enable a parallel approval flow that requests approvals from multiple users at the same time. |
| 120.30 | System shall initiate an approval escalation in Z-Workflow | 2 | Yes | Escalate approval requests in case no approval decision is obtained within a given time frame. |
| 120.40 | System shall apply Approval Memory in Z-Workflow | 3 | Yes | Do not re-request approval from approvers who already approved a quote if the quote has no 'relevant' changes since their last approval. |
| 120.50 | Sales Rep shall be able to initiate an Ad-hoc Approval in Z-Workflow | 3 | Yes | The user adds another user as an approver or reviewer. |
| 120.60 | System shall estimate approval time in Z-Workflow | 4 | Yes | When creating a quote, sales reps should know if their quote takes a short or long time to get approved based on similar quotes. |
| 120.70 | System shall send email notifications with tasks for users in Z-Workflow | 2 | Yes | The user receives an email with a task. These emails are needed to ensure users are following up on their workflow items. |
| 120.80 | System shall allow approval or rejections via email reply in Z-Workflow | 3 | Yes | A user wants the convenience to just reply to an email with some keywords like 'Approved' or 'Rejected' to accomplish a workflow task. |
| 120.90 | System shall display progress of approval in quote in Z-Workflow | 3 | Yes | Visual feedback is needed to show the owner of the quote where the approval workflow is currently. |
| 120.100 | System shall enable users to approve specific quote lines via workflow in Z-Workflow | 3 | No | The Approval Workflow investigates quote line items and flags items that require approval. The system assigns an approval task and an approver to the line. |

---

## 13. AI Framework

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 130.10 | System shall provide an AI Framework in Z-Metrics aaS | 3 | Yes | Provide tools that allow Zuora customers to train LLM and prediction models. |
| 130.20 | System shall recommended Products in Z-Metrics aaS | 3 | Yes | The system does a proximity search to recommend other similar products based on past quotes and orders. |
| 130.30 | System shall discount Guidance in Z-Metrics aaS | 3 | Yes | The system recommends a manual discount that is within the discount guidance and ensures a high probability of winning the deal. |
| 130.40 | System shall quote creation with AI prompt in Z-Metrics aaS | 3 | Yes | The entire quote with lines is created by the sentence, 'Create me a quote that has 20 ATMs that are suitable for moist conditions and apply a 10% discount.' |
| 130.50 | System shall adjust stored AI prompts in Z-Metrics aaS | 3 | Yes | This might be needed if the results with the applied prompt are not satisfying. This way, the customer admin can optimize the experience for the customer sales rep. |
| 130.60 | System shall training, learning, or fine-tune AI models in Z-Metrics aaS | 3 | Yes | This might be needed to train the model to improve the results and to make the model specific to the customer. |

---

## 14. Quote Rules & Admin

*Quote Rules are used to validate quote content based on specific customer needs without building custom extension logic into the app.*

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 140.10 | System shall define Quote Level Rules in Z-Metrics aaS | 1 | Yes | Rules are defined by an admin to validate quote-level fields. Rules can produce errors and warnings and suggest messages for users to act on. |
| 140.20 | System shall define Subscription Level Rules in Z-Metrics aaS | 1 | Yes | Rules are defined by an admin to validate subscription-level fields. Rules can produce errors and warnings and suggest messages for users to act on. |
| 140.30 | System shall define Product rules in Z-Metrics aaS | 1 | Yes | Rules are defined by an admin that validates Product-level fields. Rules can produce errors and warnings and suggest messages for users to act on. |
| 140.40 | System shall define Ramp rules in Z-Metrics aaS | 1 | Yes | Rules are defined by an admin that validates Product-level fields. Rules can produce errors and warnings and suggest messages for users to act on. |
| 140.50 | System shall provide UI for user to setup an Approval Workflow in Z-Metrics aaS | 1 | Yes | Admin can set up work tasks for approval workflows using user roles. Workflows are triggered by quote field content. |

---

## 15. Self Service

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 150.10 | System shall access a self-service portal (sample implementation) | 3 | Yes | A portal for self-service users. This is usually provided by an existing eCommerce system deployed by and owned by Zuora customers. This requirement is for a sample portal implementation and not part of the CPQ product offering to facilitate demos. |
| 150.20 | System shall access self-serv widgets provided by Zuora CPQ | 3 | Yes | Typical widgets that allow the interaction of a self-service user with a Zuora customer. Examples: View the status of submitted quote requests, order status, usage data, make new quote request, etc |
| 150.30 | System shall access a self-service Catalog Experience | 3 | Yes | Self-service users can browse, search, and filter the catalog to find products and plans. Experience is very similar to sales reps and Zuora CPQ can reuse the UI and biz logic. |
| 150.40 | System shall access self-service Product Configurator Experience | 3 | Yes | Self-service users can configure a product. Experience is very similar to sales reps. |
| 150.50 | System shall access self-service Shopping Cart Experience (sample implementation) | 3 | Yes | Self-service users can add products/plans to a cart. Experience is very similar to sales reps adding products to a quote. |
| 150.60 | System shall request a Quote | 2 | Yes | The user requests a quote instead of placing an order. This is typically done in the shopping cart, but requesting a quote can also be offered as part of the catalog experience on the product detail page. |
| 150.70 | System shall create a Quote in Z-CPQ system | 2 | Yes | When a user requests a quote instead of placing an order, the customer commerce system generates a quote in Zuora CPQ. |
| 150.80 | System shall initiate and process a Shopping Cart check-out | 5 | No | Typical check-out with payment and order confirmation. This shall not be implemented for Zuora CPQ MVP. |

---

## 16. Indirect Channel

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 160.10 | Partner Sales Rep shall access a disti portal (sample implementation) in Partner Portal | 4 | No | A portal for VAR sales reps (2nd tier) provided by the distributor (1st tier). A simple portal to be shown only for demos, not part of the CPQ offering. |
| 160.20 | Partner Sales Rep shall access disti widgets provided by Zuora CPQ in Partner Portal | 4 | No | Widgets that allow a VAR sales rep to start creating a quote and a widget that shows status of existing quotes. |
| 161.30 | Partner Sales Rep shall able to create a SPR and send it to Zuora on the disti portal or disti marketplace in Partner Portal | 4 | No | A VAR sales rep will create a quote for their customer. The purpose is to show how a VAR sales rep can create a quote for configurable products and solutions with ramps. |
| 160.40 | Sales Rep shall send quote with SPR# via email in Partner Portal | 3 | Yes | A disti sales rep will create for the VAR quote an SPR. The VAR sales rep cannot win the deal unless the Zuora customer provides higher discounts to the disti. |
| 160.50 | Partner Sales Rep shall support disti placing an order with the solution provider in Partner Portal | 3 | Yes | A channel rep on the Zuora customer side will pick up the SPR and process it, similar to a quote. |
| 161.60 | Sales Ops Admin shall enable Product/Plan/Price Export in Partner Portal | 3 | Yes | After the channel rep sends back the approved SPR, the disti sales rep can place an order. The order must have the SPR # as a reference to get the agreed favorable price. |
| 162.70 | System shall in Partner Portal | 3 | Yes | A channel ops person generates exports of products and prices that can be imported into a disti portal. |

---

## 17. User Management

| ID | Requirement | Priority | MVP | Notes |
|----|-------------|----------|-----|-------|
| 170.10 | System shall allow assignment of users to one or multiple billing orgs in Partner Portal | 2 | Yes | Our customers will want to import their sales users into Zuora CPQ. |
| 170.20 | System shall provide a sales rep profile in Partner Portal | 1 | Yes | Support assignment of billing orgs to user. |
| 170.30 | System shall provide a 'buyer viewer' profile in Partner Portal | 1 | Yes | A sales rep can only access their own quotes. Sales reps can only quote products for billing orgs to which they are assigned. |
| 170.40 | System shall provide a 'buyer signee' profile in Partner Portal | 1 | Yes | A buyer viewer can access quote proposals in the Deal Room. |
| 170.50 | System shall provide a sales manager profile in Partner Portal | 1 | Yes | The sales manager has access to all quotes of their assigned sales reps. Sales managers only comment on quotes and quote lines. Also, they approve or reject a quote for which they got an approval workflow task. |
| 170.60 | System shall provide a deal desk admin profile in Partner Portal | 1 | Yes | The deal desk admin can access all quotes within their assigned billing org. |
| 170.70 | System shall provide a solution manager profile in Partner Portal | 1 | Yes | A solution manager can access all quotes within their assigned billing org. Solution managers have the same functionality access as sales reps. |
| 170.80 | System shall provide a sales admin profile in Partner Portal | 1 | Yes | The sales admin has access to the catalog, quote setup, quote rules, and config rules admin. They also have viewing access to all quotes in the production system. |
| 170.90 | System shall provide a partner sales rep profile in Partner Portal | 1 | Yes | The partner sales rep has access to only the SPRs he/she made and can see orders he/she placed. |
| 170.100 | System shall assign data level security in Partner Portal | 1 | Yes | What data can a user with a certain profile access? For example, a sales rep can only access quotes that he created. A sales manager can only access quotes that belong to their organization. |
| 170.110 | System shall provide a license management function in Partner Portal | 3 | Yes | It is important in the long run, but not from the get-go as we are starting to sell this new app. |

---

## 18. Priority and Ranking

### Vision Demo Priorities

| Rank | Feature | Priority |
|------|---------|----------|
| 1 | Quote Management | Must Have |
| 2 | Pricing Service Integration | Must Have |
| 3 | Quote Line Management | Must Have |
| 4 | Ramping Deal | Must Have |
| 5 | Catalog Experience (browse, search, filter) | Must Have |
| 6 | Quote Metrics | Must Have |
| 7 | Workflow (simple) | Must Have |
| 8 | Quote Rules | Must Have |
| 9 | CRM Integration with SFDC | Must Have |
| 10 | Type of Product: Product Configurator | Must Have |
| 11 | Type of Product: Configuration of Solutions | Must Have |
| 11 | Type of Product: Regular Product | Very Important |
| 13 | Smart Quote Line Management | Very Important |
| 14 | Guided Selling Product Recommendations | Very Important |
| 15 | Backend Metrics | Very Important |
| 16 | Deal Score | Very Important |
| 17 | Deal Engine | Very Important |
| 18 | Direct Omnichannel (self serv to assisted) | Very Important |
| 19 | Deal Room | Very Important |
| 20 | Make quote with prompt | Very Important |
| 21 | Opportunity sync | Very Important |
| 22 | Type of Product: Hard (Product) Bundle | Very Important |
| 23 | OM and Billing Integration | Important |
| 23 | Amendments | Important |
| 24 | Outcome-based Pricing of Solutions | Important |
| 25 | Renewals | Important |
| 26 | Billing Features (exposed in CPQ) | Important |
| 28 | Price Guidance | Important |
| 29 | Deal Desk enablement | Important |
| 30 | Workflow Advanced | Optional |
| 30 | Soft Bundle | Optional |
| 31 | Guided Selling Smart Filters | Optional |
| 32 | Type of Product: Hard (Charge) Bundle | Optional |
| 34 | Proposal Gen | Optional |
| 35 | Pre-Configuration | Optional |
| 99 | CRM Integration with other CRMs | Optional |
| 99 | Advanced Billing Features (exposed in CPQ) | Optional |
| 99 | Guided Selling Wizard | Optional |
| 99 | Indirect (Selling Partner enablement) | Optional |

### MVP Priorities

| Rank | Feature | Priority |
|------|---------|----------|
| 1 | Quote Management | Must Have |
| 2 | Pricing Service Integration | Must Have |
| 3 | Quote Line Management | Must Have |
| 4 | Proposal Gen | Must Have |
| 5 | Type of Product: Regular Product | Must Have |
| 6 | Ramping Deal | Must Have |
| 7 | Amendments | Must Have |
| 8 | Renewals | Must Have |
| 9 | Quote Metrics | Must Have |
| 10 | OM and Billing Integration | Must Have |
| 11 | Billing Features (exposed in CPQ) | Must Have |
| 12 | Workflow (simple) | Must Have |
| 13 | Quote Rules | Must Have |
| 14 | CRM Integration with SFDC | Must Have |
| 15 | Type of Product: Hard (Charge) Bundle | Must Have |
| 16 | Type of Product: Product Configurator | Must Have |
| 17 | Type of Product: Configuration of Solutions | Must Have |
| 18 | Type of Product: Hard (Product) Bundle | Must Have |
| 19 | Catalog Experience (browse, search, filter) | Must Have |
| 20 | Opportunity sync | Must Have |
| 21 | Smart Quote Line Management | Very Important |
| 22 | Guided Selling Product Recommendations | Very Important |
| 23 | Deal Score | Very Important |
| 24 | Backend Metrics | Very Important |
| 25 | Deal Engine | Very Important |
| 26 | Make quote with prompt | Very Important |
| 27 | Deal Room | Very Important |
| 28 | Workflow Advanced | Very Important |
| 30 | Direct Omnichannel (self serv to assisted) | Very Important |
| 31 | CRM Integration with other CRMs | Very Important |
| 32 | Price Guidance | Important |
| 33 | Outcome-based Pricing of Solutions | Important |
| 34 | Deal Desk enablement | Important |
| 35 | Soft Bundle | Important |
| 36 | Guided Selling Smart Filters | Optional |
| 37 | Pre-Configuration | Optional |
| 38 | Advanced Billing Features (exposed in CPQ) | Optional |
| 39 | Guided Selling Wizard | Optional |
| 40 | Indirect (Selling Partner enablement) | Optional |

---

## Main Sections Summary

- Catalog End User
- Catalog Admin
- Product Configurator End User
- Solution Configurator End User
- Configurator Admin
- Presales Sales Rep Experience: Price Guidance
- Quote Sales Rep Experience
- Quote Metrics Display
- Quote Deal Engine
- Quote Deal Room
- Quote Deal Desk
- Approval Workflow
- AI Framework
- Quote Rules, Settings & User Admin
- Direct - Quote Request Flow
- Indirect - SPR
- User Management

---

*Document generated from Next Gen Functionality List CSV files*
