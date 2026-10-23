"""
SWE30003 Software Architectures and Design - Assignment 3
Group 4 - Your Order We Deliver (Melbourne)
subsystem_controllers.py: Subsystem controllers implementing business workflows.
"""

import json
import os

from domain_models import (
    AddressZone,
    CardPayment,
    CashPayment,
    DeliveryRequest,
    Driver,
    Parcel,
    Quote
)


class PricingEngine:
    """Business Area 2: Calculates delivery rates and operational windows."""
    def __init__(self, base_rate=12.00, km_rate=8.50):
        self.base_rate = float(base_rate)
        self.km_rate = float(km_rate)

    def calculate_quote(self, req_id, parcel, pickup_zone, dest_zone):
        dist_diff = abs(pickup_zone.dist_factor - dest_zone.dist_factor) + 1.0
        dist_cost = dist_diff * self.km_rate
        weight_cost = parcel.weight_kg * 1.50

        total = self.base_rate + dist_cost + weight_cost + parcel.get_category_rate() + parcel.get_handling_fee()

        pickup_window = int(1 + (dist_diff * 0.5))
        delivery_window = pickup_window + int(2 + (dist_diff * 0.8))

        return Quote(f"Q-{req_id}", total, pickup_window, delivery_window)


class OrderCoordinator:
    """Business Area 1: Coordinates order intake, address checking, and quotes."""
    def __init__(self, storage_file="delivery_orders.json"):
        self.storage_file = storage_file
        self.pricing_engine = PricingEngine()
        self.requests = {}
        self.zones = self._setup_greater_melbourne()
        self.load_orders()

    def _setup_greater_melbourne(self):
        return {
            "3000": AddressZone("3000", "Melbourne CBD", True, 1.0),
            "3122": AddressZone("3122", "Hawthorn", True, 1.4),
            "3141": AddressZone("3141", "South Yarra", True, 1.3),
            "3053": AddressZone("3053", "Carlton", True, 1.1),
            "3182": AddressZone("3182", "St Kilda", True, 1.5),
            "3030": AddressZone("3030", "Werribee", True, 2.5),
            "3175": AddressZone("3175", "Dandenong", True, 2.8)
        }

    def validate_postcode(self, postcode):
        code = str(postcode).strip()
        if code in self.zones and self.zones[code].is_valid_zone():
            return self.zones[code]
        return None

    def log_delivery_request(self, cust_id, pickup_addr, p_postcode, dest_addr, d_postcode, weight, size, special=False):
        if not str(cust_id).strip():
            raise ValueError("Customer ID cannot be empty.")
        if not str(pickup_addr).strip() or not str(dest_addr).strip():
            raise ValueError("Street addresses cannot be empty.")

        p_zone = self.validate_postcode(p_postcode)
        d_zone = self.validate_postcode(d_postcode)

        if not p_zone:
            raise ValueError(f"Pickup postcode '{p_postcode}' is outside Greater Melbourne.")
        if not d_zone:
            raise ValueError(f"Destination postcode '{d_postcode}' is outside Greater Melbourne.")

        req_id = f"REQ-{len(self.requests) + 1:04d}"
        parcel_id = f"PCL-{len(self.requests) + 1:04d}"

        parcel = Parcel(parcel_id, weight, size, special)
        order = DeliveryRequest(req_id, cust_id, pickup_addr, dest_addr, parcel, p_zone, d_zone)

        quote = self.pricing_engine.calculate_quote(req_id, parcel, p_zone, d_zone)
        order.attach_quote(quote)

        self.requests[req_id] = order
        self.save_orders()
        return order

    def confirm_customer_booking(self, req_id, payment_type="card"):
        if req_id not in self.requests:
            return False, "Order ID not found."

        order = self.requests[req_id]
        method = CardPayment() if payment_type.lower() == "card" else CashPayment()
        payment_msg = order.confirm_booking(method)
        self.save_orders()
        return True, payment_msg

    def cancel_delivery_request(self, req_id):
        if req_id in self.requests:
            self.requests[req_id].cancel()
            self.save_orders()
            return True
        return False

    def save_orders(self):
        data = {r_id: req.to_dict() for r_id, req in self.requests.items()}
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_orders(self):
        if not os.path.exists(self.storage_file):
            return
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                for r_id, item in saved.items():
                    p_data = item["parcel"]
                    p_zone = self.validate_postcode("3000")
                    d_zone = self.validate_postcode("3122")
                    parcel = Parcel(p_data["id"], p_data["weight"], p_data["size"], p_data["special"])
                    order = DeliveryRequest(r_id, item["cust_id"], item["pickup_addr"], item["dest_addr"], parcel, p_zone, d_zone)
                    order.status = item["status"]
                    order.assigned_driver_id = item["driver_id"]
                    self.requests[r_id] = order
        except Exception:
            pass


class RosterManager:
    """Business Area 3: Fleet Roster & Availability (Assignment 1 Task 4)."""
    def __init__(self, roster_file="driver_roster.json"):
        self.roster_file = roster_file
        self.drivers = {}
        self._seed_fleet()
        self.load_roster()

    def _seed_fleet(self):
        sample_fleet = [
            Driver("DRV-01", "Alex Smith", "0411222333", "alex@delivery.com", "3000", True),
            Driver("DRV-02", "Sarah Tan", "0422333444", "sarah@delivery.com", "3122", True),
            Driver("DRV-03", "Chris Evans", "0433444555", "chris@delivery.com", "3141", False),
            Driver("DRV-04", "Emma Watson", "0444555666", "emma@delivery.com", "3053", True)
        ]
        for d in sample_fleet:
            self.drivers[d.driver_id] = d

    def get_available_drivers(self):
        return [d for d in self.drivers.values() if d.is_available]

    def save_roster(self):
        data = {d_id: d.to_dict() for d_id, d in self.drivers.items()}
        with open(self.roster_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_roster(self):
        if not os.path.exists(self.roster_file):
            self.save_roster()
            return
        try:
            with open(self.roster_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                for d_id, item in saved.items():
                    d = Driver(
                        item["driver_id"],
                        item["name"],
                        item["phone"],
                        f"{item['name'].lower().replace(' ', '')}@delivery.com",
                        item["operating_zone"],
                        item["is_available"]
                    )
                    d.current_job_id = item.get("current_job_id")
                    self.drivers[d_id] = d
        except Exception:
            pass


class DispatchManager:
    """Business Area 4: Active Driver Allocation & Job Dispatch (Assignment 1 Task 5)."""
    def __init__(self, roster_manager, order_coordinator):
        self.roster_manager = roster_manager
        self.order_coordinator = order_coordinator

    def allocate_driver(self, req_id):
        if req_id not in self.order_coordinator.requests:
            return False, f"Order '{req_id}' not found."

        order = self.order_coordinator.requests[req_id]
        if order.status != "Accepted":
            return False, f"Order is '{order.status}'. Only 'Accepted' orders can be dispatched."

        available_drivers = self.roster_manager.get_available_drivers()
        if not available_drivers:
            return False, "No on-duty drivers available in fleet."

        # Match driver operating in the pickup zone first
        chosen_driver = None
        for d in available_drivers:
            if d.operating_zone == order.pickup_zone.postcode:
                chosen_driver = d
                break

        if not chosen_driver:
            chosen_driver = available_drivers[0]

        chosen_driver.assign_job(order.req_id)
        order.assign_driver(chosen_driver.driver_id)

        self.roster_manager.save_roster()
        self.order_coordinator.save_orders()
        return True, f"Allocated Driver {chosen_driver.name} ({chosen_driver.driver_id}) to {order.req_id}."