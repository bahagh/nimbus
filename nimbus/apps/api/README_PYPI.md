# Nimbus Analytics

**🚀 Open-source, self-hosted alternative to Segment & Mixpanel**

Save 90% on analytics costs. Own your data. Full customization.

## ⚠️ Beta Release

**Status:** Backend API is production-ready ✅ | Dashboard UI coming Q1 2026 🚧

## Quick Start

```bash
# Install
pip install nimbus-analytics

# Run with Docker
docker-compose up -d

# Or start manually
uvicorn nimbus.main:app --host 0.0.0.0 --port 8000
```

## Features

- ⚡ **Fast**: 10,000+ events/second
- 🔐 **Secure**: JWT + HMAC authentication
- 📊 **Real-time**: WebSocket streaming
- 🎯 **Multi-tenant**: Project isolation
- 🐳 **Docker**: One-command deployment
- 🧪 **Tested**: 100% pass rate
- 📚 **Documented**: Interactive Swagger UI

## Use Cases

Perfect for:
- Replacing expensive Segment/Mixpanel subscriptions ($500-$5000/month → $50/month)
- Companies with data privacy requirements (HIPAA, GDPR, SOC2)
- Teams needing self-hosted analytics
- Developers wanting full customization

## Documentation

📖 Full documentation: https://github.com/bahagh/nimbus

## Cost Comparison

| Monthly Events | Segment | Mixpanel | Nimbus |
|----------------|---------|----------|--------|
| 10M | ~$500 | ~$1,000 | **$50** |
| 100M | ~$2,000 | ~$5,000 | **$200** |

## Links

- 🏠 Homepage: https://github.com/bahagh/nimbus
- 📚 Documentation: https://github.com/bahagh/nimbus#readme
- 🐛 Issues: https://github.com/bahagh/nimbus/issues
- 💬 Discussions: https://github.com/bahagh/nimbus/discussions

## License

MIT License - see LICENSE file
