ADMIN_HELP = "This command "


WARN_HELP = "This command warns the given user for 30 minutes. Use `;warn @user` replacing `@user` with mentioning " \
            "the user."
WARN_DEFAULT_REASON = "No reason given."
WARN_REASON = "{} Warned because: {}"
WARN_GIVEN = "30 minute warn given."
WARN_DOUBLE = "Already had a warn, muted for 30 minutes."
WARN_DOUBLE_REASON = "{} Doubled warned because: {}"

WARN_MISSING_ROLE = "You lack the role or permission required to warn users."
WARN_CANT_WARN_WARNERS = "You can't warn the warners"
WARN_ROLE_MISSING = "The selected warn role is non-existent. Fix that by using `;warn_admin set_warn_role @role` " \
                    "replacing @role with mentioning the role."
WARN_MUTE_MISSING = "Can't do 2 warns -> mute due to mute not being assigned a role."
