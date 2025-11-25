# Testing Domain: www.tlcezpass.com

## What to Expect

### If DNS is NOT configured yet:
- `nslookup www.tlcezpass.com` → Will fail or show no IP
- `curl http://www.tlcezpass.com` → Connection timeout or DNS error

### If DNS IS configured:
- `nslookup www.tlcezpass.com` → Should show your server IP
- `curl http://www.tlcezpass.com` → Should return HTML content

## Current Status Check

### 1. Check Services Running

```bash
# Check nginx
brew services list | grep nginx

# Check Gunicorn
launchctl list com.toll-app

# Test localhost
curl http://localhost:5000
```

### 2. Check Nginx Configuration

```bash
# Test config
nginx -t

# View domain config
cat /opt/homebrew/etc/nginx/servers/toll-app.conf
```

### 3. Test DNS Resolution

```bash
# Method 1: nslookup
nslookup www.tlcezpass.com

# Method 2: dig
dig www.tlcezpass.com

# Method 3: host
host www.tlcezpass.com
```

## Troubleshooting

### Issue: DNS not resolving

**Solution**: Configure DNS A records in your domain registrar:
- `www.tlcezpass.com` → Your Server IP
- `tlcezpass.com` → Your Server IP

**Find your server IP:**
```bash
curl ifconfig.me
```

### Issue: DNS resolves but connection fails

**Check:**
1. Is nginx running? `brew services list | grep nginx`
2. Is Gunicorn running? `launchctl list com.toll-app`
3. Test localhost: `curl http://localhost:5000`

### Issue: Connection timeout

**Possible causes:**
1. Firewall blocking port 80
2. Server not publicly accessible
3. Wrong IP in DNS records

**Test localhost first:**
```bash
curl http://localhost:5000
curl http://localhost:5000/user
```

If localhost works but domain doesn't, it's a DNS/routing issue.

## Quick Test Setup

To test locally before DNS is configured:

1. **Add to /etc/hosts:**
   ```bash
   sudo sh -c 'echo "127.0.0.1 www.tlcezpass.com" >> /etc/hosts'
   ```

2. **Test:**
   ```bash
   curl http://www.tlcezpass.com
   curl http://www.tlcezpass.com/user
   ```

3. **Remove from /etc/hosts when done:**
   ```bash
   sudo nano /etc/hosts
   # Remove the line: 127.0.0.1 www.tlcezpass.com
   ```

## Expected Results

### When Everything Works:

**DNS Lookup:**
```
Server:     8.8.8.8
Address:    8.8.8.8#53

Non-authoritative answer:
Name:   www.tlcezpass.com
Address: YOUR_SERVER_IP
```

**HTTP Response:**
```bash
$ curl -I http://www.tlcezpass.com
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html
...
```

## Next Steps

1. ✅ Verify DNS is configured in registrar
2. ✅ Wait for DNS propagation (5-60 minutes)
3. ✅ Test with nslookup/dig
4. ✅ Test with curl
5. ✅ Open in browser: http://www.tlcezpass.com

