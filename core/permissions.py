from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSuperuserOrReadOnly(BasePermission):
    """Permite leitura a qualquer autenticado e escrita apenas a superusuários.

    Gerenciar grupos equivale a distribuir permissões, então nem a equipe
    (is_staff) pode escrever: isso permitiria a qualquer staff se promover.
    """

    message = 'Apenas superusuários podem gerenciar grupos.'

    def has_permission(self, request, view):
        user = request.user

        if not (user and user.is_authenticated):
            return False

        if request.method in SAFE_METHODS:
            return True

        return bool(user.is_superuser)


class IsStaffForCreate(BasePermission):
    """Restringe a criação de recursos à equipe; as demais ações seguem as outras permissões."""

    message = 'Apenas membros da equipe podem criar usuários.'

    def has_permission(self, request, view):
        if view.action != 'create':
            return True

        return bool(request.user and request.user.is_staff)
