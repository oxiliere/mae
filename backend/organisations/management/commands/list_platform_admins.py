from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from django.db.models import Count, Q
from django.db import models

from organisations.models.organisations import Organization, OrganizationUser


class Command(BaseCommand):
    help = _('Lister toutes les organisations administrateurs de plateforme')

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help=_('Afficher des informations détaillées')
        )
        parser.add_argument(
            '--include-inactive',
            action='store_true',
            help=_('Inclure les organisations inactives')
        )

    def handle(self, *args, **options):
        # Récupérer les organisations administrateurs de plateforme
        queryset = Organization.objects.filter(is_platform_admin=True)
        
        if not options['include_inactive']:
            queryset = queryset.filter(is_active=True)
        
        # Ajouter des annotations pour les statistiques
        queryset = queryset.annotate(
            users_count=Count('organization_users', distinct=True),
            active_users_count=Count('organization_users', filter=Q(organization_users__is_active=True), distinct=True)
        ).order_by('name')

        if not queryset.exists():
            self.stdout.write(
                self.style.WARNING(
                    "❌ Aucune organisation administrateur de plateforme trouvée."
                )
            )
            self.stdout.write(
                "💡 Utilisez la commande 'setup_oxiliere_platform' pour en créer une."
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"📋 {queryset.count()} organisation(s) administrateur(s) de plateforme trouvée(s):"
            )
        )
        self.stdout.write("=" * 80)

        for org in queryset:
            self._display_organization(org, options['detailed'])
            if options['detailed']:
                self.stdout.write("-" * 80)

    def _display_organization(self, org, detailed=False):
        """Afficher les informations d'une organisation"""
        # Statut avec emoji
        status_emoji = "✅" if org.is_active else "❌"
        admin_emoji = "⚡" if org.is_platform_admin else "👤"
        
        # Affichage de base
        self.stdout.write(f"{status_emoji} {admin_emoji} {org.name}")
        self.stdout.write(f"   🆔 ID: {org.id}")
        self.stdout.write(f"   🔑 Company ID: {org.slug}")
        
        if detailed:
            self.stdout.write(f"   📧 Email: {org.email or 'Non défini'}")
            self.stdout.write(f"   📱 Téléphone: {org.phone or 'Non défini'}")
            self.stdout.write(f"   🏢 SIRET: {org.siret or 'Non défini'}")
            self.stdout.write(f"   💼 TVA: {org.vat_number or 'Non défini'}")
            self.stdout.write(f"   📍 Adresse: {org.address or 'Non définie'}")
            self.stdout.write(f"   🌍 Localisation: {org.location or 'Non définie'}")
            self.stdout.write(f"   🏳️ Pays: {org.country}")
            self.stdout.write(f"   📮 Code postal: {org.postal_code or 'Non défini'}")
            self.stdout.write(f"   🕒 Fuseau horaire: {org.timezone}")
            self.stdout.write(f"   🗣️ Langue: {org.language}")
            self.stdout.write(f"   💰 Devise: {org.currency}")
            
            if org.industry:
                self.stdout.write(f"   🏭 Secteur: {org.get_industry_display()}")
            if org.company_size:
                self.stdout.write(f"   👥 Taille: {org.get_company_size_display()}")
            
            self.stdout.write(f"   🔒 Visibilité: {org.get_visibility_display()}")
            self.stdout.write(f"   📅 Créé le: {org.created_at.strftime('%d/%m/%Y à %H:%M')}")
            self.stdout.write(f"   🔄 Modifié le: {org.updated_at.strftime('%d/%m/%Y à %H:%M')}")
            
            # Statistiques des utilisateurs
            users_count = getattr(org, 'users_count', 0)
            active_users_count = getattr(org, 'active_users_count', 0)
            self.stdout.write(f"   👤 Utilisateurs: {active_users_count}/{users_count} (actifs/total)")
            
            # Lister les utilisateurs administrateurs
            admin_users = OrganizationUser.objects.filter(
                organization=org,
                is_active=True
            ).select_related('user')
            
            if admin_users.exists():
                self.stdout.write("   👨‍💼 Utilisateurs administrateurs:")
                for org_user in admin_users:
                    user = org_user.user
                    self.stdout.write(f"      - {user.get_full_name() or user.username} ({user.email})")
            else:
                self.stdout.write("   ⚠️  Aucun utilisateur administrateur associé")
        else:
            # Affichage compact
            users_count = getattr(org, 'active_users_count', 0)
            self.stdout.write(f"   👤 {users_count} utilisateur(s) actif(s)")
            self.stdout.write(f"   📅 Créé le {org.created_at.strftime('%d/%m/%Y')}")


