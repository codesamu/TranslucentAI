from bleak import BleakClient

# BLE address of the ESP32-C6 (replace with your device's address)
esp32_address = "XX:XX:XX:XX:XX:XX"
characteristic_uuid = "abcd1234-5678-1234-5678-123456789abc"  # Match UUID in ESP32 code

async def send_text(text):
    async with BleakClient(esp32_address) as client:
        if client.is_connected:
            print(f"Connected to {esp32_address}")
            await client.write_gatt_char(characteristic_uuid, text.encode('utf-8'))
            print(f"Sent: {text}")

# Example usage
import asyncio
text = input("Enter text to send: ")
asyncio.run(send_text(text))
