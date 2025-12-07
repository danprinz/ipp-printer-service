class IPPPrinterCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
  }

  configChanged(newConfig) {
    const event = new Event("config-changed", {
      bubbles: true,
      composed: true,
    });
    event.detail = { config: newConfig };
    this.dispatchEvent(event);
  }

  set hass(hass) {
    this._hass = hass;
    if (this._hass && !this._initialized) {
      this._initialized = true;
      this._render();
    }
  }

  _render() {
    if (!this._hass) return;
    
    // Get all sensor entities provided by ipp_printer_service
    const entities = Object.keys(this._hass.states).filter((eid) => {
        // Filter for our domain and specifically printer entities if identifiable
        // We look for domain "sensor" but ideally we should match integration
        // Since we can't easily filter by integration in frontend without more data,
        // we'll offer a text input or a dropdown of all sensors.
        // Better: IPP Printer Service actually registers sensors. 
        // Let's filter by entities that start with 'sensor.' and have 'ipp' in them 
        // OR better yet, just a simple entity picker.
        return eid.includes('ipp_printer') || eid.includes('ipp');
    });

    this.innerHTML = `
      <div class="card-config">
        <div class="option">
          <ha-entity-picker
            label="Printer Entity"
            .hass=${this._hass}
            .value=${this._config.entity}
            .includeDomains=${['sensor']}
            @value-changed=${this._valueChanged}
          ></ha-entity-picker>
        </div>
      </div>
    `;
    
    // Bind event
    const picker = this.querySelector("ha-entity-picker");
    if(picker) {
        picker.addEventListener("value-changed", (ev) => this._valueChanged(ev));
    }
  }

  _valueChanged(ev) {
    if (!this._config || !this._hass) return;
    const target = ev.target;
    if (this._config.entity === target.value) return;
    if (target.value) {
      this._config = {
        ...this._config,
        entity: target.value,
      };
      this.configChanged(this._config);
    }
  }
}

customElements.define("ipp-printer-card-editor", IPPPrinterCardEditor);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "ipp-printer-card",
  name: "IPP Printer Card",
  preview: true, // Optional: enables preview in the picker
  description: "A card to upload and print PDF files via IPP",
});
