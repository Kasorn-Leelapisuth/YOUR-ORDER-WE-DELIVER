"""
SWE30003 Software Architectures and Design - Assignment 3
Group 4 - Your Order We Deliver (Melbourne)
domain_models.py: Domain entities reflecting Assignment 2 CRC Card specifications.
"""

from datetime import datetime


class User:
    """Base user entity for human actors."""
    def __init__(self, user_id, name, phone, email):
        self.user_id = str(user_id)
        self.name = str(name)
        self.phone = str(phone)
        self.email = str(email)

    def get_contact_details(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email
        }


class Customer(User):
    """Customer placing orders (Assignment 2 Domain Model)."""
    def __init__(self, user_id, name, phone, email, default_address=""):
        super().__init__(user_id, name, phone, email)
        self.default_address = str(default_address)


class Driver(User):
    """Field delivery staff assigned to jobs."""
    def __init__(self, driver_id, name, phone, email, operating_zone, is_available=True):
        super().__init__(driver_id, name, phone, email)
        self.driver_id = str(driver_id)
        self.operating_zone = str(operating_zone)
        self.is_available = bool(is_available)
        self.current_job_id = None

    def update_availability(self, status):
        self.is_available = bool(status)

    def assign_job(self, req_id):
        self.current_job_id = str(req_id)
        self.is_available = False

    def complete_job(self):
        self.current_job_id = None
        self.is_available = True

    def to_dict(self):
        return {
            "driver_id": self.driver_id,
            "name": self.name,
            "phone": self.phone,
            "operating_zone": self.operating_zone,
            "is_available": self.is_available,
            "current_job_id": self.current_job_id
        }


class AddressZone:
    """Operating boundaries for Greater Melbourne (Task 1 & 2)."""
    def __init__(self, postcode, suburb, is_melb, dist_factor):
        self.postcode = str(postcode)
        self.suburb = str(suburb)
        self.is_melb = bool(is_melb)
        self.dist_factor = float(dist_factor)

    def is_valid_zone(self):
        return self.is_melb


class Parcel:
    """The freight item entrusted for transport."""
    def __init__(self, parcel_id, weight_kg, size_cat, special_handling=False):
        valid_sizes = ["Document/Satchel", "Small Box", "Bulky/Crate"]
        if size_cat not in valid_sizes:
            raise ValueError(f"Size must be one of: {valid_sizes}")
        if float(weight_kg) <= 0:
            raise ValueError("Weight must be greater than 0 kg.")

        self.parcel_id = str(parcel_id)
        self.weight_kg = float(weight_kg)
        self.size_cat = str(size_cat)
        self.special_handling = bool(special_handling)

    def get_category_rate(self):
        rates = {"Document/Satchel": 5.0, "Small Box": 10.0, "Bulky/Crate": 18.0}
        return rates.get(self.size_cat, 5.0)

    def get_handling_fee(self):
        return 7.50 if self.special_handling else 0.0


class Quote:
    """Cost estimate issued to customer (Assignment 1 Task 2)."""
    def __init__(self, quote_id, total_cost, pickup_hrs, delivery_hrs):
        self.quote_id = str(quote_id)
        self.total_cost = round(float(total_cost), 2)
        self.pickup_hrs = int(pickup_hrs)
        self.delivery_hrs = int(delivery_hrs)
        self.is_accepted = False

    def accept(self):
        self.is_accepted = True

    def to_dict(self):
        return {
            "quote_id": self.quote_id,
            "total_cost": self.total_cost,
            "pickup_window": f"{self.pickup_hrs} hr(s)",
            "delivery_window": f"{self.delivery_hrs} hr(s)",
            "is_accepted": self.is_accepted
        }


# Strategy Pattern for Payments (Designed by Member 2/3 in A2)
class PaymentMethod:
    def process(self, amount):
        raise NotImplementedError


class CardPayment(PaymentMethod):
    def process(self, amount):
        return f"Prepaid ${amount:.2f} online via Credit/Debit Card."


class CashPayment(PaymentMethod):
    def process(self, amount):
        return f"Collected ${amount:.2f} in cash on pickup."


class Payment:
    """Financial settlement associated with an order."""
    def __init__(self, payment_id, amount, payment_method):
        self.payment_id = str(payment_id)
        self.amount = float(amount)
        self.payment_method = payment_method
        self.status = "Pending"
        self.timestamp = None

    def execute(self):
        self.status = "Received"
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.payment_method.process(self.amount)


class DeliveryRequest:
    """
    Central domain entity coordinating the delivery lifecycle.
    Statuses: Requested -> Quoted -> Accepted -> In_Transit -> Delivered / Cancelled
    """
    def __init__(self, req_id, cust_id, pickup_addr, dest_addr, parcel, pickup_zone, dest_zone):
        self.req_id = str(req_id)
        self.cust_id = str(cust_id)
        self.pickup_addr = str(pickup_addr)
        self.dest_addr = str(dest_addr)
        self.parcel = parcel
        self.pickup_zone = pickup_zone
        self.dest_zone = dest_zone

        self.quote = None
        self.payment = None
        self.assigned_driver_id = None
        self.status = "Requested"
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def attach_quote(self, quote):
        self.quote = quote
        self.status = "Quoted"

    def confirm_booking(self, payment_method):
        if self.quote:
            self.quote.accept()
            self.payment = Payment(f"PAY-{self.req_id}", self.quote.total_cost, payment_method)
            msg = self.payment.execute()
            self.status = "Accepted"
            return msg
        return None

    def assign_driver(self, driver_id):
        self.assigned_driver_id = str(driver_id)
        self.status = "In_Transit"

    def cancel(self):
        self.status = "Cancelled"

    def to_dict(self):
        return {
            "req_id": self.req_id,
            "cust_id": self.cust_id,
            "pickup_addr": self.pickup_addr,
            "dest_addr": self.dest_addr,
            "status": self.status,
            "payment_status": self.payment.status if self.payment else "Unpaid",
            "driver_id": self.assigned_driver_id,
            "parcel": {
                "id": self.parcel.parcel_id,
                "weight": self.parcel.weight_kg,
                "size": self.parcel.size_cat,
                "special": self.parcel.special_handling
            },
            "quote": self.quote.to_dict() if self.quote else None,
            "created_at": self.created_at
        }