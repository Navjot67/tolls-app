#!/bin/bash
# Quick Test Script - Run this manually in your terminal

echo "=========================================="
echo "Quick Domain Test"
echo "=========================================="
echo ""

echo "1. Test Gunicorn (should return HTML):"
curl http://localhost:5000 | head -5
echo ""

echo "2. Test User App (should return HTML):"
curl http://localhost:5000/user | head -5
echo ""

echo "3. Check Gunicorn service:"
launchctl list com.toll-app | grep -E "(PID|LastExitStatus)"
echo ""

echo "4. Check Nginx:"
brew services list | grep nginx
echo ""

echo "5. Test DNS:"
nslookup www.tlcezpass.com
echo ""

echo "6. Test Domain:"
curl -I http://www.tlcezpass.com
echo ""

echo "7. Nginx Config Test:"
nginx -t
echo ""

echo "=========================================="
echo "If localhost works but domain doesn't:"
echo "→ DNS needs to be configured"
echo "→ Or DNS hasn't propagated yet"
echo "=========================================="

