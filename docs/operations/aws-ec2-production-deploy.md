# GastroLedger Production Deploy On AWS EC2

Esta guia describe el flujo productivo actual: cuando un release PR de
`develop` se mergea a `main`, GitHub Actions valida el monorepo y despliega en un
servidor EC2 por SSH. En el EC2 se actualiza el repositorio, se construyen los
contenedores, se ejecutan migrations, se ejecuta la seed idempotente y se
levantan `web`, `api`, `worker` y PostgreSQL con Docker Compose.

## Arquitectura De Despliegue

- Rama productiva: `main`.
- Evento: `push` a `main`, normalmente generado por merge de `develop` a `main`.
- Workflow: `.github/workflows/production.yml`.
- Host: una instancia EC2 Ubuntu Server 26.04 LTS x86_64 con Docker Engine y Docker Compose plugin.
- App dir recomendado: `/opt/gastroledger`.
- Runtime: `infra/compose/compose.yaml` + `infra/compose/compose.production-like.yaml`.
- Base de datos: PostgreSQL en Compose con volumen persistente `postgres-data`.
- Acceso publico recomendado: Nginx o ALB hacia `127.0.0.1:3000`.

Importante: Compose publica `web`, `api` y `postgres` solo en `127.0.0.1`.
No abras PostgreSQL ni la API directamente a Internet.

## 1. Preparar EC2

Recomendado para empezar desde cero:

- AMI: Ubuntu Server 26.04 LTS (HVM), EBS General Purpose SSD.
- Tipo de instancia: `t3.small` x86_64, 2 vCPU y 2 GiB RAM.
- Volumen EBS: minimo 30 GiB `gp3` para Docker images, PostgreSQL y backups.
- Usuario SSH default: `ubuntu`.
- Security Group:
  - `22/tcp` solo desde IPs administrativas o desde el rango de salida que uses para CI.
  - `80/tcp` y `443/tcp` publicos si Nginx termina HTTP/HTTPS.
  - No exponer `5432`, `8000` ni `3000`.

Instala dependencias base:

```bash
cat /etc/os-release
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ca-certificates \
  curl \
  docker.io \
  git \
  nginx \
  python3
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker-buildx docker-compose-v2 || true
sudo systemctl enable --now docker
sudo systemctl enable --now nginx
sudo usermod -aG docker ubuntu

ARCH="$(uname -m)"
case "$ARCH" in
  x86_64)
    COMPOSE_ARCH="x86_64"
    BUILDX_ARCH="amd64"
    ;;
  aarch64)
    COMPOSE_ARCH="aarch64"
    BUILDX_ARCH="arm64"
    ;;
  *) echo "Unsupported architecture for Docker plugins: $ARCH" >&2; exit 1 ;;
esac
sudo mkdir -p /usr/local/lib/docker/cli-plugins /usr/libexec/docker/cli-plugins /usr/lib/docker/cli-plugins

download_plugin() {
  url="$1"
  target="$2"
  if command -v curl >/dev/null 2>&1; then
    sudo curl -fsSL "$url" -o "$target"
  else
    tmp_file="$(mktemp)"
    python3 -c 'import sys, urllib.request; urllib.request.urlretrieve(sys.argv[1], sys.argv[2])' "$url" "$tmp_file"
    sudo mv "$tmp_file" "$target"
  fi
}

COMPOSE_URL="https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$COMPOSE_ARCH"
download_plugin "$COMPOSE_URL" /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

BUILDX_VERSION="v0.17.1"
BUILDX_URL="https://github.com/docker/buildx/releases/download/$BUILDX_VERSION/buildx-$BUILDX_VERSION.linux-$BUILDX_ARCH"
download_plugin "$BUILDX_URL" /usr/local/lib/docker/cli-plugins/docker-buildx
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-buildx
sudo install -m 0755 /usr/local/lib/docker/cli-plugins/docker-buildx /usr/libexec/docker/cli-plugins/docker-buildx
sudo install -m 0755 /usr/local/lib/docker/cli-plugins/docker-buildx /usr/lib/docker/cli-plugins/docker-buildx
```

El bloque de descarga manual de Compose y Buildx es intencional: en algunas AMI
los paquetes `docker-compose-v2` o `docker-buildx` pueden no existir o venir
viejos. Cierra y vuelve a entrar por SSH para tomar el grupo `docker`, luego
valida:

```bash
docker version
docker compose version
docker buildx version
git --version
nginx -v
```

Si `docker compose version` o `docker buildx version` fallan, valida con
`sudo docker compose version` y `sudo docker buildx version`.
La pipeline usa `sudo docker compose`, asi que no depende de que el grupo
`docker` ya este aplicado en la sesion de GitHub Actions.

## 2. Preparar El Directorio De La App

En EC2:

```bash
sudo mkdir -p /opt/gastroledger
sudo chown "$USER":"$USER" /opt/gastroledger
mkdir -p "$HOME/gastroledger-backups"
```

El workflow tambien crea y ajusta permisos de `/opt/gastroledger`, pero conviene
dejarlo listo antes del primer deploy.
El usuario configurado en `AWS_EC2_USER` debe poder ejecutar `sudo` para crear y
tomar ownership de ese directorio.

## 3. SSH Desde GitHub Actions Hacia EC2

Genera una llave dedicada para que GitHub Actions entre al EC2:

```bash
ssh-keygen -t ed25519 -C "github-actions-gastroledger-production" -f ./gastroledger_ec2_actions
```

En EC2, agrega la llave publica:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat gastroledger_ec2_actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

En GitHub, crea estos secrets del repositorio:

- `AWS_EC2_HOST`: DNS publico o IP publica del EC2.
- `AWS_EC2_USER`: usuario SSH, para Ubuntu normalmente `ubuntu`.
- `AWS_EC2_SSH_PRIVATE_KEY`: contenido completo de `gastroledger_ec2_actions`.
- `AWS_EC2_PORT`: opcional; si queda vacio el workflow usa `22`.

## 4. Acceso Del EC2 A GitHub

El workflow entra al EC2 y ejecuta `git clone` o `git fetch`.

Como `https://github.com/Ainsiel/GastroLedger` es publico, no necesitas deploy
key para que el EC2 lea el repositorio. La pipeline usa por defecto:

```text
https://github.com/Ainsiel/GastroLedger.git
```

Solo si cambias el repositorio a privado, configura una deploy key de solo
lectura en GitHub.

En EC2:

```bash
ssh-keygen -t ed25519 -C "gastroledger-ec2-deploy" -f ~/.ssh/gastroledger_github_deploy
cat ~/.ssh/gastroledger_github_deploy.pub
```

Agrega esa publica en GitHub: repository settings, Deploy keys, Add deploy key,
Read-only.

Configura SSH para GitHub:

```bash
cat > ~/.ssh/config <<'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/gastroledger_github_deploy
  IdentitiesOnly yes
EOF
chmod 600 ~/.ssh/config
ssh-keyscan github.com >> ~/.ssh/known_hosts
ssh -T git@github.com || true
```

Si quieres usar una URL distinta a
`https://github.com/Ainsiel/GastroLedger.git`, crea la variable de repositorio
`EC2_REPOSITORY_URL`.

## 5. Variables Y Secretos De Produccion

El workflow sube un archivo `infra/compose/.env.production` al EC2 usando el
secret multilinea `EC2_PRODUCTION_ENV`.

Ejemplo de contenido:

```dotenv
POSTGRES_DB=gastroledger
POSTGRES_USER=gastroledger
POSTGRES_PASSWORD=<migration-owner-password>
POSTGRES_RUNTIME_USER=gastroledger_runtime
POSTGRES_RUNTIME_PASSWORD=<runtime-password>
POSTGRES_PORT=5432
API_PORT=8000
WEB_PORT=3000

SEED_TENANT_SLUG=gastroledger-prod
SEED_TENANT_NAME=GastroLedger Production
SEED_ADMIN_EMAIL=admin@example.com
SEED_ADMIN_PASSWORD_HASH='<scrypt-hash>'
```

Notas:

- `POSTGRES_PASSWORD` y `POSTGRES_RUNTIME_PASSWORD` deben ser distintos.
- `POSTGRES_USER` es el owner/migration user usado por `migrate` y `seed`.
- No uses `infra/compose/.env.example` en produccion.
- `SEED_ADMIN_PASSWORD_HASH` guarda solo el hash, no la password plana.

Genera un hash compatible con el hasher de la API:

```bash
python3 - <<'PY'
import base64
import getpass
import hashlib
import secrets

password = getpass.getpass("Seed admin password: ")
salt = secrets.token_bytes(16)
digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
print(
    "scrypt$"
    + base64.urlsafe_b64encode(salt).decode("ascii")
    + "$"
    + base64.urlsafe_b64encode(digest).decode("ascii")
)
PY
```

Guarda el resultado como `SEED_ADMIN_PASSWORD_HASH` dentro de `EC2_PRODUCTION_ENV`.
El admin seed queda en `SEED_ADMIN_EMAIL` y puede iniciar sesion con la password
que usaste para generar el hash.

Opcionalmente define GitHub repository variables:

- `EC2_APP_DIR`: default `/opt/gastroledger`.
- `EC2_REPOSITORY_URL`: default `https://github.com/Ainsiel/GastroLedger.git`.

## 6. Seed Incluida

La seed vive en:

```text
infra/seeds/0001-admin-tenant-demo-data.sql
```

Se ejecuta despues de migrations mediante el servicio Compose `seed`.

Incluye:

- Tenant administrador activo.
- Usuario tenant admin.
- Sucursales, bodegas y roles de plataforma.
- Invitacion pendiente para user access.
- Unidades, conversiones, ingredientes activos y un ingrediente archivado.
- Proveedores y ofertas vigentes.
- Receta de sub-preparacion, menu item, version futura y precios por sucursal.
- Recepcion de proveedor, lotes, ledger de inventario y saldos.
- Batch de produccion posteado.
- Transferencia completada entre bodegas.
- Mermas en estados `posted`, `corrected`, `rejected` y `pending_approval`.
- Jobs, outbox, proyecciones de costo, alertas de vencimiento y notificaciones.
- Eventos de auditoria para control/insights.

La seed usa IDs fijos y `ON CONFLICT`, por lo que puede ejecutarse repetidamente.
No debe usarse para borrar o resetear datos reales.

## 7. Primer Deploy Manual Opcional

Puedes validar el EC2 antes de activar el workflow:

```bash
cd /opt/gastroledger
git clone --branch main https://github.com/Ainsiel/GastroLedger.git .
cat > infra/compose/.env.production <<'EOF'
# pega aqui el mismo contenido de EC2_PRODUCTION_ENV
EOF

COMPOSE="sudo docker compose --env-file infra/compose/.env.production -f infra/compose/compose.yaml -f infra/compose/compose.production-like.yaml"
$COMPOSE build web api worker
$COMPOSE up --detach --wait postgres
$COMPOSE run --rm migrate
$COMPOSE run --rm seed
$COMPOSE up --detach --wait web api worker
$COMPOSE ps
```

No uses `down --volumes` en produccion salvo que quieras destruir la base de
datos.

## 8. Nginx Para Exponer El Front

Ejemplo minimo:

```bash
sudo tee /etc/nginx/conf.d/gastroledger.conf >/dev/null <<'EOF'
server {
  listen 80;
  server_name app.example.com;

  location / {
    proxy_pass http://127.0.0.1:3000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
EOF
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
```

Para HTTPS usa Certbot o termina TLS en un ALB. Mantén `WEB_PORT=3000` local y
proxy hacia `127.0.0.1:3000`.

## 9. Flujo Normal De Produccion

1. Crear PR desde `develop` hacia `main`.
2. Pasar los checks de release.
3. Mergear el PR.
4. El `push` resultante a `main` dispara `production.yml`.
5. El workflow corre `artifact-smoke`.
6. Si el smoke pasa, `deploy-ec2`:
   - entra por SSH al EC2;
   - actualiza el repo a `origin/main`;
   - sube `.env.production`;
   - construye contenedores;
   - genera backup predeploy con `pg_dump`;
   - ejecuta migrations;
   - ejecuta seed;
   - levanta `web`, `api` y `worker`.

## 10. Verificacion

En EC2:

```bash
cd /opt/gastroledger
COMPOSE="sudo docker compose --env-file infra/compose/.env.production -f infra/compose/compose.yaml -f infra/compose/compose.production-like.yaml"
$COMPOSE ps
$COMPOSE logs --tail=100 web api worker
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS http://127.0.0.1:8000/health
```

Verifica login con:

- Email: valor de `SEED_ADMIN_EMAIL`.
- Password: la password usada para generar `SEED_ADMIN_PASSWORD_HASH`.

## 11. Backups Y Rollback

El workflow guarda un backup logico antes de migrations en:

```text
$HOME/gastroledger-backups/predeploy-YYYYMMDDHHMMSS.sql
```

Rollback de aplicacion:

- Revertir el merge commit en `main`, o mergear un fix hacia `main`.
- Dejar que `production.yml` despliegue el nuevo estado.

Rollback de base de datos:

- Las migrations deben ser compatibles hacia atras durante la ventana de rollback.
- Restaurar un `pg_dump` es una operacion de emergencia con downtime y debe
  hacerse solo despues de detener runtime y confirmar impacto de perdida de datos.

Comandos utiles:

```bash
$COMPOSE stop web api worker
ls -lh "$HOME/gastroledger-backups"
```

## 12. Checklist

- EC2 tiene Docker, Compose, Git y Nginx.
- Security Group no expone PostgreSQL.
- EC2 puede hacer `git fetch` del repositorio.
- GitHub Actions puede entrar por SSH al EC2.
- `EC2_PRODUCTION_ENV` contiene secretos reales y hash scrypt del admin.
- Primer `migrate` y `seed` ejecutan sin errores.
- Nginx proxy pasa a `127.0.0.1:3000`.
- Release PR siempre nace de `develop` hacia `main`.
