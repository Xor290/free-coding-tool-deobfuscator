# Free Coding Tool Deobfuscator

Un outil de déobfuscation pour les scripts Python obfusqués par [freecodingtools.org](https://freecodingtools.org/).

## Table des matières

- [À propos](#à-propos)
- [Technique d'obfuscation](#technique-dobfuscation)
- [Fonctionnement du déobfuscateur](#fonctionnement-du-déobfuscateur)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Exemple](#exemple)
- [Limitations](#limitations)

## À propos

Ce projet analyse et déobfusque les scripts Python obfusqués via l'outil en ligne gratuit [FreeCodingTools](https://freecodingtools.org/). L'outil utilise une technique d'obfuscation multi-couches basée sur la compression et l'encodage.

## Technique d'obfuscation

FreeCodingTools utilise une méthode d'obfuscation sophistiquée en plusieurs couches :

### Structure d'une couche

Chaque couche d'obfuscation suit ce schéma :

```python
# Couche N (obfusquée)
exec((lambda: <payload_bytes>)())
```

Le `<payload_bytes>` est une chaîne d'octets (bytes string) qui contient la couche suivante, encodée selon ce processus :

### Processus d'encodage (obfuscation)

1. **Compression** : Le code source est compressé avec `zlib`
   ```python
   compressed = zlib.compress(source_code)
   ```

2. **Encodage Base64** : Les données compressées sont encodées en Base64
   ```python
   encoded = base64.b64encode(compressed)
   ```

3. **Inversion** : La chaîne Base64 est inversée (reverse)
   ```python
   reversed_payload = encoded[::-1]
   ```

4. **Encapsulation** : Le payload est encapsulé dans un appel `exec()`
   ```python
   exec((lambda: b'<reversed_payload>')())
   ```

### Architecture multi-couches

Le code obfusqué utilise une structure en "poupées russes" :

```
┌─────────────────────────────────┐
│ Couche 0 (fichier original)     │
│  exec((lambda: b'XYZ...')())    │
│         │                       │
│         └──────┐                │
└────────────────│────────────────┘
                 │ Déobfuscation
                 ▼
┌─────────────────────────────────┐
│ Couche 1                        │
│  exec((lambda: b'ABC...')())    │
│         │                       │
│         └──────┐                │
└────────────────│────────────────┘
                 │ Déobfuscation
                 ▼
┌─────────────────────────────────┐
│ Couche 2                        │
│  exec((lambda: b'DEF...')())    │
│         │                       │
│         └──────┐                │
└────────────────│────────────────┘
                 │ Déobfuscation
                 ▼
┌─────────────────────────────────┐
│ Code source final (déobfusqué)  │
│  print("Hello World!")          │
└─────────────────────────────────┘
```

**Nombre de couches** : Généralement entre 3 et 10 couches selon la complexité du code source.

## Fonctionnement du déobfuscateur

Le script `deobfuscator.py` inverse le processus d'obfuscation :

### 1. Extraction du payload

```python
def extract_payload(surface_code: bytes, layer_num: int = 0) -> bytes
```

- Parse le code Python avec `ast` (Abstract Syntax Tree)
- Identifie les constantes de type `bytes` dans l'AST
- Extrait le payload obfusqué (la bytes string)
- Sauvegarde chaque couche dans `layer_XXX.py` pour débogage

### 2. Déobfuscation d'une couche

```python
def deobfuscate_layer(payload: bytes) -> bytes
```

Pour chaque couche, applique les transformations inverses :

1. **Inversion** : Inverse la chaîne d'octets
   ```python
   reversed_payload = payload[::-1]
   ```

2. **Décodage Base64** : Décode depuis Base64
   ```python
   decoded = base64.b64decode(reversed_payload)
   ```

3. **Décompression** : Décompresse avec zlib
   ```python
   decompressed = zlib.decompress(decoded)
   ```

### 3. Processus itératif

Le script applique ces étapes de manière récursive :

```
Fichier obfusqué → Extract → Deobfuscate → Extract → Deobfuscate → ... → Code source
```

Le processus s'arrête quand :
- Aucun payload bytes n'est trouvé (= code source final atteint)
- Une erreur de parsing survient
- Le maximum de couches (100) est atteint

## Installation

### Prérequis

- Python 3.7+
- Modules standards (inclus dans Python) :
  - `ast`
  - `base64`
  - `zlib`
  - `pathlib`

### Cloner le repository

```bash
git clone https://github.com/Xor290/free-coding-tool-deobfuscator.git
cd free-coding-tool-deobfuscator
```

Aucune installation de dépendances supplémentaires n'est nécessaire.

## Utilisation

### Étape 1 : Préparer le fichier obfusqué

Placez votre fichier Python obfusqué dans le répertoire courant et renommez-le `obf_payload.py`.

```bash
cp /chemin/vers/fichier_obfusque.py obf_payload.py
```

### Étape 2 : Lancer le déobfuscateur

```bash
python3 deobfuscator.py
```

### Étape 3 : Récupérer le résultat

Le script génère plusieurs fichiers :

- `layer_000.py`, `layer_001.py`, ... : Chaque couche d'obfuscation décodée
- `deobfuscated_payload.py` : Le code source final déobfusqué

## Exemple détaillé

### Anatomie d'un code obfusqué

Prenons un exemple réel d'obfuscation par FreeCodingTools :

#### Code original (déobfusqué)

```python
print("Hello, World!")
```

#### Code obfusqué

```python
_ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]));
exec((_)(b'=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'))
```

### Décortiquons ce code

#### 1. La fonction lambda

```python
_ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]))
```

Cette ligne définit une fonction anonyme qui effectue les 3 opérations de déobfuscation :

- `__[::-1]` → **Inverse** la chaîne de bytes
- `__import__('base64').b64decode(...)` → **Décode** depuis Base64
- `__import__('zlib').decompress(...)` → **Décompresse** avec zlib

**Pourquoi `__import__()` ?** : Utiliser `__import__()` au lieu de `import` rend le code plus compact et évite d'avoir des statements `import` visibles.

#### 2. Le payload obfusqué

```python
b'=c79ZEzf77///Ifl4GcvNc+4ZuZMrAdSoE14fSsxL9/XK4Foal...'
```

C'est une longue chaîne de bytes qui contient le code compressé et encodé. Cette chaîne fait **1337 bytes** pour un code original de seulement **22 bytes** !

#### 3. L'exécution

```python
exec((_)(b'...'))
```

- `(_)(b'...')` → Appelle la fonction lambda avec le payload
- `exec(...)` → Exécute le code Python résultant

### Processus de transformation

Voici exactement ce qui se passe lors de la déobfuscation :

```
┌──────────────────────────────────────────────────────────┐
│ Payload obfusqué                                         │
│ b'=c79ZEzf77///Ifl4GcvNc+4ZuZMrAdSoE14f...'              │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ Étape 1: Inversion [::-1]
                     ▼
┌──────────────────────────────────────────────────────────┐
│ Payload inversé                                          │
│ b'...f41EeSoE4ZMruSdArM5Zuv4+cNvcGl4fI///77fzE97c='      │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ Étape 2: Décodage Base64
                     ▼
┌──────────────────────────────────────────────────────────┐
│ Données binaires compressées                             │
│ x\x9c\xed\x9c\xebS\x1bG\x16\xc7\xff\x8b...               │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ Étape 3: Décompression zlib
                     ▼
┌──────────────────────────────────────────────────────────┐
│ Code Python déobfusqué                                   │
│ print("Hello, World!")                                   │
└──────────────────────────────────────────────────────────┘
```

### Test de déobfuscation

Créons un fichier test :

```bash
# Créer le fichier obfusqué
cat > obf_payload.py << 'EOF'
_ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]));
exec((_)(b'=c79ZEzf77///Ifl4GcvNc+4ZuZMrAdSoE14fSsxL9/XK4Foal7LPrwU6IjgFAWV9dP4AigLWdAyRp3FrYN7k8KN4ixqm15XJq/RuyrEmDYGKkDVW7KAZpK6uDiaah5zRCk8t80AAP+29hr6gx7Q1XF1Jf2zhIEmJU5IMx+M/sZb2IjUtSNDqfUd7q20qd/EV/PgQQvUgJ2F+UckWOXqMgR3Gr6AqzfWcghQVTreIUYqsVyMiLfE9ziiw7sTPLN+Fz+Qmcw3THxeuCwYsETmyamS6WWBftIG2TD2ZJboucxlJQw3PY6Xb5e6LyyBoUpWAi/hvK55mrkFwRhbZisNo23ttHtN009mLLkdWlWyMVImyp90s6JD/1sKgUgc3/oKRZemEKDxj31vZp3nVtFvH07yWUQDgu5fb+kReAmhfehZEhR9tBM4yYn/mIcXYt4X57GymyQ9WfkijTu+4vbsJEVw3CtPHMdm9nKWaLgYsMUdjXitPX1MkMyOyEg7UqztzaxLOwh04fOmA63n38rcZJ2dFyarS+RHVB7erJvCSpJnqNsWlp5s5NtCc2vYDTrr44qAtXZq71RcKCwPtD63kq43bE1QTB5vUuQS8XiQ4I5MZ6bf9xGx1CCVo35F00shewGFgVQ7vabt1Ay1ogGqh/0+vFhAx9Fdc4b5pHLoOlJyqdWZAqdYU5IGazeDH/MDFMxgjzQqo1IPaFplxk5wItHHCx7a22wvErb7aybqSAB1e6ZgIlTKV7YO6aori3fmw0D9KQ0ZKfqCxJcRDZYHMcxbsJVhSpA4AQtipOxia7ntjy6ZurAC7/1uqHHdcQWiJSTb2EP7It2oWyHFRg0KTQ2xycWJ4n3FKT519/2InSL8JHQVfrvllkRXD7IJkjKu7hzolD6g/nYrNgC90gCI/QQEImLXOaD0xPd+9rMDmms93Ptmj3iRwAaKhjW+eQiPsOuMimb2WXy+lLmbr6b3L0FFDG/ncTXBIv+7T8+LzzR3TlS+EcrD+6BxFgVDGsfRpjthqakhb8I3YLZ++8pVEV68sLytaKZS9OOFbyeP2hqH0pPxNwHHEwdDuUJxG8VvwIWkxz+2XYRdmLFkQs9aiL1Eu4y08q1Wdx3zHwUg3YZj6P4WNDB0khLkYq1M+zWg+cszKkYw2CuefEedWP/111kk/npshfbehSGVLEMOFsVUDKnueUYJ6qJNbv6FlSYarp+ep96xt/N1XWvPo6imAhMEx3DOvb5i76HYcxUr8IMQVyixcs5r6GvUiMVcob6NxxDdyv4YM6k0opjfS6kInquFUmRF/cMqkudy88EKSZjA0KkEa8zyG/8BwNY0KJevB4nnbL4H5uNxYfQbGemHd0enOqFjCIkJZMfAfvGdYEwSG2xlXH5OXHmf7VTqOS86S4SxtVhxtRywTZ9OBdF2iOCyR7SWYZ39NW0muq51vP6EacfJTI5ZUiChvkf3Ut1HE80XV3565ZR3y1O+oF+kpmjgZ96zWxSEOLpeAtp87zOS1eTv2xLe/XiMbPmiYtDK7jgF+17L01vBFLaY/0ZO5FArTEjraL/hclv/zaX/+fMaAVgYV7DPaQyedirsQ/xa4eaUjJp6NW4lxMMBv1yJEEeGVyqtQxXciK+BuApwkpbu+rLKSjC/Nm83VefWzf2vpGpS+MZu4twOWc1K7DJad0FFuFe4Oil4lQKqLAKbd4CPG61DmZMq82snutZo1AGXhY+arhb+veVK/1MOWho2HUbOtoiYF7AhztcX+gmAvPE/pB0siHSzZWpwduykKHKY/G33WCOSbWAFvaSc57Wb7Pqbqr6crxLYZR/alU5uU/kmm0O3MkPMfkSFI3J4kJzKYy1BXnlntZLfO0Z4yIa5Zi9iWpGWeTt2zg9VBWfTj5oaPWu/t4qbdpdxnCMZeUdMMdnRHCbxXXb5jb12OQKflOsGS/PM6ebxWEPpQ2j8jKCCPhrBHV+1dbseiKc5P2Q4ANB7U+7KRVFannYHMMsYsaAIWMwdvItYUjjia0UtN6hXzD2CzHdvDXaK5Vq0OMe7/WhqPLe7DLKZNtHl+Yvi4523Ma6OJwsmJEFRA8fUWXLVBOpdZHks/cYGFfmok51uA9Na3h2YVEqBIc+qBOAKmvKGhJaWZBHyW7ImE2BqfOd4l0nptKF64doabCHf8lcYfcaIWU89hB0G1kt9jpUeWXpU5Wpw+MuQlAEkSksAxMV7s4eHQFvRzT8oBIVIIyAjFrmEkCBQE6B39396/9e+/T2//+d++/38pI/kSSVqD823Wd3dLQqzuDuHDKO4Dcx/Tf5QCoQhyWElNwJe'))
EOF

# Lancer le déobfuscateur
python3 deobfuscator.py
```

**Résultat** :

```bash
============================================================
Final payload reached at layer 1
============================================================

Success! Deobfuscated payload saved to: deobfuscated_payload.py
Final size: 22 bytes

============================================================
Full deobfuscated content:
============================================================

print("Hello, World!")
```

**Utilisez cet outil de manière responsable et éthique.**

## 🔗 Liens utiles

- [FreeCodingTools](https://freecodingtools.org/) - Outil d'obfuscation en ligne
- [Documentation Python AST](https://docs.python.org/3/library/ast.html)
- [Documentation zlib](https://docs.python.org/3/library/zlib.html)
- [Documentation base64](https://docs.python.org/3/library/base64.html)
