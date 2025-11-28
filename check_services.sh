#!/bin/bash
# Script to check status of all toll dashboard services

echo "============================================================"
echo "TOLL DASHBOARD SERVICES STATUS"
echo "============================================================"

# Check Email Checker
echo ""
echo "📧 Email Checker Service:"
EMAIL_CHECKER_LOADED=$(launchctl list 2>/dev/null | grep -q "com.toll.email-checker" && echo "1" || echo "0")
EMAIL_CHECKER_RUNNING=$(ps aux 2>/dev/null | grep -q "[e]mail_checker_worker.py" && echo "1" || echo "0")

if [ "$EMAIL_CHECKER_LOADED" -gt 0 ]; then
    echo "   Status: ✅ Loaded in launchd"
    if [ "$EMAIL_CHECKER_RUNNING" -gt 0 ]; then
        echo "   Process: ✅ Running"
    else
        echo "   Process: ⚠️  Not running (will auto-restart)"
    fi
else
    echo "   Status: ❌ Not loaded"
fi

# Check Auto-Fetch
echo ""
echo "🔄 Auto-Fetch Service:"
AUTOFETCH_LOADED=$(launchctl list 2>/dev/null | grep -q "com.toll-dashboard-autofetch" && echo "1" || echo "0")
AUTOFETCH_RUNNING=$(ps aux 2>/dev/null | grep -q "[a]uto_fetch.py" && echo "1" || echo "0")

if [ "$AUTOFETCH_LOADED" -gt 0 ]; then
    echo "   Status: ✅ Loaded in launchd"
    if [ "$AUTOFETCH_RUNNING" -gt 0 ]; then
        echo "   Process: ✅ Currently running"
    else
        echo "   Process: ⚠️  Scheduled (runs every 3 hours)"
    fi
else
    echo "   Status: ❌ Not loaded"
fi

# Check Server
echo ""
echo "🚀 Server (Gunicorn):"
SERVER_LOADED=$(launchctl list 2>/dev/null | grep -q "com.toll-dashboard-server" && echo "1" || echo "0")
SERVER_RUNNING=$(ps aux 2>/dev/null | grep -q "[g]unicorn.*app:app" && echo "1" || echo "0")

if [ "$SERVER_LOADED" -gt 0 ]; then
    echo "   Status: ✅ Loaded in launchd"
    if [ "$SERVER_RUNNING" -gt 0 ]; then
        echo "   Process: ✅ Running"
        PORT=$(lsof -ti:5000 2>/dev/null || echo "")
        if [ -n "$PORT" ]; then
            echo "   Port 5000: ✅ Active"
        else
            echo "   Port 5000: ⚠️  Not listening"
        fi
    else
        echo "   Process: ❌ Not running (will auto-restart)"
    fi
else
    echo "   Status: ❌ Not loaded in launchd"
    if [ "$SERVER_RUNNING" -gt 0 ]; then
        echo "   Process: ⚠️  Running but not managed by launchd"
    else
        echo "   Process: ❌ Not running"
    fi
fi

echo ""
echo "============================================================"
echo "To view logs:"
echo "  - Email Checker: tail -f logs/email_checker_stdout.log"
echo "  - Auto-Fetch: tail -f launchd_stdout.log"
echo "  - Server: tail -f logs/gunicorn-stdout.log"
echo "============================================================"

