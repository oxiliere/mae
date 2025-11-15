# Commandes de gestion Django - Organisations

Ce répertoire contient les commandes de gestion Django pour l'application `organisations`.

## Commandes disponibles

### 1. `setup_oxiliere_platform`

**Configuration rapide de l'organisation administrateur Oxiliere**

Cette commande crée automatiquement une organisation administrateur de plateforme avec des valeurs par défaut optimisées pour Oxiliere.

```bash
# Configuration basique (valeurs par défaut)
python manage.py setup_oxiliere_platform

# Configuration personnalisée
python manage.py setup_oxiliere_platform \
    --name "Oxiliere Platform" \
    --company-id "oxiliere-platform" \
    --email "admin@oxiliere.com"

# Forcer la création même si l'organisation existe
python manage.py setup_oxiliere_platform --force

# Ignorer si l'organisation existe déjà
python manage.py setup_oxiliere_platform --skip-if-exists
```

**Valeurs par défaut :**
- Nom : "Oxiliere Platform"
- Company ID : "oxiliere-platform"
- Email : "admin@oxiliere.com"
- Secteur : Technologie
- Taille : Moyenne entreprise
- Localisation : Lubumbashi, RD Congo
- Fuseau horaire : Africa/Lubumbashi
- Devise : USD

### 2. `create_platform_admin_org`

**Création personnalisée d'une organisation administrateur**

Cette commande permet de créer une organisation administrateur avec tous les paramètres personnalisables.

```bash
# Création avec paramètres minimaux
python manage.py create_platform_admin_org \
    --name "Ma Plateforme" \
    --company-id "ma-plateforme" \
    --email "admin@maplateforme.com"

# Création complète avec tous les paramètres
python manage.py create_platform_admin_org \
    --name "Oxiliere Enterprise" \
    --company-id "oxiliere-enterprise" \
    --email "enterprise@oxiliere.com" \
    --description "Organisation enterprise Oxiliere" \
    --website "https://enterprise.oxiliere.com" \
    --phone "+243970123456" \
    --siret "12345678901234" \
    --vat-number "CD123456789" \
    --address "Avenue de la Paix, Gombe" \
    --location "Kinshasa" \
    --country "CD" \
    --postal-code "12345" \
    --timezone "Africa/Kinshasa" \
    --language "fr" \
    --currency "USD" \
    --industry "technology" \
    --company-size "large" \
    --visibility "private"
```

**Paramètres disponibles :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `--name` | string | ✅ | Nom de l'organisation |
| `--company-id` | string | ✅ | Identifiant unique (slug) |
| `--email` | string | ✅ | Email de contact |
| `--description` | string | ❌ | Description de l'organisation |
| `--website` | string | ❌ | Site web |
| `--phone` | string | ❌ | Numéro de téléphone |
| `--siret` | string | ❌ | Numéro SIRET |
| `--vat-number` | string | ❌ | Numéro de TVA |
| `--address` | string | ❌ | Adresse complète |
| `--location` | string | ❌ | Ville/Localisation |
| `--country` | string | ❌ | Code pays ISO (défaut: CD) |
| `--postal-code` | string | ❌ | Code postal |
| `--timezone` | choice | ❌ | Fuseau horaire |
| `--language` | string | ❌ | Code langue (défaut: fr) |
| `--currency` | string | ❌ | Code devise (défaut: USD) |
| `--industry` | choice | ❌ | Secteur d'activité |
| `--company-size` | choice | ❌ | Taille de l'entreprise |
| `--visibility` | choice | ❌ | Visibilité (public/private) |
| `--force` | flag | ❌ | Forcer la création |

**Choix disponibles :**

- **Timezone :** `Africa/Kinshasa`, `Africa/Lubumbashi`, `Africa/Dakar`, `Africa/Nairobi`
- **Industry :** `technology`, `healthcare`, `finance`, `education`, `manufacturing`, `retail`, `agriculture`, `construction`, `transportation`, `energy`, `telecommunications`, `media`, `hospitality`, `real_estate`, `consulting`, `legal`, `nonprofit`, `government`, `mining`, `other`
- **Company Size :** `micro`, `small`, `medium`, `large`, `enterprise`
- **Visibility :** `public`, `private`

### 3. `list_platform_admins`

**Lister les organisations administrateurs de plateforme**

```bash
# Liste basique
python manage.py list_platform_admins

# Liste détaillée
python manage.py list_platform_admins --detailed

# Inclure les organisations inactives
python manage.py list_platform_admins --include-inactive

# Liste complète avec détails
python manage.py list_platform_admins --detailed --include-inactive
```

## Workflow recommandé

### 1. Configuration initiale

```bash
# 1. Créer l'organisation administrateur
python manage.py setup_oxiliere_platform

# 2. Créer un superutilisateur Django
python manage.py createsuperuser

# 3. Vérifier la création
python manage.py list_platform_admins --detailed
```

### 2. Association utilisateur-organisation

Après avoir créé l'organisation et l'utilisateur :

1. Aller sur `/admin/organisations/organizationuser/add/`
2. Sélectionner l'utilisateur créé
3. Sélectionner l'organisation "Oxiliere Platform"
4. Définir le rôle comme "Owner" ou "Admin"
5. Cocher "is_active"
6. Sauvegarder

### 3. Configuration des applications

1. Aller sur `/admin/organisations/oxapplication/`
2. Créer les applications de la plateforme
3. Configurer les webhooks et URLs d'intégration

## Exemples d'utilisation

### Environnement de développement

```bash
python manage.py setup_oxiliere_platform \
    --email "dev@oxiliere.local" \
    --skip-if-exists
```

### Environnement de production

```bash
python manage.py create_platform_admin_org \
    --name "Oxiliere Production" \
    --company-id "oxiliere-prod" \
    --email "admin@oxiliere.com" \
    --website "https://oxiliere.com" \
    --phone "+243970000000" \
    --address "Avenue de la Libération, Lubumbashi" \
    --location "Lubumbashi" \
    --timezone "Africa/Lubumbashi" \
    --industry "technology" \
    --company-size "medium"
```

### Environnement de test

```bash
python manage.py create_platform_admin_org \
    --name "Oxiliere Test" \
    --company-id "oxiliere-test" \
    --email "test@oxiliere.com" \
    --force
```

## Dépannage

### Erreur : Organisation existe déjà

```bash
# Solution 1 : Forcer la création
python manage.py setup_oxiliere_platform --force

# Solution 2 : Ignorer si existe
python manage.py setup_oxiliere_platform --skip-if-exists

# Solution 3 : Vérifier l'existant
python manage.py list_platform_admins --detailed
```

### Erreur : Company ID invalide

Le `company-id` doit :
- Contenir uniquement des lettres, chiffres, tirets et underscores
- Être unique dans la base de données
- Être en minuscules (recommandé)

### Erreur : Email invalide

L'email doit contenir un `@` et être au format valide.

## Notes importantes

- ⚠️ Les organisations avec `is_platform_admin=True` ont des privilèges élevés
- 🔒 Utilisez toujours `--force` avec précaution en production
- 📊 Utilisez `list_platform_admins` pour vérifier les créations
- 🔄 Les commandes sont transactionnelles (rollback automatique en cas d'erreur)
