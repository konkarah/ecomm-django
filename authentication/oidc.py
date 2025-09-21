# def userinfo(claims, user):
#     """
#     Populate OpenID Connect userinfo response
#     """
#     claims['sub'] = str(user.id)
#     claims['name'] = f"{user.first_name} {user.last_name}".strip()
#     claims['given_name'] = user.first_name
#     claims['family_name'] = user.last_name
#     claims['email'] = user.email
#     claims['email_verified'] = user.is_verified
#     claims['preferred_username'] = user.username
#     claims['phone_number'] = getattr(user, 'phone_number', '')
#     claims['address'] = getattr(user, 'address', '')
#     return claims
def userinfo(claims, user):
    """
    Populate OpenID Connect userinfo response
    This function is called when the /o/userinfo/ endpoint is accessed
    """
    claims['sub'] = str(user.id)  # Subject - unique user identifier
    claims['name'] = f"{user.first_name} {user.last_name}".strip() or user.username
    claims['given_name'] = user.first_name or ""
    claims['family_name'] = user.last_name or ""
    claims['email'] = user.email
    claims['email_verified'] = getattr(user, 'is_verified', False)
    claims['preferred_username'] = user.username
    
    # Add custom claims from your Customer model
    if hasattr(user, 'phone_number'):
        claims['phone_number'] = user.phone_number or ""
    if hasattr(user, 'address'):
        claims['address'] = {
            'formatted': user.address or ""
        }
    
    # Add profile picture if you have one
    claims['picture'] = ""  # Add URL to user's profile picture if available
    
    # Add custom business logic claims
    claims['orders_count'] = user.orders.count() if hasattr(user, 'orders') else 0
    claims['is_premium_customer'] = user.orders.count() > 5 if hasattr(user, 'orders') else False
    
    return claims
