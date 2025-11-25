#!/bin/bash
# Check IP addresses to diagnose the setup

echo "=========================================="
echo "IP Address Check"
echo "=========================================="
echo ""

echo "1. Your Public IP:"
PUBLIC_IP=$(curl -s ifconfig.me)
echo "   $PUBLIC_IP"
echo ""

echo "2. DNS points to:"
echo "   74.68.113.248"
echo ""

echo "3. Your Local IPs:"
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print "   " $2}'
echo ""

echo "=========================================="
echo "Analysis:"
echo "=========================================="

if [ "$PUBLIC_IP" = "74.68.113.248" ]; then
    echo "✅ Public IP matches DNS!"
    echo "   → Need to configure port forwarding or firewall"
elif [ -z "$PUBLIC_IP" ]; then
    echo "⚠️  Could not detect public IP"
    echo "   → May be behind NAT/firewall"
else
    echo "⚠️  Public IP ($PUBLIC_IP) doesn't match DNS (74.68.113.248)"
    echo "   → DNS points to a different server"
    echo "   → Options:"
    echo "     1. Deploy to server at 74.68.113.248"
    echo "     2. Update DNS to point to $PUBLIC_IP"
fi

echo ""

