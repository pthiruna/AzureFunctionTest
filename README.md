# Temp Alerts

An Azure Function that fetches the current temperature for Cary, NC (zip code 27519) and sends it as a WhatsApp message.

## How it works

1. An HTTP request triggers the Azure Function
2. The function calls [Open-Meteo](https://open-meteo.com/) to get the current temperature in Fahrenheit for zip code 27519
3. The temperature is sent as a WhatsApp message via [CallMeBot](https://www.callmebot.com/)

## Project structure

```
├── temp_alerts.py        # Azure Function app (main entry point)
├── test_local.py         # Local test script
├── run.sh                # Shell script to run the local test
├── host.json             # Azure Functions host configuration
├── local.settings.json   # Local environment settings (not committed)
└── requirements.txt      # Python dependencies
```

## Prerequisites

- Python 3.9+
- [Azure Functions Core Tools v4](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- A [CallMeBot](https://www.callmebot.com/blog/free-api-whatsapp-messages/) API key

### Getting a CallMeBot API key (one-time setup)

1. Add **+34 644 65 21 91** to your WhatsApp contacts
2. Send it the message: `I allow callmebot to send me messages`
3. You will receive an API key in reply — save it

## Local development

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure local settings

Edit `local.settings.json` and set your CallMeBot API key:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "PYTHON_SCRIPT_FILE": "temp_alerts.py",
    "CALLMEBOT_API_KEY": "your-callmebot-api-key"
  }
}
```

### 3. Run the test script

```bash
./run.sh
```

Or directly:

```bash
python3 test_local.py
```

### 4. Run as a local Azure Function

```bash
func start
```

Then trigger it:

```bash
curl http://localhost:7071/api/weather-whatsapp
```

## Deploy to Azure

```bash
# Login
az login

# Create resources
az group create --name rg-temp-alerts --location eastus
az storage account create --name tempalertsstorage --location eastus \
  --resource-group rg-temp-alerts --sku Standard_LRS
az functionapp create --resource-group rg-temp-alerts \
  --consumption-plan-location eastus \
  --runtime python --runtime-version 3.11 --functions-version 4 \
  --name temp-alerts-fn --storage-account tempalertsstorage --os-type linux

# Set app settings
az functionapp config appsettings set \
  --name temp-alerts-fn \
  --resource-group rg-temp-alerts \
  --settings PYTHON_SCRIPT_FILE="temp_alerts.py" CALLMEBOT_API_KEY="your-callmebot-api-key"

# Deploy
func azure functionapp publish temp-alerts-fn
```

Once deployed, invoke it at:

```
https://temp-alerts-fn.azurewebsites.net/api/weather-whatsapp
```

## APIs used

| API | Purpose | Cost |
|-----|---------|------|
| [Open-Meteo](https://open-meteo.com/) | Weather data | Free, no key required |
| [CallMeBot](https://www.callmebot.com/) | WhatsApp notifications | Free, no limits |
