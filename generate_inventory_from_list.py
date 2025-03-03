import json

# Read IPs from a file
with open("ip_list.txt", "r") as file:
    ip_list = [line.strip() for line in file if line.strip()]  # Remove empty lines

# Generate inventory
inventory = {
    "cisco_devices": {
        "hosts": {f"cisco{i+1}": {"ansible_host": ip} for i, ip in enumerate(ip_list)},
        "vars": {
            "ansible_user": "admin",
            "ansible_password": "C1sco12345",
            "ansible_connection": "network_cli",
            "ansible_network_os": "ios"
        }
    }
}

# Print the inventory as JSON
print(json.dumps(inventory, indent=2))



#  python3 generate_inventory_from_list.py > inventory.json
# ansible-inventory -i inventory.json --list
