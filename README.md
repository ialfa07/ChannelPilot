# 🤖 Bot de Gestion de Canal Telegram

Un bot Telegram complet utilisant **aiogram** pour la gestion automatisée de canaux avec messages de bienvenue, publications programmées et sondages quotidiens.

## 🌟 Fonctionnalités

### ✅ Messages de Bienvenue Personnalisés
- Messages automatiques lors de nouveaux abonnements
- Envoi en privé ou dans le canal
- Template personnalisable avec nom d'utilisateur

### 📅 Messages Quotidiens Programmés
- Messages automatiques à heure fixe
- Rotation des messages
- Configuration via fichier JSON

### 🗳️ Sondages Quotidiens
- Sondages automatiques pour les canaux avec 500+ abonnés
- Options personnalisables par l'admin
- Horaire configurable

### 🔧 Gestion Multi-Canaux
- Support de plusieurs canaux simultanément
- Configuration individuelle par canal
- Statut et statistiques en temps réel

### ⚙️ Configuration Flexible
- Fichiers JSON pour les messages et paramètres
- Variables d'environnement pour les données sensibles
- Interface admin pour personnalisation

## 📋 Prérequis

- Python 3.8+
- Token de bot Telegram (via @BotFather)
- Droits d'administrateur sur les canaux à gérer

## 🚀 Installation

### 1. Cloner et préparer l'environnement

```bash
# Créer le répertoire du projet
mkdir telegram-channel-bot
cd telegram-channel-bot

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install aiogram python-dotenv apscheduler
