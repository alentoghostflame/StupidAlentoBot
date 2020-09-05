BOT_MISSING_MANAGE_ROLES_PERMISSION = "I require the \"Manage Roles\" permission to assign roles to users."
BOT_CANT_ADD_OR_REMOVE_ROLE = "I can't add/remove that role, is the role hierarchy properly set up?"
USER_MISSING_ADMIN_PERMISSION = "This command requires the Administrator permission, something that you lack."
ROLE_INVALID_SUBCOMMAND = "Subcommand or role keyword not found. To see available subcommands, do `role`"
NO_PRIVATE_MESSAGE = "This command can only be used on a server, not in private messages."
ROLE_KEYWORD_NOT_FOUND = "Role keyword `{}` not found."
ROLE_NO_LONGER_IN_GUILD = "The role corresponding to that keyword no longer exists, contact a server administrator " \
                          "to have it removed."


ROLE_GROUP_BRIEF = "Allows users to self-assign roles securely."
ROLE_INFO_BRIEF = "Shows keywords and the roles they are assigned to."
ROLE_ADD_BRIEF = "Assigns a keyword with a role for users to use."
ROLE_REMOVE_BRIEF = "Removes a keyword from being used."


ROLE_HELP_DESCRIPTION = "Allows users to give themselves roles without giving them risky permissions. Do `role` to " \
                        "view this embed."
ROLE_HELP_USAGE = "`role role_keyword`: Gives the user the role the keyword is assigned to."
ROLE_HELP_EDITING = f"`role add`: {ROLE_ADD_BRIEF}\n`role remove`: {ROLE_REMOVE_BRIEF}\n Both of these commands " \
                    f"require the Discord \"Administrator\" permission."
ROLE_HELP_INFORMATION = f"`role info`: {ROLE_INFO_BRIEF}\n`role info role_keyword` show all the people who has the " \
                        f"role corresponding to that keyword."


ROLE_TOGGLE_REMOVED = "Role removed from your account."
ROLE_TOGGLE_ADDED = "Role added to your account."

ROLE_ADD_MISSING_ARGS = "`role add role_keyword @role` Do `role` for more information."
ROLE_ADD_SUCCESS = "Role keyword `{}` added, now assigned to role `{}`."

ROLE_REMOVE_MISSING_ARGS = "`role remove role_keyword` or `role rm role_keyword` Do `role` for more information."
ROLE_REMOVE_SUCCESS = "Role keyword `{}` removed."

