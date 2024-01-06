from . import permission_predicates, db_predicates

trusted_and_config = (permission_predicates.check_is_trusted and
                      db_predicates.check_is_config_set_up)

beatmaps_ready = (trusted_and_config and
                  db_predicates.check_is_user_has_beatmaps)

scores_ready = (trusted_and_config and
                db_predicates.check_is_user_has_scores)
