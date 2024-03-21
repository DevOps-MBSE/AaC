### LIST ALL REGISTERED AAC PLUGINS ###
echo "===================================="
echo "  AAC PLUGINS:"
echo "===================================="
aac print-defs | perl -ne 'm/^  name:(.*)$/ && print "  - $1\n"' | sort
echo "===================================="
