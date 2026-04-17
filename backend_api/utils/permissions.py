from rest_framework import permissions

class HasCompanyModulePermission(permissions.BasePermission):
    """
    Checks if the user has permission to access a specific module based on their role and permissions JSON.
    The module string is checked against `view.permission_module_name` (e.g. 'invoices').
    """

    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False

        # SUPER_ADMIN and COMPANY_ADMIN always have full permissions
        if user.role in ['SUPER_ADMIN', 'COMPANY_ADMIN']:
            return True
            
        module_name = getattr(view, 'permission_module_name', None)
        if not module_name:
            # If the view doesn't specify a module name, allow access by default,
            # or you could deny it. We will allow basic access.
            return True
            
        user_permissions = getattr(user, 'permissions', {})
        if not isinstance(user_permissions, dict):
            return False
            
        # Example permissions JSON definition: {"all": true} or {"invoices": true, "items": false}
        if user_permissions.get('all') is True:
            return True
            
        return user_permissions.get(module_name) is True
