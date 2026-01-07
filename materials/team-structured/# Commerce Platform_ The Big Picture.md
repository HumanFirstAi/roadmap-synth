\# Commerce Platform: The Big Picture

\#\# What This Document Is For

This is your guide to understanding what we're building across our commerce platform. If you're new to the team, need to explain our strategy to others, or just want to understand how everything fits together, start here.

For detailed information on any specific area, we'll point you to the right document.

\---

\#\# The Problem We're Solving

Right now, selling subscriptions is harder than it should be. Here's what businesses struggle with:

\*\*Managing pricing and business rules\*\*  
\- Rules are scattered across different systems  
\- Changes take weeks and require multiple teams  
\- Nobody's sure which rule is "correct"  
\- Testing new pricing is slow and risky

\*\*Creating packages and bundles\*\*  
\- Can't easily group products together  
\- No way to let customers build their own bundles  
\- Tiered offerings (Good/Better/Best) require workarounds

\*\*Showing customers the right offers\*\*  
\- Same pricing appears for everyone regardless of location  
\- Can't automatically personalise based on who the customer is  
\- Different channels show inconsistent offers

\*\*The result?\*\* Lost revenue, confused customers, slow time-to-market, and frustrated teams who spend time on manual work instead of strategy.

\---

\#\# Our Solution: Three Connected Capabilities

We're building three systems that work together to solve these problems:

\#\#\# 1\. Commerce Foundation: The Rules Engine  
\*\*What it does:\*\* Creates a single place to define and manage all your subscription rules (pricing, discounts, trials, etc.)

\*\*The key insight:\*\* Rules should be defined once and used everywhere. When a rule changes, it updates automatically across all systems.

\*\*Example:\*\* Instead of updating pricing in five different places, you change it once and everywhere updates instantly.

â†’ \*\*\[Read the full Commerce Foundation Strategy document for details\]\*\*

\#\#\# 2\. Business Context Service: The Smart Layer  
\*\*What it does:\*\* Automatically understands each customer's situation (location, customer type, channel) and applies the right rules to them.

\*\*The key insight:\*\* Context should be automatic. The system should detect where customers are, who they are, and what they're doing, then show them appropriate offers without manual configuration.

\*\*Example:\*\* A customer in Germany automatically sees Euro pricing with EU terms. An enterprise customer sees business pricing. All automatic.

â†’ \*\*\[Read the full Business Context Service document for details\]\*\*

\#\#\# 3\. Zuora Commerce Merchandising: The Packaging Layer  
\*\*What it does:\*\* Lets you create product packages and flexible bundles that customers can choose from.

\*\*The key insight:\*\* Customers don't want to buy individual products from a flat list. They want curated packages and the ability to customise within guardrails.

\*\*Example:\*\* Create a "Startup Bundle" that combines three products, or let customers "Pick 5 channels from this list" for a custom streaming package.

â†’ \*\*\[Read the full Zuora Commerce Merchandising document for details\]\*\*

\---

\#\# How They Work Together

Think of these three systems as layers that build on each other:

\`\`\`  
Customer sees: Professional Package for UK customers on mobile  
                           â†“  
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  
â”‚  MERCHANDISING: Package \= "Professional"            â”‚  
â”‚  (What the customer is buying)                      â”‚  
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  
                           â†“  
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  
â”‚  BUSINESS CONTEXT: Location \= UK, Channel \= Mobile  â”‚  
â”‚  (Who they are and how they're buying)              â”‚  
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  
                           â†“  
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  
â”‚  COMMERCE FOUNDATION: Rules \= GBP pricing, UK T\&Cs  â”‚  
â”‚  (What rules apply to this situation)               â”‚  
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  
\`\`\`

\*\*In practice:\*\*  
1\. \*\*Business Context\*\* detects the customer is in the UK, using your mobile app  
2\. \*\*Commerce Foundation\*\* knows the pricing rules for UK mobile customers  
3\. \*\*Merchandising\*\* shows the Professional Package with the right products and pricing  
4\. Customer sees exactly what they should see, automatically

\---

\#\# What Changes for Different Teams

\#\#\# Revenue Teams (Sales, Marketing, Pricing)  
\*\*Today:\*\* "We want to test a new discount structure. That needs engineering work, takes 2 weeks, involves 3 teams."

\*\*Future:\*\* "We want to test a new discount. Let me create that rule in Commerce Foundation... done. It's live and we're measuring results."

\*\*What you gain:\*\*  
\- Test pricing and offers without engineering dependencies  
\- Launch location-specific pricing in minutes, not weeks  
\- Create promotional bundles whenever you need them  
\- See real-time impact of your changes

\#\#\# Product Teams  
\*\*Today:\*\* "We're launching a new product tier. We need to configure pricing for each location, set up the tier in our systems, and update documentation. Then engineering needs to make it appear correctly on each channel."

\*\*Future:\*\* "We're launching a new product tier. It's a new Package in Merchandising. Business Context automatically handles locations and channels. Done."

\*\*What you gain:\*\*  
\- Bring products to market faster  
\- Structure offerings to match how customers think  
\- See which packages and bundles perform best  
\- Iterate based on real data

\#\#\# Operations & Finance Teams  
\*\*Today:\*\* "Did we charge this customer correctly? Let me check five systems to reconstruct what rules applied."

\*\*Future:\*\* "Here's the complete audit trail showing exactly which rules applied and why."

\*\*What you gain:\*\*  
\- Complete audit trail for every transaction  
\- Consistent rules across all systems  
\- Compliance built-in, not bolted on  
\- Clear reporting on what's driving revenue

\#\#\# Customer Support Teams  
\*\*Today:\*\* "Why is this customer seeing different pricing on web versus mobile? I'm not sure which is correct."

\*\*Future:\*\* "Both show the same pricing because it comes from one place. If something looks wrong, I can see exactly what context was detected and which rules applied."

\*\*What you gain:\*\*  
\- Give accurate information to customers  
\- Understand exactly what offer each customer saw  
\- Escalate issues with complete context

\#\#\# Engineering Teams  
\*\*Today:\*\* Spending significant time maintaining scattered configuration, implementing one-off business rules, and debugging pricing inconsistencies.

\*\*Future:\*\* Integrate with these systems once, then business teams manage the rules.

\*\*What you gain:\*\*  
\- Stop building custom logic for every business rule  
\- Focus on features, not configuration  
\- Reduce maintenance burden dramatically  
\- Clear APIs that handle complexity

\---

\#\# Current State vs Future State

\#\#\# Where We Are Today

\*\*Scattered systems\*\*  
\- Pricing in one place, business rules in another  
\- Each channel has its own configuration  
\- Manual updates across multiple systems

\*\*Manual work\*\*  
\- Creating bundles requires engineering  
\- Every location needs separate setup  
\- Testing new offers takes weeks

\*\*Limited flexibility\*\*  
\- Hard to personalise by customer type  
\- Can't quickly respond to market changes  
\- Difficult to see what's working

\#\#\# Where We're Going

\*\*Unified platform\*\*  
\- Single source for all business rules  
\- Automatic context detection  
\- Consistent experience across channels

\*\*Self-service\*\*  
\- Business teams create and test offers  
\- Changes go live in minutes  
\- No engineering work for most changes

\*\*Intelligent\*\*  
\- Automatic personalisation by context  
\- Real-time measurement and optimisation  
\- AI-powered recommendations

\---

\#\# The Journey: What Gets Built When

We're building this in phases so you can get value quickly while we work towards the complete vision.

\#\#\# Phase 1 (Months 1-3): Foundations  
\*\*What's delivered:\*\*  
\- Basic Commerce Foundation: Single place to define and view rules  
\- Basic Business Context: Automatic location and channel detection  
\- Basic Merchandising: Create simple packages

\*\*What you can do:\*\*  
\- Start centralising your business rules  
\- Create basic product packages  
\- See which customers get which context

\#\#\# Phase 2 (Months 4-6): Business User Control  
\*\*What's delivered:\*\*  
\- Self-service rule creation in Commerce Foundation  
\- Context Pane for targeting rules to specific situations  
\- Flexible bundles with customer choice

\*\*What you can do:\*\*  
\- Create and test pricing strategies without engineering  
\- Target offers to specific locations, channels, and customer types  
\- Let customers build their own bundles

\#\#\# Phase 3 (Months 7-9): Advanced Capabilities  
\*\*What's delivered:\*\*  
\- A/B testing and measurement  
\- Real-time session context  
\- Package hierarchies and templates  
\- Advanced analytics

\*\*What you can do:\*\*  
\- Run sophisticated experiments  
\- Optimise based on performance data  
\- Create complex package structures  
\- See detailed insights on what's working

\#\#\# Phase 4 (Months 10-12): Intelligence & Scale  
\*\*What's delivered:\*\*  
\- AI-powered recommendations  
\- Advanced governance and compliance  
\- Enterprise-scale features  
\- Automated optimisation

\*\*What you can do:\*\*  
\- Get smart suggestions on which rules to apply  
\- Support complex organisational structures  
\- Handle millions of transactions  
\- Let the system optimise automatically

\---

\#\# Key Principles Across Everything We're Building

\#\#\# 1\. Business Teams in Control  
You shouldn't need engineering to change pricing, create packages, or target offers. These are business decisions that should be in business hands.

\#\#\# 2\. Safe by Default  
Changes require explicit approval. You can preview before publishing. You can roll back if needed. We make it hard to break things accidentally.

\#\#\# 3\. One Source of Truth  
Every system reads from Commerce Foundation. Business Context is detected once and used everywhere. No more conflicting configurations.

\#\#\# 4\. Measure Everything  
Every rule, every test, every result is tracked. You'll always know what's working and what isn't.

\#\#\# 5\. Start Simple, Scale Up  
Basic use cases should be easy. Advanced scenarios can require more setup. You won't be overwhelmed on day one.

\---

\#\# Common Questions

\*\*Q: Will this replace our existing systems?\*\*  
No. These capabilities sit on top of and integrate with your existing billing, CRM, and commerce systems. They make those systems smarter, not replace them.

\*\*Q: Do we need to use all three?\*\*  
They're designed to work together, but you can adopt them independently. Business Context makes Commerce Foundation smarter. Merchandising uses both to create better packages. But each delivers value on its own.

\*\*Q: What happens to our current rules and pricing?\*\*  
Nothing immediately. We'll provide migration tools to move existing configurations into these systems on your timeline. Current setups keep working.

\*\*Q: Can we customise this for our specific business?\*\*  
Yes. While we provide standard dimensions (location, channel, customer type), you can define custom context attributes and rules for your unique needs.

\*\*Q: Who needs training on this?\*\*  
Revenue teams, product managers, and operations teams will be the primary users. We're designing it to be intuitive enough that training is minimal.

\*\*Q: How do we get started?\*\*  
Start with Commerce Foundation to centralise your rules. Add Business Context to make those rules smarter. Then add Merchandising to create better packages. Or jump straight to whichever solves your biggest pain point.

\---

\#\# What Doesn't Change

\- Your existing products and subscriptions  
\- How customers buy and use your services  
\- Your billing and payment systems  
\- Your analytics and reporting tools  
\- Your relationships with customers

\*\*What does change:\*\* These systems get smarter, faster, and easier to manage. You spend less time on configuration and more time on strategy.

\---

\#\# Success Looks Like

\*\*For the business:\*\*  
\- New offers launch in hours instead of weeks  
\- Revenue per customer increases through better packaging  
\- Fewer pricing errors and customer confusion  
\- Data-driven decisions about what works

\*\*For teams:\*\*  
\- Business users make changes without engineering  
\- Engineering focuses on features, not configuration  
\- Support gives accurate information to customers  
\- Operations maintains compliance effortlessly

\*\*For customers:\*\*  
\- See relevant offers for their situation  
\- Clear choices between packages and tiers  
\- Consistent experience across channels  
\- Fair pricing for their location

\---

\#\# Learn More

Each of these areas has a detailed strategy document:

\- \*\*Commerce Foundation Strategy\*\* \- Deep dive on the rules engine  
\- \*\*Business Context Service\*\* \- How automatic context detection works  
\- \*\*Zuora Commerce Merchandising\*\* \- Creating packages and bundles

For technical implementation details, see the Engineering Specifications.

For user workflows and training, see the User Documentation.

\---

\#\# The Bottom Line

We're building a commerce platform where:

1\. \*\*Rules are defined once\*\* and used everywhere (Commerce Foundation)  
2\. \*\*Context is automatic\*\* so customers see the right offers (Business Context Service)    
3\. \*\*Products are packaged\*\* the way customers want to buy (Merchandising)

Together, these three capabilities transform subscription commerce from a slow, manual, error-prone process into a fast, automated, intelligent system that drives revenue and delights customers.

This is about giving business teams the tools to respond to markets in real-time, test new strategies instantly, and deliver personalised experiences at scaleâ€”without drowning in technical complexity.