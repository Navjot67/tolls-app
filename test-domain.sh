#!/bin/bash
# Quick domain test script

echo "=========================================="
echo "Domain Test: www.tlcezpass.com"
echo "=========================================="
echo ""

echo "1. Testing Gunicorn (localhost:5000)..."
if curl -s http://localhost:5000 > /dev/null; then
    echo "   ✓ Gunicorn is running and responding"
    curl -s http://localhost:5000 | head -2
else
    echo "   ✗ Gunicorn not responding"
fi

echo ""
echo "2. Testing /user endpoint..."
if curl -s http://localhost:5000/user > /dev/null; then
    echo "   ✓ User endpoint accessible"
else
    echo "   ✗ User endpoint not accessible"
fi

echo ""
echo "3. Checking services..."
if launchctl list com.toll-app &>/dev/null; then
    echo "   ✓ Gunicorn service is running"
    launchctl list com.toll-app | grep PID
else
    echo "   ✗ Gunicorn service not found"
fi

if brew services list | grep -q "nginx.*started"; then
    echo "   ✓ Nginx is running"
else
    echo "   ✗ Nginx not running"
fi

echo ""
echo "4. Testing DNS..."
DNS_RESULT=$(nslookup www.tlcezpass.com 2>&1)
if echo "$DNS_RESULT" | grep -q "Address"; then
    echo "   ✓ DNS is resolving:"
    echo "$DNS_RESULT" | grep "Address" | tail -1
else
    echo "   ⚠ DNS not resolving (may need configuration)"
fi

echo ""
echo "5. Testing domain connection..."
if curl -s --max-time 5 http://www.tlcezpass.com > /dev/null 2>&1; then
    echo "   ✓ Domain is accessible!"
    curl -I http://www.tlcezpass.com 2>&1 | head -5
else
    echo "   ⚠ Domain not accessible (check DNS or wait for propagation)"
fi

echo ""
echo "6. Nginx configuration..."
if nginx -t 2>&1 | grep -q "successful"; then
    echo "   ✓ Nginx config is valid"
else
    echo "   ✗ Nginx config has errors"
    nginx -t 2>&1
fi

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="

