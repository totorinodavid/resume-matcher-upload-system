# 🚨 STRIPE CREDITS DEBUG - PRAKTISCHE ANLEITUNG

## 🎯 **Das User-ID Mapping Problem lösen**

Da die Environment Variables korrekt sind und die Authentifizierung funktioniert, liegt das Problem wahrscheinlich bei der **User-ID Übertragung** vom Frontend zum Backend-Webhook.

## 🔍 **SOFORTIGE DIAGNOSE - SCHRITT FÜR SCHRITT**

### **Schritt 1: Prüfen Sie Ihre aktuelle Session**

1. Gehen Sie zu **https://gojob.ing**
2. Öffnen Sie **Browser Dev Tools** (F12)
3. Gehen Sie zu **Console** tab
4. Führen Sie aus:
   ```javascript
   fetch('/api/auth/session').then(r => r.json()).then(console.log)
   ```
5. **Erwartetes Ergebnis**: Sie sollten ein `user` Objekt mit einer `id` sehen

### **Schritt 2: Test-Checkout mit Debug-Informationen**

1. Bleiben Sie in den **Dev Tools**
2. Gehen Sie zu **Network** tab
3. Versuchen Sie einen **Credit-Kauf**
4. Schauen Sie sich den **POST Request** zu `/api/stripe/checkout` an
5. **Prüfen Sie**: Ist `userId` im Request-Body enthalten?

### **Schritt 3: Webhook-Logs in Echtzeit prüfen**

Führen Sie dieses Monitoring aus (während Sie einen Kauf tätigen):

```bash
python webhook_realtime_logger.py
```

**Was Sie sehen sollten:**
- ✅ "Webhook processed successfully" → Credits sollten hinzugefügt werden
- ❌ "USER ID MAPPING FAILURE" → user_id Problem
- ❌ "PRICE MAPPING FAILURE" → Price-ID Problem

## 🔧 **WAHRSCHEINLICHSTE URSACHEN & LÖSUNGEN**

### **1. NextAuth User-ID Format Problem**
**Symptom**: Webhook bekommt `user_id` aber kann sie nicht verarbeiten
**Lösung**: 
```typescript
// In checkout/route.ts, Zeile ~60:
metadata: {
  user_id: String(userId), // Sicherstellen, dass es ein String ist
  // ...
}
```

### **2. Session Expiry während Checkout**
**Symptom**: User startet Checkout eingeloggt, aber Session läuft ab
**Lösung**: Session vor Checkout erneuern

### **3. Price-ID Mismatch**
**Symptom**: Webhook bekommt `user_id` aber keine Credits wegen falscher Price-ID
**Lösung**: Environment Variables mit echten Stripe Price-IDs aktualisieren

## 🧪 **QUICK TEST - MANUAL WEBHOOK SIMULATION**

Sie können den Webhook manuell testen mit:

```bash
curl -X POST https://gojob.ing/api/stripe/webhook \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: t=1693906800,v1=test" \
  -d '{
    "type": "checkout.session.completed",
    "data": {
      "object": {
        "metadata": {
          "user_id": "IHR_USER_ID_HIER",
          "credits": "100"
        }
      }
    }
  }'
```

## 📊 **DEBUGGING PRIORITÄTEN**

1. **HÖCHSTE PRIORITÄT**: Prüfen Sie Ihre aktuelle User-ID im Browser
2. **HOHE PRIORITÄT**: Monitoring während echtem Kauf
3. **MITTLERE PRIORITÄT**: Webhook-Logs analysieren

## 🎯 **ERWARTETES ERGEBNIS NACH FIX**

1. **Checkout Session**: Enthält korrekte `user_id` in metadata
2. **Webhook Event**: Empfängt und verarbeitet `user_id` korrekt  
3. **Credits**: Werden automatisch zu Ihrem Account hinzugefügt
4. **Balance**: Aktualisiert sich nach Payment

---

**NÄCHSTER SCHRITT**: Führen Sie Schritt 1-3 durch und teilen Sie die Ergebnisse mit mir! 🚀
