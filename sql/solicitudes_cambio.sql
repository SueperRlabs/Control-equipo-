-- ═══════════════════════════════════════════════════════════════
--  Módulo de solicitud de cambio de turno (swaps)
--  Ejecutar una vez en Supabase → SQL Editor.
--  Es idempotente: se puede volver a correr sin romper nada.
-- ═══════════════════════════════════════════════════════════════

-- 1. Estado de la solicitud
do $$
begin
  if not exists (select 1 from pg_type where typname = 'estado_solicitud') then
    create type estado_solicitud as enum ('pendiente', 'aprobado', 'rechazado');
  end if;
end $$;

-- 2. Turno liberado por un cambio aprobado sin reemplazo propuesto.
--    Sigue apuntando a quien lo tenía, pero no se le cuenta como trabajado:
--    el supervisor lo reasigna a mano desde Horarios.
alter table turnos add column if not exists vacante boolean not null default false;

-- 3. Tabla de solicitudes
create table if not exists solicitudes_cambio (
  id                      uuid primary key default gen_random_uuid(),
  turno_id                uuid not null references turnos(id)     on delete cascade,
  empleado_solicitante_id uuid not null references empleados(id)  on delete cascade,
  empleado_reemplazo_id   uuid          references empleados(id)  on delete set null,
  motivo                  text,
  estado                  estado_solicitud not null default 'pendiente',
  fecha_solicitud         timestamptz not null default now(),
  fecha_resolucion        timestamptz
);

create index if not exists solicitudes_cambio_turno_idx
  on solicitudes_cambio (turno_id);
create index if not exists solicitudes_cambio_solicitante_idx
  on solicitudes_cambio (empleado_solicitante_id, fecha_solicitud desc);

-- Una sola solicitud pendiente por turno
create unique index if not exists solicitudes_cambio_pendiente_uniq
  on solicitudes_cambio (turno_id) where estado = 'pendiente';

-- 4. Permisos: mismo criterio que el resto de las tablas de la app,
--    que se consulta con la clave anon desde el navegador.
alter table solicitudes_cambio enable row level security;

do $$
begin
  if not exists (
    select 1 from pg_policies
    where tablename = 'solicitudes_cambio' and policyname = 'solicitudes_cambio_todo'
  ) then
    create policy solicitudes_cambio_todo on solicitudes_cambio
      for all to anon, authenticated using (true) with check (true);
  end if;
end $$;
