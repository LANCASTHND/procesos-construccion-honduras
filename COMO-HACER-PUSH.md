# 🚀 Cómo Hacer Push a GitHub - Guía Paso a Paso

**Problema**: Error 403 Forbidden al intentar hacer push  
**Causa**: Sesión remota de Claude Code sin autenticación GitHub configurada  
**Solución**: Necesitas configurar credenciales

---

## ⚡ Solución Rápida (5 minutos)

### Si tienes GitHub CLI instalado localmente:

```bash
# En tu máquina (no en esta sesión remota)
gh auth login

# Sigue las instrucciones:
# 1. Selecciona GitHub.com
# 2. Selecciona HTTPS
# 3. Autoriza en el navegador
# 4. Confirma

# Luego, en esta sesión remota, intenta:
git push -u origin claude/honduras-procurement-report-hv200y
```

---

## 📋 Opción 1: SSH Keys (Más Seguro)

### Paso 1: Generar SSH Key (si no tienes)
```bash
ssh-keygen -t ed25519 -C "tu-email@ejemplo.com"
# Presiona Enter 3 veces (sin contraseña)
```

### Paso 2: Copiar la clave pública
```bash
cat ~/.ssh/id_ed25519.pub
# Copia todo el contenido
```

### Paso 3: Agregar a GitHub
1. Ve a https://github.com/settings/keys
2. Click en "New SSH key"
3. Pega el contenido
4. Guarda

### Paso 4: Cambiar remota a SSH
```bash
git remote set-url origin git@github.com:LANCASTHND/procesos-construccion-honduras.git
```

### Paso 5: Hacer push
```bash
git push -u origin claude/honduras-procurement-report-hv200y
```

---

## 🔐 Opción 2: Personal Access Token (GitHub CLI)

### Paso 1: Crear token en GitHub
1. Ve a https://github.com/settings/tokens
2. Click en "Generate new token" (classic)
3. Dale permisos `repo` (acceso completo a repositorio)
4. Copia el token (solo se muestra una vez)

### Paso 2: Usar el token
```bash
git push -u origin claude/honduras-procurement-report-hv200y
# Cuando pida contraseña/token, pega el token
```

---

## 💻 Opción 3: Usar Claude Code Desktop/Web Local

Si tienes Claude Code en tu máquina:

```bash
# En tu máquina local
cd /ruta/a/procesos-construccion-honduras
claude code .
```

El sistema de autenticación debería funcionar automáticamente.

---

## 🛠️ Opción 4: Forzar Credenciales en Esta Sesión

Si quieres intentar aquí mismo:

```bash
# Configurar credenciales temporalmente
git config credential.helper store

# Hacer push (pedirá usuario/contraseña)
git push -u origin claude/honduras-procurement-report-hv200y

# Cuando pida:
# Usuario: tu-usuario-github (o usa access token)
# Contraseña: access-token (si usas token, esto va aquí)
```

---

## 📊 Estado Actual de Commits

**4 commits listos para push:**

```
afb20ab - ✨ Agregar generador de datos demo y estado del sistema v3.0
c22d931 - 📌 Documentar estado de push pendiente y soluciones de autenticación
2a61f44 - 📚 Agregar documentación de demostración del sistema v3.0
115e8db - ✨ Implementar sistema automático de extracción y generación de reportes
```

**Tamaño de cambios:**
- ~1,200 líneas de código Python
- ~2,500 líneas de documentación
- 8 archivos nuevos
- 5 archivos modificados

---

## ✅ Verificar que funciona

Después de hacer push:

```bash
# Ver ramas remotas
git branch -r

# Debería mostrar:
# origin/claude/honduras-procurement-report-hv200y

# Ver commits en GitHub
git log --oneline -5
```

---

## 🎯 Recomendación

**Opción 1 (SSH)** es la más segura y permanente.  
**Opción 2 (Token)** es rápida si necesitas hacerlo YA.  
**Opción 3 (Local)** es la más simple si tienes Claude Code en tu máquina.

---

## 🚨 Si nada funciona

1. Verifica que tienes permisos en el repositorio:
   - Debes ser colaborador o dueño de `LANCASTHND/procesos-construccion-honduras`
   
2. Verifica la cuenta GitHub:
   - En https://github.com/settings/emails tu email debe estar verificado

3. Si el repositorio es privado:
   - Necesitas tener acceso explícito

---

## 📝 Comando Final (Una vez configurado)

```bash
git push -u origin claude/honduras-procurement-report-hv200y
```

**Eso es todo. 4 commits con todo el código irán a GitHub.** ✨

---

**Archivos que se enviarán:**
- scripts/extractor_honduras_compras.py
- scripts/generar_reportes.py
- scripts/generar_datos_demo.py
- scripts/actualizar.sh
- scripts/README.md
- scripts/requirements.txt
- data/instituciones.json
- CLAUDE.md (actualizado)
- SISTEMA-v3-DEMO.md
- ESTADO-SISTEMA-v3.md
- PUSH-PENDING.md
- COMO-HACER-PUSH.md

**Total: ~4,500 líneas de código y documentación**
