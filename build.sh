#!/bin/bash
# Remove dist directory if it exists
rm -f "Vatsim FPL Checker Linux/Vatsim FPL Checker.deb"

fpm -s dir -t deb -n "Vatsim FPL Checker" -v 1.0.0 -a arm64 \
    --prefix /opt/vatsim-fpl-checker \
    -C "/home/willbrunker/Vatsim-FPL" .

# Rename the output .deb file
mv "vatsim-fpl-checker_1.0.0_arm64.deb" "Vatsim FPL Checker Linux/Vatsim FPL Checker.deb"
rm -f "Vatsim FPL Checker.zip"

echo "Done."