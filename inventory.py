import configparser

# Function to read the IP addresses from ip_list.txt
def read_ip_list(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Define the path to the IP list text file
ip_list_file = 'ip_list.txt'

# Read the list of IP addresses from the file
ips = read_ip_list(ip_list_file)

# Define common username and password
ansible_user = 'admin'
ansible_ssh_pass = 'password'  # Same password for all devices

# Create a ConfigParser object to handle the .ini file format
config = configparser.ConfigParser()

# Add the [defaults] section for Ansible configuration
config['defaults'] = {
    # 'ansible_connection': 'network_cli',
    # 'ansible_network_os': 'nxos',
}

# Add devices to the corresponding group
group = 'cisco_devices'  # Group for Cisco devices
if group not in config:
    config[group] = {}

# Add each IP address as a host under the group
for ip in ips:
    # Using the IP address as the hostname (you can modify this to a different format if needed)
    config[group][ip] = f"{ip} ansible_user={ansible_user} ansible_ssh_pass={ansible_ssh_pass}"

# Write the inventory data to a file
with open('inventory.ini', 'w') as configfile:
    config.write(configfile)
