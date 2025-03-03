# generate_inventory.py
import json

inventory = {
    "cisco_devices": {
        "hosts": {f"cisco{i}": {"ansible_host": f"172.22.0.{i}"} for i in range(2, 246)},
        "vars": {
            "ansible_user": "admin",
            "ansible_password": "cisco",
            "ansible_connection": "network_cli",
            "ansible_network_os": "ios"
        }
    }
}

print(json.dumps(inventory, indent=2))


# python3 generate_inventory.py > inventory.json
# ansible-inventory -i inventory.json --list
