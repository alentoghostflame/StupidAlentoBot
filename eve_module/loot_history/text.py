LOOT_HISTORY_NO_ATTACHMENT = "Error, no attachment found."
LOOT_HISTORY_INVALID_FILTER = "Error, given filter mode not valid."
LOOT_HISTORY_INVALID_OUTPUT = "Error, given display mode not valid."
LOOT_HISTORY_INVALID_LOCATION = "Error, given location is invalid. Note: this does not support spaces."
LOOT_HISTORY_UNICODE_DECODE_ERROR = "Error, couldn't decode the attachment. Is it a text file?"
LOOT_HISTORY_ATTACHMENT_FAILED_CHECK = "Error, file contents failed internal check. Is that a valid EVE loot history " \
                                       "file?"

LOOT_HISTORY_HELP_DESCRIPTION = "Takes a Loot History file and outputs information about it, optionally filtering it " \
                                "or outputting it in another format.\nBe warned that Loot History can be tampered " \
                                "with by malevolent fleet members taking from jetcans and other containers."
LOOT_HISTORY_HELP_USAGE = "Write the command as you want, then add the Loot History file as an attachment. If you " \
                          "have multiple attachments, only the first one will be used.\n" \
                          "`lh filter_mode display_mode location_name percent_payout percent_volume`\n"
LOOT_HISTORY_HELP_OPTIONS = "`filter_mode`: `all` to show all items, `ore` to show only ores/asteroids.\n" \
                            "`display_mode`: `display` to display in Discord, `tsv` to output a Tab Separated " \
                            "Values file, `yaml` for basic YAML, `yaml_full` for a complete breakdown in YAML.\n" \
                            "`location_name`: Name of region or solar system to get prices from. If omitted, " \
                            "defaults to `jita`.\n" \
                            "`percent_payout`: Multiplier to apply to the payout. `0.9` for 90%, `0.8` for 80%, etc. " \
                            "If omitted, defaults to `1.0`\n" \
                            "`percent_quantity`: Multiplier to apply to the quantity, similar to `percent_payout`. " \
                            "If omitted, defaults to `1.0`"
LOOT_HISTORY_NOTHING_TO_SHOW = "No data to show."

LOOT_HISTORY_DISPLAY_LOOT_HISTORY_WAIT = "Request received, processing..."
LOOT_HISTORY_LOOT_HISTORY_FILE_SUCCESS = "Processed, file sent.\n{}"
