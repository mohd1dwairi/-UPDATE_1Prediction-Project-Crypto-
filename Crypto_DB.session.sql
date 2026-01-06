INSERT INTO model_registry (
    id,
    name,
    version,
    path,
    params,
    metrics,
    is_active,
    registered_at
  )
VALUES (
    id:integer,
    'name:character varying',
    'version:character varying',
    'path:character varying',
    'params:json',
    'metrics:json',
    is_active:boolean,
    'registered_at:timestamp with time zone'
  );
  -- 