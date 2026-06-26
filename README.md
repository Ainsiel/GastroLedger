# GastroLedger

GastroLedger es un SaaS operacional multi-tenant para holdings, cadenas y
franquicias gastronómicas. Busca convertir recetas, compras, producción y ventas
operacionales en un ledger de inventario trazable para explicar consumo, merma,
costo y rentabilidad por sucursal.

El repositorio contiene actualmente el scaffold ejecutable, los límites
arquitectónicos y la infraestructura de entrega. Todavía no implementa casos de uso
funcionales.

## Propuesta De Valor

Las capacidades objetivo aprobadas son:

- administrar tenants, usuarios locales, roles, sucursales y bodegas;
- modelar unidades, ingredientes, recetas versionadas, rendimientos y costos;
- gestionar proveedores, sugerencias de compra, órdenes, recepciones y devoluciones
  operacionales;
- mantener inventario por lotes mediante movimientos inmutables;
- registrar producción, transferencias, mermas, vencimientos y conteos físicos;
- importar o simular ventas para explicar consumo operacional;
- comparar costo teórico, movimientos reales y rentabilidad.

GastroLedger no es un POS, procesador de pagos, sistema contable, facturador,
sistema de nómina ni plataforma de suscripciones pagadas. V1 no consume APIs ni
servicios externos.

## Stack Confirmado

| Área | Tecnología |
|---|---|
| Frontend | Next.js `16.2.9` App Router, React `19.2.7`, TypeScript `6.0.3`, shadcn/ui, Tailwind CSS `4.3.1` |
| Backend | Python `3.13`, FastAPI `0.137.0`, SQLAlchemy `2.0.50`, psycopg `3.3.4`, Uvicorn `0.49.0` |
| Worker | Entry point Python separado que reutiliza módulos de `apps/api` |
| Datos | PostgreSQL `17-alpine` |
| JavaScript | Node.js `22.13.1`, npm `10.9.2`, workspaces npm |
| Pruebas | Vitest `4.1.8`, pytest `9.1.0`, Ruff `0.15.17` |
| Entrega | Docker Compose y GitHub Actions |

## Arquitectura

GastroLedger usa un monolito modular:

```text
Browser -> Next.js -> FastAPI API -> módulos públicos -> PostgreSQL
                              Worker -> jobs/outbox PostgreSQL
```

Los seis bounded contexts son Platform & Organization, Menu Engineering,
Procurement, Inventory & Production, Store Operations y Control & Insights.
FastAPI conserva la autoridad de negocio y autorización; Next.js conserva
presentación y estado de interacción. Los contextos se comunican únicamente mediante
contratos públicos o eventos outbox.

La dirección aprobada contempla multi-tenancy en esquema compartido con `tenant_id`
y RLS, ledger de inventario inmutable, recetas versionadas, jobs PostgreSQL y outbox
transaccional. Esas reglas funcionales y tablas todavía no están implementadas.

## Estructura Del Monorepo

```text
apps/
  web/                 Next.js App Router y features frontend
  api/                 FastAPI, contratos y módulos backend
  worker/              entry point técnico separado
packages/
  api-contract/        contratos de transporte sin lógica de dominio
tests/
  architecture/        reglas de dependencias y límites públicos
  infrastructure/      contratos Compose y GitHub Actions
  integration/         harness técnico con PostgreSQL real
  e2e/                 smoke técnico crítico
infra/
  compose/             Compose base y overlays
  containers/          Dockerfiles
  migrations/          cadena de migración técnica
docs/
  product/             propósito y alcance
  sdd/                 requisitos, casos de uso y trazabilidad
  architecture/        arquitectura, ADRs y planes operacionales
```

## Requisitos Locales

- Node.js `>=22 <23`.
- npm `>=10 <11`.
- Docker Engine con el plugin Docker Compose.
- Puertos `3000`, `8000` y `5432` disponibles para los entornos normales.
- Puertos `53000` y `58000` disponibles para el runtime de integración.

El entorno local confirmado usa Docker Engine `28.1.1` y Docker Compose
`2.35.1-desktop.1`. Python se ejecuta dentro de contenedores; no se requiere una
instalación Python en el host.

`infra/compose/.env.example` contiene únicamente valores locales no secretos. No
agregues secretos reales al repositorio.

## Instalación

Desde la raíz del repositorio:

```powershell
npm run bootstrap
```

El comando instala las dependencias npm bloqueadas y construye los contenedores
Python de desarrollo.

## Entornos Locales

Los comandos Compose de inicio esperan hasta que los servicios estén saludables y
dejan los contenedores ejecutándose.

### Develop

```powershell
docker compose --env-file infra/compose/.env.example -f infra/compose/compose.yaml -f infra/compose/compose.develop.yaml up --detach --build --wait
```

Servicios: web `http://127.0.0.1:3000`, API
`http://127.0.0.1:8000/health` y PostgreSQL `127.0.0.1:5432`.

Documentacion interactiva local del backend:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Swagger usa assets servidos por el propio contenedor API y no necesita CDN ni
conexion a Internet.

Para trabajar con los logs adjuntos y hot reload, el script interactivo confirmado
es `npm run dev`; permanece activo hasta interrumpirlo.

Detener:

```powershell
docker compose --env-file infra/compose/.env.example -f infra/compose/compose.yaml -f infra/compose/compose.develop.yaml down
```

### QA

```powershell
docker compose --env-file infra/compose/.env.example -f infra/compose/compose.yaml -f infra/compose/compose.qa.yaml up --detach --build --wait
```

Detener:

```powershell
docker compose --env-file infra/compose/.env.example -f infra/compose/compose.yaml -f infra/compose/compose.qa.yaml down
```

### Production-Like

Este entorno local valida el contrato de ejecución; no despliega a producción.

```powershell
docker compose --env-file infra/compose/.env.example -f infra/compose/compose.yaml -f infra/compose/compose.production-like.yaml up --detach --build --wait
```

Detener:

```powershell
docker compose --env-file infra/compose/.env.example -f infra/compose/compose.yaml -f infra/compose/compose.production-like.yaml down
```

### Seed

La seed idempotente crea el tenant administrador y datos de demostracion para
las features implementadas. Se ejecuta automaticamente al levantar `api` o
`worker`, y tambien puede correrse manualmente:

```powershell
npm run seed:database
npm run seed:database:qa
npm run seed:database:production-like
```

En local, `.env.example` usa `admin@gastroledger.local` con un hash scrypt de
desarrollo. En produccion configura `SEED_ADMIN_PASSWORD_HASH` con un hash propio.

## Validación Y Pruebas

Validaciones principales:

```powershell
npm run lint
npm test
npm run test:migrations
npm run build
```

`npm test` ejecuta pruebas unitarias, de arquitectura, infraestructura e integración
con PostgreSQL aislado. La migración actual verifica solamente la infraestructura y
no crea tablas funcionales.

Validar las combinaciones Compose soportadas:

```powershell
npm run compose:config
npm run compose:config:qa
npm run compose:config:production-like
npm run compose:config:integration
```

Ejecutar el smoke técnico E2E aislado:

```powershell
docker compose -p gastroledger-integration --env-file infra/compose/.env.example -f infra/compose/compose.yaml -f infra/compose/compose.integration.yaml up --detach --wait --build web api worker
npm run test:e2e:critical
docker compose -p gastroledger-integration --env-file infra/compose/.env.example -f infra/compose/compose.yaml -f infra/compose/compose.integration.yaml down --volumes --remove-orphans
```

El smoke usa web `http://127.0.0.1:53000` y API
`http://127.0.0.1:58000/health`.

## Ramas Y Contribución

- `main` representa producción.
- `develop` es la rama de integración.
- Cada `feature/<work-order-id>-<slug>` nace desde `develop` y apunta a `develop`.
- Los release PR van desde `develop` hacia `main`.
- No se permiten pushes directos a `develop` ni `main`.
- Los feature PR usan squash merge; los release PR usan merge commit.

## Despliegue AWS EC2

La guia completa de configuracion de EC2, SSH, GitHub secrets, Docker Compose,
migrations, seed y pipeline productiva esta en
`docs/operations/aws-ec2-production-deploy.md`.

Antes de implementar comportamiento:

1. Trabaja desde un work order vertical aprobado.
2. Lee los requisitos y contratos arquitectónicos relacionados.
3. Mantén los límites públicos de módulos y frontend features.
4. Ejecuta lint, pruebas y build antes de solicitar verificación.
5. No agregues APIs externas ni comportamiento monetario real sin ampliar el SDD y
   aprobar un nuevo ADR.

## Documentación

- [Índice SDD](docs/sdd/README.md)
- [Índice de arquitectura](docs/architecture/README.md)
- [Contexto compacto para agentes](CONTEXT.md)
