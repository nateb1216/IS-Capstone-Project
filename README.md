# IS-Capstone-Project

Overview 

For this project, team 2 gained familiarity with distributed messaging concepts, and using Google Pub/Sub to set up messaging endpoints and publish/subscribe messages using those endpoints. Additionally, team 2 gained an understanding of available message delivery options such as Guaranteed Delivery, and solved the issue of duplicate messages which is a common side effect of using Guaranteed Delivery. Members of team 2 include: Jayda Smith, Josh McCrary, Victoria Ewoigbokhan and Nate Belete. The system will demonstrate how to use Google Cloud Pub Sub to process orders distributed using ecommerce. Publishers will send order details to the designated topic. Subscribers will process orders as they come in. Faculty and staff will be able to rely on a system that can handle high-volume orders and promise guaranteed delivery. The system will identify duplicate messages in order to prevent duplicate charges or multiple shipments of the same order.  

Faculty and staff use the system to place an order, get a Purchase Order ID (POID), and track status with the option to cancel until it ships. A clean catalog of school supplies keeps items and prices valid. Behind the scenes, Google Pub/Sub moves each order with acknowledgments, automatic retries, and a dead-letter safety net, so delivery is guaranteed and there are no lost orders. The three main services are Inventory checks and reserves stock, Payment charges the order exactly once, and Shipping packs and sends U.S. deliveries with tracking. We also watch for duplicates by POID, so repeat messages don’t cause extra charges or shipments. Requesters get email confirmations and updates, admins can step in to manage settings and fix issues, and everything is logged and monitored for at least 30 days to keep the system reliable and transparent.

Tech stack: Pub/Sub, Python, Flask, SQLite (or Cloud SQL), VS Code, GitHub



Milestone References & Summaries 

Milestone 1 - Functional Requirements. Here, team 2 communicated system capabilities to users and stakeholders after requirements analysis. They outlined the system’s features, behaviors, and interactions in plain,non-technical terms so stakeholders could understand them

Milestone 2 - Technical Requirements. Here, team 2 communicated the system’s design and build details to the development team. They included detailed specifications that developers used in creating and implementing the system.

Milestone 3 - Mid-semester Presentations. Here, team 2 provided stakeholders with a presentation on the progress made thus far within the project. 

Milestone 4 - Test Plan and Scripts. Here, team 2 developed test scripts for the application, describing the steps to be taken and expected outcomes.

Milestone 5 - System Testing and Results Document. Here, team 2 executed the test scripts and recorded the actual results of the system and compared them against the expected results described in Milestone 4.
