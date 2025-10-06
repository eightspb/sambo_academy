#!/bin/bash

# Statistics
sed -n '/<script>$/,/^    <\/script>$/p' templates/statistics.html | sed '1d;$d' > static/js/pages/statistics.js
echo "/**" | cat - static/js/pages/statistics.js > temp && mv temp static/js/pages/statistics.js
sed -i '1i /**\n * Statistics Page Script\n */' static/js/pages/statistics.js

# Settings  
sed -n '/<script>$/,/^    <\/script>$/p' templates/settings.html | sed '1d;$d' > static/js/pages/settings.js
sed -i '1i /**\n * Settings Page Script\n */' static/js/pages/settings.js

# Tournaments
sed -n '/<script>$/,/^    <\/script>$/p' templates/tournaments.html | sed '1d;$d' > static/js/pages/tournaments.js  
sed -i '1i /**\n * Tournaments Page Script\n */' static/js/pages/tournaments.js

# Payments (old)
sed -n '/<script>$/,/^    <\/script>$/p' templates/payments.html | sed '1d;$d' > static/js/pages/payments.js
sed -i '1i /**\n * Payments Page Script\n */' static/js/pages/payments.js

# Payments (new)
sed -n '/<script>$/,/^    <\/script>$/p' templates/payments_new.html | sed '1d;$d' > static/js/pages/payments-new.js
sed -i '1i /**\n * Payments New Page Script\n */' static/js/pages/payments-new.js

echo "✅ Created 5 JS files"
ls -lh static/js/pages/{statistics,settings,tournaments,payments,payments-new}.js
