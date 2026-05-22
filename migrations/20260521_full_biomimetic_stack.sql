BEGIN;

-- Shiva-Octopus + Cephalopod base tables
CREATE TABLE IF NOT EXISTS limbs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES try_runs(id) ON DELETE CASCADE,
    parent_limb_id UUID REFERENCES limbs(id),
    coalition_json JSONB NOT NULL,
    status TEXT CHECK (status IN ('active', 'decomposed', 'completed', 'failed')),
    segmentation_level INT DEFAULT 1,
    suckerotopy_map JSONB,
    inter_limb_ring_enabled BOOLEAN DEFAULT FALSE,
    cephalopod_recoding_active BOOLEAN DEFAULT FALSE,
    last_za_scan_at TIMESTAMPTZ,
    srd_self_edit_delta JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    decomposed_at TIMESTAMPTZ,
    hmac_signature TEXT NOT NULL
);

-- (full migration content as previously provided)
COMMIT;