#!/bin/bash

# Update statistics.html
sed -i '/<script>$/,/<\/script>$/c\    <script src="/static/js/pages/statistics.js"></script>' templates/statistics.html

# Update settings.html  
sed -i '/<script>$/,/<\/script>$/c\    <script src="/static/js/pages/settings.js"></script>' templates/settings.html

# Update tournaments.html
sed -i '/<script>$/,/<\/script>$/c\    <script src="/static/js/pages/tournaments.js"></script>' templates/tournaments.html

# Update payments.html
sed -i '/<script>$/,/<\/script>$/c\    <script src="/static/js/pages/payments.js"></script>' templates/payments.html

# Update payments_new.html  
sed -i '/<script>$/,/<\/script>$/c\    <script src="/static/js/pages/payments-new.js"></script>' templates/payments_new.html

echo "✅ Updated 5 HTML files to use external JS"
