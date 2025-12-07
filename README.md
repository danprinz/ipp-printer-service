# IPP Printer Service

This integration provides extended IPP printing capabilities, including a simulation mode for testing.

## Installation

### HACS

1. Open HACS.
2. Go to "Integrations".
3. Click the 3 dots in the top right corner and select "Custom repositories".
4. Add the URL of this repository (https://github.com/danprinz/ipp-printer-service).
5. Select "Integration" as the category.
6. Click "Add".
7. Find "IPP Printer Service" in the list and install it.
8. Restart Home Assistant.

### Manual

1. Copy the `custom_components/ipp_printer_service` folder to your `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

This integration supports config flow. Go to Settings -> Devices & Services -> Add Integration and search for "IPP Printer Service".

## Host Configuration

When configuring the integration, the host address should be provided without the protocol (e.g., `your-printer-ip` or `your-printer-hostname`). After successful connection validation, you will be presented with a list of available printers to choose from.

## Frontend Card

This integration includes a custom Lovelace card for printing PDFs.

To use it:

1.  **Add Resource**:
    *   Go to **Settings** -> **Dashboards** -> **3 dots** (top right) -> **Resources**.
    *   Click **Add Resource**.
    *   **URL**: `/hacsfiles/ipp_printer_service/ipp-printer-card.js`
    *   **Resource type**: JavaScript Module
2.  **Add Card to Dashboard**:
    *   Edit your dashboard.
    *   Click **Add Card**.
    *   Search for **IPP Printer Card** (if the visual editor is active) or use the YAML configuration below:

```yaml
type: custom:ipp-printer-card
entity: ipp.your_printer_name
```


