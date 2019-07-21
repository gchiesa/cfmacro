
def role_arn_to_name(role_arn):
    # ?"arn:aws:iam::${account}:role/RoleCredentialServerCryptOnly"
    if isinstance(role_arn, str) and role_arn.startswith('arn'):
        return role_arn.rpartition('/')[-1]
    return role_arn
