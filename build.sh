#!/bin/bash
# Remove old .deb
rm -f "Vatsim FPL Checker Linux/Vatsim FPL Checker.deb"

# Build .deb with launcher icon and desktop entry
fpm -s dir -t deb -n "Vatsim FPL Checker" -v 1.0.0 -a arm64 \
    --prefix /opt/vatsim-fpl-checker \
    -C "/home/willbrunker/Vatsim-FPL" \
    "Vatsim FPL Checker Linux/Vatsim FPL Checker.desktop"=/usr/share/applications/vatsim-fpl-checker.desktop \
    "Vatsim FPL Checker Icon.png"=/usr/share/icons/hicolor/128x128/apps/vatsim-fpl-checker.png \
    .

# Rename output
mv "vatsim-fpl-checker_1.0.0_arm64.deb" "Vatsim FPL Checker Linux/Vatsim FPL Checker.deb"
rm -f "Vatsim FPL Checker.zip"

echo "Done."
