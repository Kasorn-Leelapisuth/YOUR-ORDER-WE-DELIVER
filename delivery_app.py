"""
delivery_app.py: Presentation Layer executing the 4 verification scenarios.
"""

from subsystem_controllers import DispatchManager, OrderCoordinator, RosterManager


class DeliveryApp:
    def __init__(self):
        # Section 7 Bootstrapping Sequence: Initialize coordinators and controllers
        self.order_coordinator = OrderCoordinator()
        self.roster_manager = RosterManager()
        self.dispatch_manager = DispatchManager(self.roster_manager, self.order_coordinator)

    def display_menu(self):
        print("\n" + "=" * 58)
        print("   YOUR ORDER WE DELIVER - DISPATCH & ORDER SYSTEM")
        print("=" * 58)
        print("1. Log Delivery Request & Calculate Quote")
        print("2. Confirm Booking & Process Payment")
        print("3. Cancel Delivery Job ")
        print("4. View Driver Roster & Shift Availability")
        print("5. Allocate & Dispatch Driver to Order ")
        print("6. Exit")
        print("=" * 58)

    def run(self):
        while True:
            self.display_menu()
            choice = input("\nSelect Option (1-6): ").strip()

            if choice == "1":
                self.ui_log_delivery_request()
            elif choice == "2":
                self.ui_confirm_booking()
            elif choice == "3":
                self.ui_cancel_order()
            elif choice == "4":
                self.ui_view_roster()
            elif choice == "5":
                self.ui_dispatch_driver()
            elif choice == "6":
                print("\nShutting down. Operational records saved.")
                break
            else:
                print("\n[ERROR] Invalid option. Enter a number between 1 and 6.")

    def ui_log_delivery_request(self):
        print("\n--- [Scenario 1] Log Delivery Request ---")
        try:
            cust_id = input("Customer ID: ").strip()
            pickup_addr = input("Pickup Street Address: ").strip()
            p_postcode = input("Pickup Postcode (e.g. 3000, 3122): ").strip()
            dest_addr = input("Destination Street Address: ").strip()
            d_postcode = input("Destination Postcode (e.g. 3000, 3122): ").strip()
            weight_str = input("Parcel Weight (kg): ").strip()
            
            print("Size Options: 1) Document/Satchel  2) Small Box  3) Bulky/Crate")
            size_choice = input("Select Size (1-3): ").strip()
            size_map = {"1": "Document/Satchel", "2": "Small Box", "3": "Bulky/Crate"}
            size_cat = size_map.get(size_choice, "Small Box")
            
            special = input("Fragile / Special Handling? (y/n): ").strip().lower() == "y"

            try:
                weight = float(weight_str)
            except ValueError:
                raise ValueError("Weight must be a valid number.")

            order = self.order_coordinator.log_delivery_request(
                cust_id=cust_id,
                pickup_addr=pickup_addr,
                p_postcode=p_postcode,
                dest_addr=dest_addr,
                d_postcode=d_postcode,
                weight=weight,
                size=size_cat,
                special=special
            )

            print("\n" + "-" * 45)
            print(f"[SUCCESS] Order Created: {order.req_id}")
            print(f"Quoted Fare       : ${order.quote.total_cost:.2f}")
            print(f"Estimated Pickup  : Within {order.quote.pickup_hrs} hr(s)")
            print(f"Estimated Delivery: Within {order.quote.delivery_hrs} hr(s)")
            print(f"Current Status    : {order.status}")
            print("-" * 45)

        except ValueError as err:
            print(f"\n[VALIDATION ERROR] {err}")

    def ui_confirm_booking(self):
        print("\n--- [Scenario 2] Confirm Booking & Process Payment ---")
        req_id = input("Enter Request ID to confirm: ").strip()
        pay_type = input("Payment Method: 1) Prepaid Card Online  2) Cash on Pickup (1 or 2): ").strip()
        method_str = "card" if pay_type == "1" else "cash"

        success, msg = self.order_coordinator.confirm_customer_booking(req_id, method_str)
        if success:
            print(f"\n[SUCCESS] {msg}")
            print(f"Status updated to: {self.order_coordinator.requests[req_id].status}")
        else:
            print(f"\n[ERROR] {msg}")

    def ui_cancel_order(self):
        print("\n--- [Scenario 3] Cancel Delivery Job (Change of Mind) ---")
        req_id = input("Enter Request ID to cancel: ").strip()
        if self.order_coordinator.cancel_delivery_request(req_id):
            print(f"\n[SUCCESS] Order {req_id} marked as Cancelled.")
        else:
            print(f"\n[ERROR] Order ID '{req_id}' not found.")

    def ui_view_roster(self):
        print("\n--- Active Fleet Roster ---")
        print(f"{'Driver ID':<10} | {'Name':<15} | {'Zone':<6} | {'Availability':<14} | {'Current Job'}")
        print("-" * 65)
        for d in self.roster_manager.drivers.values():
            status = "AVAILABLE" if d.is_available else "OFF-DUTY/BUSY"
            job = d.current_job_id if d.current_job_id else "-"
            print(f"{d.driver_id:<10} | {d.name:<15} | {d.operating_zone:<6} | {status:<14} | {job}")

    def ui_dispatch_driver(self):
        print("\n--- [Scenario 4] Allocate & Dispatch Driver ---")
        req_id = input("Enter Accepted Request ID to dispatch: ").strip()
        success, msg = self.dispatch_manager.allocate_driver(req_id)
        if success:
            print(f"\n[SUCCESS] {msg}")
            print("Status updated to: In_Transit.")
        else:
            print(f"\n[DISPATCH FAILED] {msg}")


if __name__ == "__main__":
    app = DeliveryApp()
    app.run()