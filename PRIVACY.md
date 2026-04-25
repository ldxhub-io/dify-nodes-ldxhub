## Privacy Policy

This document describes how the LDX hub plugin handles your data.

### What This Plugin Does

The LDX hub plugin acts as a thin client between Dify and the LDX hub API. The plugin itself does **not** persist any user data. All processing happens on LDX hub's servers and the AI providers it integrates with.

### Data You Provide

When you use this plugin, the following data is transmitted to LDX hub servers (`https://gw.ldxhub.io` or a Base URL you configure):

- **Files you upload** (XLIFF documents for RefineLoop, JSONL files for StructFlow)
- **Text content** you specify (system prompts, custom instructions, example outputs)
- **Configuration parameters** (model selection, language codes, etc.)
- **Your API key** is sent in the `Authorization` header for authentication

### Data Storage on LDX hub Servers

- Uploaded files and processing results are temporarily stored on LDX hub servers
- Files have an `expires_at` timestamp and are automatically deleted after that period

### Data Sent to Third-Party AI Providers

LDX hub forwards your content to AI model providers based on the model you select. The providers currently include:

- OpenAI
- Microsoft (Azure OpenAI)
- Google
- Anthropic
- Amazon (AWS Bedrock)
- xAI

The available models change over time. The current list of models is exposed by the LDX hub API and shown in the model selection dropdown of each tool. When you select a model, your data is forwarded to the corresponding provider listed above. Each provider has its own privacy and data handling policies; please review the policy of the provider corresponding to your selected model.

### Credentials Handling

- Your API key is encrypted by Dify using PKCS1_OAEP and stored within your Dify workspace
- The plugin never logs your API key
- The plugin never transmits your API key anywhere other than the configured LDX hub Base URL

### Webhook URLs

If you specify a `webhook_url` parameter, LDX hub will (in the future) send job completion notifications to that URL. The plugin does not control the destination — it is entirely your responsibility to provide a URL you trust. Note that server-side webhook delivery is currently being implemented and is not active yet.

### Telemetry

This plugin does not send telemetry, analytics, or usage data to anyone other than the LDX hub API endpoint you configure.

### Contact

For questions about LDX hub itself or its data handling, see https://ldxlab.io
