def user_type_context(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return {"base_template": "admin-base.html"}
        else:
            return {"base_template": "base.html"}
    return {"base_template": "base.html"}
