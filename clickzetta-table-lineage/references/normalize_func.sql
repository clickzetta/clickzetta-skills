CREATE OR REPLACE FUNCTION public.__normalize_table(t STRING) 
RETURNS STRING
RETURN case when contains(t, '__delta__') or contains(t, '__incr__') then NULL -- remove delta/incr intermediate tables
    when contains(t, '__DIRECTORY__EXTERNAL__') then NULL -- volume directory listing
    when contains(t, '_$kafka$_') then regexp_replace(t, r'([\w\.\-]+)_\$kafka\$_\w+$', r'KAFKA.$1') -- kafka pipe source
    when t rlike r'_t_\w{32}$' then regexp_replace(t, r'([\w\.]+)_t_\w{32}$', r'VOLUME.$1') -- volume source
    else t -- keep as is
    end
;

CREATE OR REPLACE FUNCTION public.__normalize_objects(ts ARRAY<STRING>) 
RETURNS ARRAY<STRING>
RETURN TRANSFORM(FILTER(ts, x -> x is not null and x != ''), x -> public.__normalize_table(x))
;
