\# Zuora Commerce: Merchandising, Packaging, and Bundles

\#\# What This Document Covers

This document explains how we're improving how businesses create and manage product packages and bundles in Zuora. It's written for all business stakeholders.

\---

\#\# Why This Matters

Right now, creating product packages (like "Startup Bundle" or "Enterprise Suite") is harder than it should be. You can't easily:  
\- Group products together as a single offering  
\- Let customers pick from a set of options  
\- Create tiered packages (Good/Better/Best)  
\- Show product relationships in your catalog

This makes it difficult to sell the way your customers want to buy.

\---

\#\# Core Concepts

Before we explain the solution, here's how Zuora organizes subscription products:

\#\#\# The Basic Building Blocks

\*\*Offer\*\* â†’ The complete thing a customer buys  
\- Example: "Professional Plan Annual"

\*\*Product\*\* â†’ What you're selling  
\- Example: "Project Management Software"

\*\*Plan\*\* â†’ Terms for how customers pay  
\- Example: "Annual" or "Monthly"

\*\*Charge\*\* â†’ Individual pricing items  
\- Example: "$99/month" or "$50 per additional user"

\#\#\# How They Work Together  
An \*\*Offer\*\* combines a \*\*Product\*\* with a \*\*Plan\*\* which contains \*\*Charges\*\*. This creates the specific thing a customer can purchase.

\*\*Simple example:\*\*  
\- Product: "Email Marketing Tool"  
\- Plan: "Monthly Subscription"  
\- Charge: "$29/month for up to 10,000 contacts"  
\- Offer: "Email Marketing Tool \- Monthly"

\---

\#\# The Problem We're Solving

Today, if you want to sell products as packages or bundles, you face these challenges:

\#\#\# 1\. \*\*No Native Package Structure\*\*  
You can't group related products together as a single package. Want to sell a "Marketing Suite" with email, social media, and analytics tools? You have to create workarounds.

\#\#\# 2\. \*\*Can't Show Relationships\*\*  
\- Products that naturally go together look unrelated  
\- Cross-sells and upsells require manual tracking  
\- Dependencies between products aren't visible

\#\#\# 3\. \*\*Manual Bundle Creation\*\*  
\- Creating bundles requires custom coding  
\- No standard way to say "pick 3 from these 5 options"  
\- Can't easily create tiered packages (Starter/Pro/Enterprise)

\#\#\# 4\. \*\*Poor Customer Experience\*\*  
\- Customers see flat product lists instead of curated packages  
\- Can't easily compare tiers  
\- Upgrade paths aren't clear

\#\#\# 5\. \*\*Business Impact\*\*  
\- Slower time-to-market for new packages  
\- Inconsistent bundle pricing and discounting  
\- Hard to track which packages perform best  
\- Can't quickly respond to competitive pressures

\---

\#\# Our Solution

We're adding two new capabilities to Zuora:

\#\#\# Packages  
\*\*What it is:\*\* A curated group of products sold together as a single offering.

\*\*When to use it:\*\* When you want to bundle multiple products that customers always buy together.

\*\*Examples:\*\*  
\- "Startup Bundle" \= CRM \+ Email Marketing \+ Basic Support  
\- "Office Suite" \= Word Processing \+ Spreadsheet \+ Presentation software  
\- "Complete Security Package" \= Antivirus \+ VPN \+ Password Manager

\*\*Key features:\*\*  
\- Group any products together  
\- Set package-level pricing (can be different from individual prices)  
\- Add package-level discounts  
\- Define what's included clearly

\#\#\# Bundles  
\*\*What it is:\*\* A flexible framework where customers choose products from predefined options.

\*\*When to use it:\*\* When customers need flexibility to pick what they want from a curated selection.

\*\*Examples:\*\*  
\- "Pick 3 Streaming Channels" from 10 available options  
\- "Build Your Plan" \- select base \+ choose add-ons  
\- "Choose Your Apps" \- 5 included, pay for additional

\*\*Key features:\*\*  
\- Define available options  
\- Set selection rules ("pick at least 3" or "pick up to 5")  
\- Each option can have different pricing  
\- Flexible quantity limits per option

\---

\#\# How They Work Together

Think of it like this:

\*\*Packages\*\* \= Pre-made combos (like a \#1 Value Meal)  
\- Fixed contents  
\- One price for everything  
\- Customer gets what's in the package

\*\*Bundles\*\* \= Build-your-own (like a create-your-own-combo)  
\- Customer chooses from options  
\- Price varies based on choices  
\- Flexible within defined rules

\*\*You can even combine them:\*\*  
A bundle could include a package as one of its options. Example: "Enterprise Bundle" lets customers pick: Professional Package OR Enterprise Package \+ choose 3 add-ons from a list.

\---

\#\# What This Enables

\#\#\# For Sales Teams  
\- Create compelling package offers quickly  
\- Show clear upgrade paths (Starter â†’ Pro â†’ Enterprise)  
\- Respond faster to customer requests for custom bundles  
\- Present cohesive solutions instead of product lists

\#\#\# For Marketing Teams  
\- Launch promotional bundles without engineering  
\- Test different package combinations easily  
\- Create competitive packages quickly  
\- Better control over pricing and positioning

\#\#\# For Product Teams  
\- Structure products to match customer needs  
\- See which bundles drive most value  
\- Iterate on package offerings based on data  
\- Build logical product families

\#\#\# For Finance Teams  
\- Consistent revenue recognition across bundles  
\- Clear reporting on package performance  
\- Simplified discount management  
\- Better forecasting of package vs. individual sales

\#\#\# For Customers  
\- Easier to understand what they're buying  
\- Clear choices between tiers  
\- Flexibility to customize when needed  
\- Transparent pricing for bundles

\---

\#\# Real-World Examples

\#\#\# Example 1: SaaS Company with Tiered Packages

\*\*Current approach:\*\* Three separate offers (Starter, Pro, Enterprise) with no visible relationship

\*\*With Packages:\*\*  
\- \*\*Starter Package:\*\* Base product \+ 5 user licenses \+ email support  
\- \*\*Pro Package:\*\* Everything in Starter \+ Advanced features \+ 20 user licenses \+ phone support  
\- \*\*Enterprise Package:\*\* Everything in Pro \+ Custom integrations \+ Unlimited users \+ dedicated manager

Customers can clearly see what they get at each tier and how to upgrade.

\#\#\# Example 2: Media Company with Channel Selection

\*\*Current approach:\*\* Customers must subscribe to each channel individually

\*\*With Bundles:\*\*  
\- \*\*Basic Bundle:\*\* "Choose 5 channels from our standard tier" \- $29.99/month  
\- \*\*Premium Bundle:\*\* "Choose 3 channels from our premium tier" \- $39.99/month  
\- \*\*Ultimate Bundle:\*\* "Unlimited access to all channels" \- $59.99/month

Customers can customize while staying within your pricing structure.

\#\#\# Example 3: Business Services with Add-ons

\*\*Current approach:\*\* Base service sold separately from add-ons, unclear relationships

\*\*With Packages \+ Bundles:\*\*  
\- \*\*Core Package:\*\* Accounting Software \+ Basic Payroll \+ Tax Filing  
\- \*\*Bundle Options:\*\* "Add up to 5 premium features" (Inventory, Multi-currency, Advanced reporting, etc.)  
\- Each add-on priced individually but shown as part of one cohesive offering

Customers see the complete solution and can customize without confusion.

\---

\#\# Key Principles

\#\#\# 1\. \*\*Flexibility Over Rigidity\*\*  
Packages are fixed, bundles are flexible. Use the right tool for your use case.

\#\#\# 2\. \*\*Preserve Existing Structure\*\*  
Packages and bundles work with your existing Products, Plans, and Charges. Nothing breaks.

\#\#\# 3\. \*\*Business Control\*\*  
Create and modify packages without engineering work. Test and iterate quickly.

\#\#\# 4\. \*\*Clear Customer Experience\*\*  
Customers should always understand what they're getting and what it costs.

\#\#\# 5\. \*\*Track Everything\*\*  
Know which packages perform best, which bundles convert highest, and where customers customize most.

\---

\#\# What's Not Changing

\- Your existing products, plans, and charges stay as they are  
\- Current customers' subscriptions are unaffected  
\- How you build individual products remains the same  
\- Billing and pricing logic works the same way

\*\*What we're adding:\*\* A layer on top that lets you organize and present products differently.

\---

\#\# How We're Building This

\#\#\# Phase 1: Package Foundation (Months 1-3)  
\*\*What:\*\* Create basic package capability  
\*\*Delivers:\*\* Ability to group products, set package pricing, manage package lifecycle

\#\#\# Phase 2: Bundle Framework (Months 4-6)  
\*\*What:\*\* Add bundle creation and selection rules  
\*\*Delivers:\*\* Flexible bundles with customer choice, quantity rules, option pricing

\#\#\# Phase 3: Advanced Features (Months 7-9)  
\*\*What:\*\* Package hierarchies, bundle templates, package analytics  
\*\*Delivers:\*\* Complex package structures, reusable bundle patterns, performance insights

\#\#\# Phase 4: Optimization (Months 10-12)  
\*\*What:\*\* AI recommendations, automated optimization, advanced bundling strategies  
\*\*Delivers:\*\* Smart package suggestions, automated pricing optimization, bundle performance AI

\---

\#\# Common Questions

\*\*Q: Do packages and bundles replace products?\*\*  
No. They organize existing products. Your products stay as they are.

\*\*Q: Can a product be in multiple packages?\*\*  
Yes. The same product can appear in as many packages as you want.

\*\*Q: How do discounts work in packages?\*\*  
You can set package-level discounts that apply to the bundle price, or individual product discounts within the package.

\*\*Q: Can customers modify a package after purchase?\*\*  
Yes, if you allow it. You control whether packages are fixed or customizable after purchase.

\*\*Q: Do bundles affect billing?\*\*  
Bundles are merchandising constructs. They define what customers select, then billing works normally based on their choices.

\*\*Q: Can we migrate existing custom bundles to this system?\*\*  
Yes. We'll provide migration tools to convert custom bundle implementations to the native system.

\---

\#\# Success Metrics

We'll know this is successful when:  
\- Time to create a new package drops from days to minutes  
\- Package attach rates improve (more customers buy packages vs. individual products)  
\- Revenue per customer increases (packages drive larger deals)  
\- Sales cycle time decreases (clearer offerings close faster)  
\- Customer satisfaction improves (easier to understand what they're buying)