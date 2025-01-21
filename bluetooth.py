import bluetooth

# Define the target device's MAC address and port
address = "XX:XX:XX:XX:XX:XX"  # Replace with the ESP32-C6 Bluetooth device's MAC address
port = 1

# Create a Bluetooth socket and connect
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((address, port))

# Sending data
data_to_send = "Hello ESP32-C6 via Bluetooth"
sock.send(data_to_send)

# Close the socket
sock.close()
