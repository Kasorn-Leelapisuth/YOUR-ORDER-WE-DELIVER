# YOUR ORDER WE DELIVER - Delivery Management System

SWE30003 Software Architectures and Design (Assignment 3)  
Group 4  

## Overview
This project is an object-oriented Python implementation of the Delivery Management System for Your Order We Deliver. The system handles delivery booking, zone-based pricing quotes, payment processing, driver availability rostering, and order dispatch across Greater Melbourne.

## Project Structure
* `domain_models.py` - Core domain entities (User, Customer, Driver, AddressZone, Parcel, Quote, Payment).
* `subsystem_controllers.py` - Business logic controllers and file persistence (PricingEngine, OrderCoordinator, RosterManager, DispatchManager).
* `delivery_app.py` - Command-line interface (CLI) for running and testing the system.

## Requirements
* Python 3.8 or higher (uses Python standard libraries only: `json`, `datetime`, `os`).

## How to Run
1. Open a terminal or command prompt and navigate into the project folder where the repository was cloned or extracted:
   ```bash
   cd <path-to-project-folder>
   ```
2. Run the application entry point:
   ```bash
   python3 delivery_app.py
   ```
   *(Windows users can run `python delivery_app.py`)*

## Features & Verification Scenarios
* **Option 1: Log Delivery Request & Calculate Quote**  
  Accepts customer details, pickup/destination addresses, postcodes, and parcel specifications. Rejects invalid inputs (e.g., non-Melbourne postcodes or negative weights) with graceful defensive validation. Computes delivery quote based on distance factors and parcel size.
* **Option 2: Confirm Booking & Process Payment**  
  Confirms the quoted order and executes simulated payment settlement via credit/debit card online or cash on pickup.
* **Option 3: Cancel Delivery Job**  
  Cancels a logged delivery order to verify the change of mind / input deletion scenario.
* **Option 4: View Driver Roster & Shift Availability**  
  Displays the current driver fleet, operating zones, and real-time duty availability.
* **Option 5: Allocate & Dispatch Driver to Order**  
  Assigns a suitable available driver to an accepted delivery job and updates the order status to `In_Transit`.
* **Data Persistence**  
  Automatically saves all active orders and driver updates to `delivery_orders.json` and `driver_roster.json` so data persists across application restarts.