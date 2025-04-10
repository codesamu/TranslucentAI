#include <lvgl.h>
#include <TFT_eSPI.h>
#include "BluetoothSerial.h"

// Initialize TFT display
TFT_eSPI tft = TFT_eSPI();

// LVGL draw buffer
static lv_disp_draw_buf_t draw_buf;
static lv_color_t buf[TFT_WIDTH * 10]; // Adjust for display size

// Bluetooth object
BluetoothSerial SerialBT;

// LVGL Display Driver Callback
void my_disp_flush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p) {
  tft.startWrite();
  tft.setAddrWindow(area->x1, area->y1, area->x2 - area->x1 + 1, area->y2 - area->y1 + 1);
  tft.pushColors((uint16_t *)&color_p->full, (area->x2 - area->x1 + 1) * (area->y2 - area->y1 + 1), true);
  tft.endWrite();
  lv_disp_flush_ready(disp);
}

// Create a styled label for the text
lv_obj_t *label;
void createStyledText(const char *text) {
  // If label already exists, just update text
  if (label) {
    lv_label_set_text(label, text);
    return;
  }

  // Create a new style
  static lv_style_t style;
  lv_style_init(&style);
  lv_style_set_text_color(&style, lv_color_hex(0xFFFFFF)); // White text
  lv_style_set_text_font(&style, &lv_font_montserrat_20);  // Font size 20
  lv_style_set_text_align(&style, LV_TEXT_ALIGN_CENTER);   // Centered text

  // Create the label and apply the style
  label = lv_label_create(lv_scr_act());
  lv_obj_add_style(label, &style, 0);
  lv_label_set_text(label, text);                         // Set initial text
  lv_obj_align(label, LV_ALIGN_CENTER, 0, 0);             // Center align
}

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);

  // Initialize Bluetooth
  SerialBT.begin("ESP32-LVGL");
  Serial.println("Bluetooth started. Waiting for messages...");

  // Initialize the TFT display
  tft.begin();
  tft.setRotation(1); // Adjust rotation if needed

  // Initialize LVGL
  lv_init();

  // Initialize the LVGL display buffer
  lv_disp_draw_buf_init(&draw_buf, buf, NULL, TFT_WIDTH * 10);

  // Register the display driver with LVGL
  static lv_disp_drv_t disp_drv;
  lv_disp_drv_init(&disp_drv);
  disp_drv.hor_res = TFT_WIDTH;
  disp_drv.ver_res = TFT_HEIGHT;
  disp_drv.flush_cb = my_disp_flush;
  disp_drv.draw_buf = &draw_buf;
  lv_disp_drv_register(&disp_drv);

  // Create an initial styled label
  createStyledText("Waiting for message...");
}

void loop() {
  // Handle LVGL tasks
  lv_timer_handler();
  delay(5);

  // Check if Bluetooth data is available
  if (SerialBT.available()) {
    String receivedText = SerialBT.readString(); // Read incoming Bluetooth data
    Serial.println("Received: " + receivedText); // Log received text
    createStyledText(receivedText.c_str());      // Display the received text
  }
}
