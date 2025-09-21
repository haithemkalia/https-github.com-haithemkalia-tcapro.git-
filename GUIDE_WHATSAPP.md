# 📱 Guide d'utilisation WhatsApp - Système TCA

## 🎯 Fonctionnalités WhatsApp

Le système TCA intègre maintenant des notifications WhatsApp automatiques et manuelles pour tous les clients.

### ✅ Fonctionnalités disponibles :

1. **Notifications automatiques** lors du changement de statut de visa
2. **Envoi manuel** via le bouton WhatsApp dans la liste des clients
3. **Messages personnalisés** selon le statut de visa
4. **Ouverture automatique** de WhatsApp Desktop ou Web

## 🚀 Comment utiliser

### 1. **Notifications automatiques**

Quand vous changez le statut de visa d'un client :
- Le système détecte automatiquement le changement
- WhatsApp s'ouvre avec le numéro du client
- Le message est pré-rempli selon le nouveau statut
- Vous n'avez qu'à cliquer sur "Envoyer"

### 2. **Envoi manuel**

Dans la liste des clients :
- Cliquez sur le bouton vert WhatsApp (📱) à côté de chaque client
- WhatsApp s'ouvre avec le numéro et le message du statut actuel
- Cliquez sur "Envoyer" dans WhatsApp

### 3. **Messages automatiques par statut**

#### 🛂 **تم التقديم في السيستام**
```
🛂 تحديث حالة التأشيرة

مرحباً [Nom du client]،

تم تسجيل طلب التأشيرة الخاص بك في النظام بنجاح.

📋 الحالة الحالية: تم التقديم في السيستام
📅 التاريخ: [Date actuelle]

سيتم متابعة طلبك وإعلامك بأي تحديثات.

شكراً لثقتكم بنا.

---
شركة تونس للاستشارات والخدمات
```

#### 🏛️ **تم التقديم إلى السفارة**
```
🛂 تحديث حالة التأشيرة

مرحباً [Nom du client]،

تم تقديم طلب التأشيرة الخاص بك إلى السفارة.

📋 الحالة الحالية: تم التقديم إلى السفارة
📅 التاريخ: [Date actuelle]

ننتظر رد السفارة وسنقوم بإعلامك فوراً.

شكراً لصبركم.

---
شركة تونس للاستشارات والخدمات
```

#### 🎉 **تمت الموافقة على التأشيرة**
```
🎉 تهانينا!

مرحباً [Nom du client]،

🎊 تمت الموافقة على طلب التأشيرة الخاص بك!

📋 الحالة الحالية: تمت الموافقة على التأشيرة
📅 التاريخ: [Date actuelle]

يمكنكم الآن استلام جواز السفر مع التأشيرة.

شكراً لثقتكم بنا.

---
شركة تونس للاستشارات والخدمات
```

#### 😔 **التأشيرة غير موافق عليها**
```
😔 تحديث حالة التأشيرة

مرحباً [Nom du client]،

للأسف، لم يتم قبول طلب التأشيرة.

📋 الحالة الحالية: التأشيرة غير موافق عليها
📅 التاريخ: [Date actuelle]

يمكنكم مراجعة الأسباب معنا أو إعادة التقديم.

نحن هنا لمساعدتكم.

---
شركة تونس للاستشارات والخدمات
```

#### ✅ **اكتملت العملية**
```
✅ اكتملت العملية

مرحباً [Nom du client]،

تم إكمال جميع إجراءات التأشيرة بنجاح.

📋 الحالة الحالية: اكتملت العملية
📅 التاريخ: [Date actuelle]

شكراً لثقتكم بنا.

---
شركة تونس للاستشارات والخدمات
```

## 🔧 Configuration technique

### Numéros de téléphone supportés :
- Format tunisien : `216XXXXXXXXX`
- Format international : `+216XXXXXXXXX`
- Format local : `0XXXXXXXXX`

### Méthodes d'ouverture :
1. **WhatsApp Desktop** (si installé)
2. **WhatsApp Web** (navigateur par défaut)
3. **Fallback automatique** si WhatsApp Desktop n'est pas disponible

## 📋 Exemple d'utilisation

### Client : ابوبكر بادي (CLI976)
- **Numéro** : 218913810603
- **Statut actuel** : تمت الموافقة على التأشيرة

### Actions possibles :
1. **Changer le statut** → WhatsApp s'ouvre automatiquement
2. **Cliquer sur le bouton WhatsApp** → Envoi manuel du message
3. **Le message est pré-rempli** avec le nom et le statut

## ⚠️ Notes importantes

- **WhatsApp Desktop** : Préféré si installé
- **WhatsApp Web** : Utilisé automatiquement si Desktop non disponible
- **Messages en arabe** : Encodage automatique correct
- **Numéros** : Nettoyage et validation automatiques
- **Logs** : Tous les envois sont enregistrés dans les logs du serveur

## 🎯 Résultat

Le système est maintenant **100% opérationnel** pour :
- ✅ Notifications automatiques
- ✅ Envoi manuel
- ✅ Messages personnalisés
- ✅ Ouverture WhatsApp automatique
- ✅ Support des numéros tunisiens
- ✅ Messages en arabe

**WhatsApp fonctionne parfaitement avec votre système TCA !** 🎉
