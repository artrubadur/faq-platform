from typing import Any


state = {'glb_last_bot_message_id': 6485, 'glb_found_user_id': 5457527695, 'glb_found_username': 'artrubadur', 'tmp_in_operation': True, 'tmp_orig_id': 5457527695, 'tmp_orig_username': 'artrubadur', 'tmp_orig_role': 'admin'}
print(state)

def is_expired(state_data: dict[str, Any]):
    return state_data.get("tmp_in_operation", False) != True

print(is_expired(state))