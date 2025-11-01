# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **baha.ghrissi@esprit.tn**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information in your report:

- Type of vulnerability
- Full paths of source file(s) related to the manifestation of the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine the affected versions
2. Audit code to find any similar problems
3. Prepare fixes for all supported releases
4. Release patches as soon as possible

## Security Best Practices

When deploying Nimbus in production, follow these security best practices:

### 1. Environment Variables

Never commit sensitive data to your repository:

```bash
# Use strong, random secrets
NIMBUS_JWT_SECRET_KEY=$(openssl rand -hex 32)
NIMBUS_HMAC_SECRET_KEY=$(openssl rand -hex 32)

# Use secure database passwords
NIMBUS_DB_PASSWORD=$(openssl rand -base64 32)
```

### 2. HTTPS/TLS

Always use HTTPS in production:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

### 3. Rate Limiting

Enable rate limiting to prevent abuse:

```python
NIMBUS_RATE_LIMIT_ENABLED=true
NIMBUS_RATE_LIMIT_PER_MINUTE=100
```

### 4. Database Security

- Use strong passwords for database users
- Restrict database access to application IPs only
- Enable SSL/TLS for database connections
- Regular security updates for PostgreSQL

### 5. API Key Management

- Rotate API keys periodically
- Use separate keys for different environments
- Never log or expose API secrets
- Implement key expiration policies

### 6. CORS Configuration

Restrict CORS to trusted origins only:

```python
NIMBUS_CORS_ORIGINS=["https://yourdomain.com"]
```

### 7. Dependency Security

Keep dependencies updated:

```bash
cd apps/api
poetry update
poetry show --outdated
```

### 8. Container Security

- Use non-root user in Docker containers
- Scan images for vulnerabilities
- Keep base images updated
- Use minimal base images (alpine, distroless)

### 9. Secrets Management

Use proper secrets management:

- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager
- HashiCorp Vault
- Kubernetes Secrets

### 10. Monitoring

Enable security monitoring:

- Log all authentication attempts
- Monitor for unusual traffic patterns
- Set up alerts for failed login attempts
- Track API key usage patterns

## Known Security Considerations

### JWT Tokens

- Tokens expire after the configured time (default: 30 minutes)
- Refresh tokens should be stored securely
- Consider implementing token blacklisting for logout

### HMAC Signatures

- HMAC signatures prevent request tampering
- Signatures are tied to request body
- Replay protection via idempotency keys

### Password Storage

- Passwords hashed with bcrypt (cost factor 12)
- No plaintext passwords stored anywhere
- Password reset requires email verification

## Security Audit Trail

| Date       | Version | Issue                          | Severity | Status   |
|------------|---------|--------------------------------|----------|----------|
| 2025-11-01 | 0.1.0   | Initial security review        | N/A      | Complete |

## Contact

For security concerns, contact: **baha.ghrissi@esprit.tn**

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Guide](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
