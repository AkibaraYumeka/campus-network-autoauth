#!/bin/bash

INTERFACE=$1
ACTION=$2

CAMPUS_PATTERNS=(
	"SSID*"
	"ANOTHER_SSID*"
)

if [ "$ACTION" = "up" ]; then
	CONN_NAME=$(nmcli -t -f GENERAL.CONNECTION device show "$INTERFACE" | cut -d: -f2-)
	CURRENT_SSID=$(nmcli -t -f 802-11-wireless.ssid connection show "$CONN_NAME" 2>/dev/null | cut -d: -f2-)

	for pattern in "${CAMPUS_PATTERNS[@]}"; do
		if [[ "$CURRENT_SSID" == $pattern ]]; then
			/usr/bin/systemctl restart campus-network-autoauth.service
			exit 0
		fi
	done
fi
