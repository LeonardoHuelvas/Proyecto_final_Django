import os
import django

# Configurar Django para que pueda acceder a los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_courses.settings')
django.setup()

from django.contrib.auth.models import Group, Permission, User

# Crear grupo 'Moderators'
moderators, created = Group.objects.get_or_create(name='Moderators')

# Asignar permisos al grupo 'Moderators'
permissions = ['add_user', 'change_user', 'delete_user', 'view_user']
for perm in permissions:
    permission = Permission.objects.get(codename=perm)
    moderators.permissions.add(permission)

# Asignar un usuario al grupo 'Moderators'
user = User.objects.get(username='tu_nombre_de_usuario')
user.groups.add(moderators)

print("Grupos y permisos inicializados con éxito.")
