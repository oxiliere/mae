# MAE – Passport Publication Service

MAE is a digital platform designed to publish online lists of received passports.  
It replaces the traditional process of posting printed lists at physical locations, allowing citizens to check the status of their passport from anywhere.

MAE improves transparency, reduces unnecessary travel, and offers a modern and reliable communication tool for public institutions.

---

## Features

- Online publication of received passport lists
- Real-time updates when new passports arrive
- Search and filtering capabilities
- Mobile-friendly public interface
- Secure administrator dashboard
- API endpoints for integrations with other systems
- Audit-ready logs for traceability

---

## System Overview

MAE is composed of three main components:

1. **Backend API**
   Handles passport records, publication logic, authentication, permissions, and data validation.

2. **Admin Dashboard**
   A secure interface where authorized personnel can add, update, or publish passport data.

3. **Public Portal**
   A lightweight web interface allowing users to search for their passport status.

---

## How It Works

1. Passport arrival data is recorded by an administrator.
2. The backend updates the published list using the defined business rules.
3. The public portal retrieves the updated records through the API.
4. Citizens search for their passport by name, reference number, or batch code.

---

## Installation

### Requirements

- Python 3.10+
- Django / Django-Ninja (or the chosen stack)
- PostgreSQL or MySQL database
- Redis (for caching, background tasks, or real-time updates)
- Git for version control
