CLIENTOSERROR = "A networking issue occurred, try again later? If this keeps happening, contact " \
                                 "Alento/Sombra Ghostflame."
PI_SERVICE_UNAVAILABLE = "Service unavailable, something is happening on EVEs side. Please try again later..."
NO_AUTH_SELECTED_CHARACTER = "It doesn't appear you have a selected character, do `auth select` to find out more."
AUTH_SCOPE_MISSING = "Auth scope {} is missing, contact Alento/Sombra Ghostflame immediately!"
PI_AUTH_SCOPE_FALSE = "You are missing the `esi-planets.manage_planets.v1` scope required for this " \
                                 "feature, set it to be enabled by doing `pi enable`"
PI_INVALID_PLANET = "Planet ID `{}` not found."


PI_BRIEF = "Shows info about your Planetary Integration setup."
PI_ENABLE_BRIEF = "Flags the selected character to have permissions for PI enabled."
PI_DISABLE_BRIEF = "Does the opposite of enable, flagging permissions to be disabled."
PI_UPDATE_BRIEF = "Updates and displays the information the bot has about your PI."
PI_INFO_BRIEF = "Displays the information the bot has about your PI, but does not update. Optional planet_id " \
                "argument to list in-depth information of a specific planet."
PI_HELP_DESCRIPTION = "Gives information about Planetary Interactions. Be warned, data on EVEs side only " \
                              "updates when you log in and view the planet, so inaccuracies will only grow larger " \
                      "the longer you have not viewed the planet. Use `pi` to list this embed."
PI_HELP_PERMISSION = f"`pi enable`: {PI_ENABLE_BRIEF}\n`pi disable`: {PI_DISABLE_BRIEF}"
PI_HELP_UPDATE = f"`pi update`: {PI_UPDATE_BRIEF} Do `pi update` for more information."
PI_HELP_INFORMATION = f"`pi info`: {PI_INFO_BRIEF}"
PI_INVALID_SUBCOMMAND = "Invalid subcommand, do `pi` to view valid subcommands."

PI_UPDATE_BASIC_BRIEF = "Updates and shows basic PI data, faster than `pi update full`"
PI_UPDATE_FULL_BRIEF = "Updates all PI data, including in-depth information about planets. Shows basic PI data."
PI_UPDATE_PLANET_BRIEF = "Updates information about a specific planet and shows it."
PI_UPDATE_HELP_DESCRIPTION = PI_UPDATE_BRIEF
PI_UPDATE_HELP_COMMANDS = f"`pi update basic`: {PI_UPDATE_BASIC_BRIEF}\n`pi update full`: {PI_UPDATE_FULL_BRIEF}\n" \
                          f"`pi update planet_id`: {PI_UPDATE_PLANET_BRIEF} Replace `planet_id` with the ID of a " \
                          f"planet."
PI_UPDATE_INVALID_SUBCOMMAND = "Invalid subcommand, do `pi update` to view valid subcommands."


PI_CONTROL_MISSING_ARG_1 = "Invalid argument, do `pi` to view valid arguments."

PI_CONTROL_ENABLE_SUCCESS = "`esi-planets.manage_planets.v1` enabled, run `auth update` to update permissions."
PI_CONTROL_DISABLE_SUCCESS = "`esi-planets.manage_planets.v1` disabled, run `auth update` to update permissions."

PI_CONTROL_INVALID_CHAR_OR_PERMISSION = "`esi-planets.manage_planets.v1` failed to toggle. If the selected auth " \
                                        "character is valid, contact Sombra/Alento Ghostflame!"
PI_CONTROL_UPDATE_MISSING_ARG = "This command updates the PI information, do `pi` for more information."
PI_CONTROL_UPDATE_PLANET_SUCCESS = "Updated planet `{}` successfully."
PI_CONTROL_UPDATE_PLANET_NOT_FOUND = "Planet ID `{}` not found."
PI_CONTROL_UPDATE_BASIC_SUCCESS = "Updated basic PI data."
PI_CONTROL_LIST_UPDATING = "Missing basic PI data, fixing that..."
PI_CONTROL_PLANET_INFO_MISSING_ARG = "`pi planet planet_id` Replace `planet_id` with one in `pi list` to get " \
                                     "information about that planet."
PI_CONTROL_PLANET_INFO_ERROR = "An error occurred getting planet info, do you have a colony on the given planet ID?"
PI_CONTROL_PLANET_INFO_ID_NOT_IN_PI_INFO = "Planet ID not in basic PI data, maybe run `pi update basic` ?"
PI_CONTROL_PLANET_INFO_UPDATING = "Missing planet PI data, fixing that..."

