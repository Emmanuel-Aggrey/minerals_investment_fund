def app_permissions(request):
    user = request.user
    if not user.is_authenticated:
        return {
            'app_permissions': {
                'can_view_dashboard': False,
                'can_register_visit': False,
                'can_view_reports': False,
                'can_access_admin': False,
            }
        }

    return {
        'app_permissions': {
            'can_view_dashboard': user.can_view_dashboard,
            'can_register_visit': user.can_register_visit,
            'can_view_reports': user.can_view_reports,
            'can_access_admin': user.can_access_admin,
        }
    }
